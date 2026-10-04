"""FastMCP server exposing three composing Gmail tools over stdio.

    read_recent_emails  --message_id-->  get_email_recipients  --addresses-->  send_email
                        --message_id----------------------------(reply_to_message_id)-->
"""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import EmailStr, Field

from .errors import GmailError
from .gmail import EmailRecipients, EmailSummary, GmailClient, SendResult

INSTRUCTIONS = """\
Gmail tools for the signed-in user.

Typical workflow:
1. read_recent_emails -> returns emails with a `message_id`.
2. get_email_recipients(message_id) -> who sent it, who else was on it, and `me`
   (the signed-in user). Sign emails with `me.name`; if it is empty, ask the user
   for their name. Never guess it from file paths or other context.
3. send_email(..., dry_run=true) to preview, show the preview to the user, then
   send_email(..., dry_run=false) only after the user confirms. To reply in-thread,
   pass the original `message_id` as `reply_to_message_id`.

Errors come back as JSON with `error`, `message`, `retryable` and sometimes `hint`
/ `retry_after_seconds`. If `retryable` is false, do not repeat the same call;
follow the hint (e.g. `auth_required` means a human must re-run the auth command).
"""

mcp = FastMCP("gmail", instructions=INSTRUCTIONS)

_client: GmailClient | None = None


def get_client() -> GmailClient:
    """Lazily build the client so the server starts even before auth is set up."""
    global _client
    if _client is None:
        _client = GmailClient()
    return _client


Label = Literal["INBOX", "SENT", "UNREAD", "STARRED", "IMPORTANT", "SPAM", "DRAFT"]


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": True, "title": "Read recent emails"},
)
def read_recent_emails(
    count: Annotated[int, Field(ge=1, le=10, description="How many of the newest emails to return.")] = 1,
    label: Annotated[Label, Field(description="Which mailbox to read from.")] = "INBOX",
) -> list[EmailSummary]:
    """Read the most recent email(s) in a mailbox, newest first.

    Returns sender, subject, date, and a plain-text body (truncated) for each email.
    Each result's `message_id` can be passed to `get_email_recipients` or used as
    `reply_to_message_id` in `send_email`. Returns an empty list if the mailbox is empty.
    """
    try:
        return get_client().recent_emails(count=count, label=label)
    except GmailError as e:
        raise ToolError(e.to_json()) from e


@mcp.tool(
    annotations={"readOnlyHint": True, "openWorldHint": True, "title": "Get email recipients"},
)
def get_email_recipients(
    message_id: Annotated[
        str,
        Field(
            min_length=1,
            pattern=r"^[A-Za-z0-9]+$",
            description="Gmail message ID: the `message_id` field from read_recent_emails.",
        ),
    ],
) -> EmailRecipients:
    """Get the sender and all recipients (To, Cc, Reply-To) of one email, plus `me`.

    Use this to find who to reply to or who else was on an email. The returned
    addresses can be passed directly to `send_email`'s `to` / `cc`. `me` is the
    signed-in user: use `me.name` to sign a reply, and ask the user if it is empty.
    """
    try:
        return get_client().recipients(message_id)
    except GmailError as e:
        raise ToolError(e.to_json()) from e


@mcp.tool(
    annotations={
        "readOnlyHint": False,
        "destructiveHint": True,  # sending is irreversible
        "idempotentHint": False,  # calling twice sends two emails
        "openWorldHint": True,
        "title": "Send email",
    },
)
def send_email(
    to: Annotated[list[EmailStr], Field(min_length=1, max_length=20, description="Recipient addresses.")],
    body: Annotated[str, Field(min_length=1, max_length=20000, description="Plain-text body.")],
    subject: Annotated[
        str | None,
        Field(max_length=300, description="Subject line. Required unless replying; when replying, defaults to 'Re: <original subject>'."),
    ] = None,
    cc: Annotated[list[EmailStr], Field(max_length=20, description="Cc addresses.")] = [],
    reply_to_message_id: Annotated[
        str | None,
        Field(
            pattern=r"^[A-Za-z0-9]+$",
            description="To reply in-thread, the `message_id` from read_recent_emails. Omit for a new email.",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        Field(description="true (default): build and return a preview, send nothing. false: actually send."),
    ] = True,
) -> SendResult:
    """Send an email (or reply in-thread) from the signed-in Gmail account.

    IRREVERSIBLE when dry_run=false. Always call first with dry_run=true, show the
    preview to the user, and only call again with dry_run=false after they confirm.
    The preview's `from` is the signed-in user; sign the body with that name, or ask
    the user for it if `from` has no name. Do not guess the user's name.
    """
    if subject is None and reply_to_message_id is None:
        raise ToolError(
            GmailError(
                "invalid_request",
                "`subject` is required when not replying.",
                retryable=False,
                hint="Pass `subject`, or pass `reply_to_message_id` to reply to an existing email.",
            ).to_json()
        )
    try:
        client = get_client()
        msg, thread_id = client.build_message(
            to=[str(a) for a in to],
            subject=subject,
            body=body,
            cc=[str(a) for a in cc],
            reply_to_message_id=reply_to_message_id,
        )
        me = client.me()
        preview = {
            "from": f"{me.name} <{me.email}>" if me.name else me.email,
            "to": msg["To"],
            "cc": msg["Cc"] or "",
            "subject": msg["Subject"],
            "body": body,
            "in_reply_to_thread": thread_id,
        }
        if dry_run:
            return SendResult(
                sent=False,
                preview=preview,
                note="Dry run: nothing was sent. Confirm with the user, then call again with dry_run=false.",
            )
        result = client.send(msg, thread_id)
        return SendResult(
            sent=True,
            message_id=result.get("id"),
            thread_id=result.get("threadId"),
            preview=preview,
            note="Sent. Do not call again for this email or it will be sent twice.",
        )
    except GmailError as e:
        raise ToolError(e.to_json()) from e
