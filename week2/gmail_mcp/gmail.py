"""Thin Gmail REST client: HTTP -> shaped models, HTTP errors -> GmailError.

Raw Gmail payloads are large (nested MIME parts, dozens of headers). Everything
returned from here is a small pydantic model with only the fields an agent needs.
"""

from __future__ import annotations

import base64
import html
import re
from email.message import EmailMessage
from email.utils import getaddresses

import httpx
from pydantic import BaseModel, Field

from . import auth
from .errors import AUTH_HINT, GmailError

API = "https://gmail.googleapis.com/gmail/v1/users/me"
MAX_BODY_CHARS = 2000


# ---------- shaped output models ----------


class Address(BaseModel):
    name: str = Field(description="Display name, may be empty.")
    email: str


class EmailSummary(BaseModel):
    message_id: str = Field(description="Gmail message ID. Pass to get_email_recipients or send_email.")
    thread_id: str
    date: str
    sender: Address
    subject: str
    snippet: str
    body: str = Field(description=f"Plain-text body, truncated to {MAX_BODY_CHARS} chars.")
    body_truncated: bool
    labels: list[str]


class EmailRecipients(BaseModel):
    message_id: str
    thread_id: str
    subject: str
    sender: Address
    reply_to: list[Address] = Field(description="Reply-To header; reply here if non-empty, else to sender.")
    to: list[Address]
    cc: list[Address]
    me: Address = Field(
        description="The signed-in user (who a reply is sent from). Sign off with me.name; "
        "if it is empty, ask the user for their name instead of guessing."
    )


class SendResult(BaseModel):
    sent: bool = Field(description="False for a dry run; True if Gmail accepted the message.")
    message_id: str | None = Field(None, description="ID of the sent message (null on dry run).")
    thread_id: str | None = None
    preview: dict = Field(description="Exactly what is (or would be) sent.")
    note: str


# ---------- helpers ----------


def _addresses(raw: str | None) -> list[Address]:
    if not raw:
        return []
    return [Address(name=n, email=e) for n, e in getaddresses([raw]) if e]


def _headers(payload: dict) -> dict[str, str]:
    return {h["name"].lower(): h["value"] for h in payload.get("headers", [])}


def _decode(data: str) -> str:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4)).decode("utf-8", "replace")


def _find_part(payload: dict, mime: str) -> str | None:
    if payload.get("mimeType") == mime and payload.get("body", {}).get("data"):
        return _decode(payload["body"]["data"])
    for part in payload.get("parts", []) or []:
        found = _find_part(part, mime)
        if found:
            return found
    return None


def _plain_body(payload: dict) -> str:
    text = _find_part(payload, "text/plain")
    if text is None:
        h = _find_part(payload, "text/html") or ""
        h = re.sub(r"(?is)<(script|style).*?</\1>", "", h)
        text = html.unescape(re.sub(r"<[^>]+>", " ", h))
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", text)).strip()


# ---------- client ----------


