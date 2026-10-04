"""Protocol-level tests: every call goes through an MCP Client session against
the real FastMCP server (in-memory transport). Only the Gmail HTTP layer is faked.
"""

from __future__ import annotations

import json

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from gmail_mcp import server
from gmail_mcp.errors import GmailError
from gmail_mcp.gmail import Address, EmailRecipients, EmailSummary, GmailClient


class FakeGmail(GmailClient):
    def __init__(self) -> None:
        self.sent: list = []

    def recent_emails(self, count, label):
        return [
            EmailSummary(
                message_id="abc123",
                thread_id="t1",
                date="Fri, 2 Oct 2026 10:00:00 -0700",
                sender=Address(name="Ada", email="ada@example.com"),
                subject="Lunch?",
                snippet="Want to grab lunch",
                body="Want to grab lunch tomorrow?",
                body_truncated=False,
                labels=[label],
            )
        ][:count]

    def recipients(self, message_id):
        if message_id != "abc123":
            raise GmailError("not_found", "No message with that ID.", retryable=False)
        return EmailRecipients(
            message_id="abc123",
            thread_id="t1",
            subject="Lunch?",
            sender=Address(name="Ada", email="ada@example.com"),
            reply_to=[],
            to=[Address(name="Me", email="me@example.com")],
            cc=[Address(name="Bob", email="bob@example.com")],
            me=self.me(),
        )

    def me(self):
        return Address(name="Me Myself", email="me@example.com")

    def _metadata(self, message_id):
        return {
            "threadId": "t1",
            "payload": {"headers": [{"name": "Subject", "value": "Lunch?"}, {"name": "Message-ID", "value": "<m1@x>"}]},
        }

    def send(self, msg, thread_id):
        self.sent.append((msg, thread_id))
        return {"id": "sent1", "threadId": thread_id or "new"}


@pytest.fixture
def fake(monkeypatch):
    f = FakeGmail()
    monkeypatch.setattr(server, "get_client", lambda: f)
    return f


async def test_tools_listed_with_annotations():
    async with Client(server.mcp) as c:
        tools = {t.name: t for t in await c.list_tools()}
    assert set(tools) == {"read_recent_emails", "get_email_recipients", "send_email"}
    assert tools["read_recent_emails"].annotations.read_only_hint is True
    assert tools["send_email"].annotations.read_only_hint is False
    assert tools["read_recent_emails"].input_schema["properties"]["label"]["enum"][0] == "INBOX"


async def test_chain_read_then_recipients_then_reply_dry_run(fake):
    async with Client(server.mcp) as c:
        emails = (await c.call_tool("read_recent_emails", {})).structured_content["result"]
        mid = emails[0]["message_id"]
        rec = (await c.call_tool("get_email_recipients", {"message_id": mid})).structured_content
        res = await c.call_tool(
            "send_email",
            {"to": [rec["sender"]["email"]], "body": "Sure!", "reply_to_message_id": mid},
        )
    out = res.structured_content
    assert rec["me"] == {"name": "Me Myself", "email": "me@example.com"}
    assert out["preview"]["from"] == "Me Myself <me@example.com>"
    assert out["sent"] is False  # dry_run defaults to true
    assert out["preview"]["subject"] == "Re: Lunch?"
    assert fake.sent == []


async def test_send_for_real(fake):
    async with Client(server.mcp) as c:
        res = await c.call_tool(
            "send_email", {"to": ["ada@example.com"], "subject": "Hi", "body": "Hello", "dry_run": False}
        )
    assert res.structured_content["sent"] is True
    assert len(fake.sent) == 1


async def test_bad_id_is_structured_non_retryable_error(fake):
    async with Client(server.mcp) as c:
        with pytest.raises(ToolError) as exc:
            await c.call_tool("get_email_recipients", {"message_id": "doesnotexist"})
    err = json.loads(str(exc.value))
    assert err["error"] == "not_found" and err["retryable"] is False


async def test_schema_rejects_invalid_email(fake):
    async with Client(server.mcp) as c:
        with pytest.raises(ToolError):
            await c.call_tool("send_email", {"to": ["not-an-email"], "subject": "x", "body": "y"})


async def test_missing_token_gives_auth_hint(monkeypatch, tmp_path):
    monkeypatch.setenv("GMAIL_MCP_TOKEN_PATH", str(tmp_path / "none.json"))
    monkeypatch.setattr(server, "_client", None)
    async with Client(server.mcp) as c:
        with pytest.raises(ToolError) as exc:
            await c.call_tool("read_recent_emails", {"count": 1})
    err = json.loads(str(exc.value))
    assert err["error"] == "auth_required" and "gmail-mcp auth" in err["hint"]