class GmailClient:
    def __init__(self, timeout: float = 20.0) -> None:
        self._http = httpx.Client(base_url=API, timeout=timeout)
        self._me: Address | None = None

    def _request(self, method: str, path: str, **kwargs) -> dict:
        for attempt in range(2):
            creds = auth.get_credentials(force_refresh=attempt > 0)
            headers = {"Authorization": f"Bearer {creds.token}"}
            try:
                resp = self._http.request(method, path, headers=headers, **kwargs)
            except httpx.TimeoutException as e:
                raise GmailError(
                    "upstream_unavailable", "Gmail request timed out.", retryable=True, retry_after_seconds=5
                ) from e
            except httpx.TransportError as e:
                raise GmailError(
                    "upstream_unavailable", f"Network error: {e}", retryable=True, retry_after_seconds=5
                ) from e
            # 401 once -> token may have died mid-session; refresh silently and retry.
            if resp.status_code == 401 and attempt == 0:
                continue
            return self._handle(resp)
        raise AssertionError("unreachable")

    @staticmethod
    def _handle(resp: httpx.Response) -> dict:
        if resp.is_success:
            return resp.json() if resp.content else {}
        try:
            detail = resp.json().get("error", {}).get("message", resp.text)
        except ValueError:
            detail = resp.text
        status = resp.status_code
        if status == 401:
            raise GmailError("auth_required", f"Gmail rejected the token: {detail}", retryable=False, hint=AUTH_HINT)
        if status == 403 and "rate" not in detail.lower():
            raise GmailError("permission_denied", detail, retryable=False, hint=AUTH_HINT)
        if status == 404:
            raise GmailError(
                "not_found",
                "No message with that ID.",
                retryable=False,
                hint="Get a valid message_id from read_recent_emails; do not retry with the same ID.",
            )
        if status == 400:
            raise GmailError("invalid_request", detail, retryable=False, hint="Fix the arguments before retrying.")
        if status in (403, 429):
            retry_after = int(resp.headers.get("Retry-After", "30") or 30)
            raise GmailError(
                "rate_limited", f"Gmail rate limit hit: {detail}", retryable=True, retry_after_seconds=retry_after
            )
        raise GmailError(
            "upstream_unavailable", f"Gmail returned HTTP {status}.", retryable=True, retry_after_seconds=10
        )

    # ----- read -----

    def recent_emails(self, count: int, label: str) -> list[EmailSummary]:
        listing = self._request("GET", "/messages", params={"maxResults": count, "labelIds": label})
        out = []
        for ref in listing.get("messages", []):
            msg = self._request("GET", f"/messages/{ref['id']}", params={"format": "full"})
            h = _headers(msg["payload"])
            body = _plain_body(msg["payload"])
            sender = _addresses(h.get("from"))
            out.append(
                EmailSummary(
                    message_id=msg["id"],
                    thread_id=msg["threadId"],
                    date=h.get("date", ""),
                    sender=sender[0] if sender else Address(name="", email=""),
                    subject=h.get("subject", "(no subject)"),
                    snippet=html.unescape(msg.get("snippet", "")),
                    body=body[:MAX_BODY_CHARS],
                    body_truncated=len(body) > MAX_BODY_CHARS,
                    labels=msg.get("labelIds", []),
                )
            )
        return out

    def me(self) -> Address:
        """The signed-in user's primary send-as identity (cached per process)."""
        if self._me is None:
            send_as = self._request("GET", "/settings/sendAs").get("sendAs", [])
            primary = next((a for a in send_as if a.get("isPrimary")), None)
            if primary:
                self._me = Address(name=primary.get("displayName", ""), email=primary["sendAsEmail"])
            else:
                self._me = Address(name="", email=self._request("GET", "/profile")["emailAddress"])
        return self._me

    def _metadata(self, message_id: str) -> dict:
        return self._request(
            "GET",
            f"/messages/{message_id}",
            params={
                "format": "metadata",
                "metadataHeaders": ["From", "To", "Cc", "Reply-To", "Subject", "Message-ID", "References"],
            },
        )

    def recipients(self, message_id: str) -> EmailRecipients:
        msg = self._metadata(message_id)
        h = _headers(msg["payload"])
        sender = _addresses(h.get("from"))
        return EmailRecipients(
            message_id=msg["id"],
            thread_id=msg["threadId"],
            subject=h.get("subject", "(no subject)"),
            sender=sender[0] if sender else Address(name="", email=""),
            reply_to=_addresses(h.get("reply-to")),
            to=_addresses(h.get("to")),
            cc=_addresses(h.get("cc")),
            me=self.me(),
        )

    # ----- write -----

    def build_message(
        self,
        to: list[str],
        subject: str | None,
        body: str,
        cc: list[str],
        reply_to_message_id: str | None,
    ) -> tuple[EmailMessage, str | None]:
        msg = EmailMessage()
        msg["To"] = ", ".join(to)
        if cc:
            msg["Cc"] = ", ".join(cc)
        thread_id = None
        if reply_to_message_id:
            orig = self._metadata(reply_to_message_id)
            h = _headers(orig["payload"])
            thread_id = orig["threadId"]
            if h.get("message-id"):
                msg["In-Reply-To"] = h["message-id"]
                msg["References"] = f"{h.get('references', '')} {h['message-id']}".strip()
            if subject is None:
                orig_subject = h.get("subject", "")
                subject = orig_subject if orig_subject.lower().startswith("re:") else f"Re: {orig_subject}"
        msg["Subject"] = subject or "(no subject)"
        msg.set_content(body)
        return msg, thread_id

    def send(self, msg: EmailMessage, thread_id: str | None) -> dict:
        payload: dict = {"raw": base64.urlsafe_b64encode(msg.as_bytes()).decode()}
        if thread_id:
            payload["threadId"] = thread_id
        return self._request("POST", "/messages/send", json=payload)
