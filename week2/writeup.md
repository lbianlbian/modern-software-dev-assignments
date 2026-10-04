# Week 2 Write-up

## Part I: The Server

**API chosen**, and why:
Google because I frequently use the GSuite applications like Gmail, Google Docs, and Google Sheets and these require OAuth 2.0. 

**How to run it** (one command):
```
uv run --directory week2 gmail-mcp
```

| Tool | What it does | Read/Write | Composes with |
|---|---|---|---|
| read_recent_emails | reads the most recent emails of the connected gmail account | read | none |
| get_email_recipients | extracts all email addresses involved in an email | read | read_recent_emails |
| send_email | sends an email with the authenticated google account | write | get_email_recipients |


## Part II: Agent Ergonomics

For each, point at the code (`file:line`) and say what it buys.

| Decision | Where | Why |
|---|---|---|
| Schema-level constraint | `week2/gmail_mcp/server.py:48`, `:55-56`, `:74-81`, `:105-111` | `label` is a `Literal` of real Gmail labels, `count` is bounded 1-10, `message_id` has a regex pattern, and `to`/`cc` are `list[EmailStr]` with length caps. The agent sees the valid values in the JSON schema, so bad args are rejected at validation with a clear message instead of turning into a confusing Gmail 400. |
| Output shaping (fields kept vs. dropped) | `week2/gmail_mcp/gmail.py:28-64`, `:94-100`, `:164-185` | Raw Gmail messages are nested MIME trees with base64 parts and dozens of headers. I return small pydantic models: id, thread, date, parsed sender, subject, snippet, a plain-text body (HTML stripped, truncated to 2000 chars with a `body_truncated` flag), and labels. Addresses are parsed into `{name, email}` so they can go straight into `send_email`. This saves tokens and means my contract doesn't change if Gmail's payload does. |
| Structured errors (retry vs. don't-retry) | `week2/gmail_mcp/errors.py:13-49`, `week2/gmail_mcp/gmail.py:132-160` | Every HTTP or network failure becomes JSON with `error`, `message`, `retryable`, and optionally `hint` / `retry_after_seconds`. A bad ID (404), bad args (400), or a dead token (401) is `retryable: false` with a hint about what to do instead. Rate limits (429) and 5xx/timeouts are `retryable: true` with a wait time. The agent can tell "fix it or ask a human" apart from "wait and try again". |
| Docstring that chains tools together | `week2/gmail_mcp/server.py:18-33`, `:58-63`, `:79`, `:83-88`, `week2/gmail_mcp/gmail.py:34` | The docstrings and field descriptions say where each ID comes from ("the `message_id` field from read_recent_emails") and where outputs go (recipients "can be passed directly to `send_email`'s `to` / `cc`"). `FastMCP(instructions=...)` spells out the whole read -> recipients -> preview -> confirm -> send workflow. |
| Brake on the write tool | `week2/gmail_mcp/server.py:95-103`, `:119-130`, `:158-171` | `send_email` is annotated `destructiveHint: true` and `idempotentHint: false`, and the readers are `readOnlyHint: true`. `dry_run` defaults to `true`, so the default call only returns a preview of exactly what would be sent. Actually sending requires an explicit `dry_run=false`, and the docstring tells the agent to confirm with the user first. After a real send, the result says not to call again so the email isn't sent twice. |

**One thing you changed after watching the agent misuse a tool:**
> When I asked the agent to reply to a test email, it drafted a reply signed "Best, Wesley" and said it had "guessed the name 'Wesley' from your user folder." It got lucky, but it was signing an email as me based on a Windows file path. The problem was in my tools, not the agent: nothing told it who the signed-in user was. `get_email_recipients` returned the To/Cc addresses, but with no way to tell which one was me, and display names in headers are often empty, so even calling it wouldn't have helped.
>
> The fix: `GmailClient.me()` (`week2/gmail_mcp/gmail.py:187`) reads the account's primary send-as identity (display name + email; this works under the existing `gmail.readonly` scope). `get_email_recipients` now returns it as a `me` field (`gmail.py:53`), and the `send_email` preview shows a `from` line (`week2/gmail_mcp/server.py:151`). The `me` field description, both tool docstrings, and the server instructions (`server.py:23-25`, `:87`, `:128-129`) tell the agent to sign with `me.name` and to ask the user if it's empty, never to guess. On my account the send-as display name is actually empty, so the agent now asks for my name instead of inventing one, which is the behavior I want. The protocol test (`week2/tests/test_server.py`) checks that `me` and the preview's `from` come through.


## Part III: OAuth

**Flow**: how a token is obtained, cached, and refreshed:
> **Obtained:** a human runs `uv run --directory week2 gmail-mcp auth` once. `run_login()` (`week2/gmail_mcp/auth.py:70-76`) builds the client config from env vars and runs `InstalledAppFlow.run_local_server(port=0)`. That starts a loopback server on a random localhost port, opens the Google consent page, and receives the authorization code at the redirect. It then exchanges the code for an access token and a refresh token. The OAuth client is a **Desktop app** client, since only those accept a loopback redirect on any port (my first attempt used a Web client and Google rejected the `redirect_uri`). `access_type="offline"` and `prompt="consent"` make sure Google returns a refresh token.
>
> **Cached:** the credentials are written to `~/.gmail-mcp/token.json`, outside the repo (override with `GMAIL_MCP_TOKEN_PATH`), with `chmod 600` where the OS supports it (`auth.py:37-39`, `:60-67`).
>
> **Refreshed:** on every Gmail call the server runs `get_credentials()` (`auth.py:79-127`). It loads the cached token and returns it as-is while it's valid. If it has expired, it refreshes it silently with the refresh token and saves the new one. A lock keeps concurrent tool calls from refreshing at the same time. This is the only code path the server uses, and it never opens a browser; only the `auth` CLI command does.

**Scopes requested**, and why each is necessary:
> - `gmail.readonly`: needed by `read_recent_emails` (message bodies and headers) and `get_email_recipients` (To/Cc/Reply-To headers). It also covers reading the send-as identity (`settings/sendAs`) behind the `me` field, and reading the original message's `Message-ID` so a reply threads correctly.
> - `gmail.send`: needed by `send_email`. It can only send; it can't read, modify, label, or delete anything.
>
> I deliberately did not request `gmail.modify` or the full `https://mail.google.com/` scope, since no tool moves, archives, or deletes mail. `get_credentials()` also checks that the cached token actually has both scopes and returns a `permission_denied` error with the re-auth hint if one is missing (`auth.py:91-98`).

**Secrets**: what's in env, what's gitignored:
> - **In env:** `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`, read only from environment variables (`auth.py:42-57`). For local runs they live in `week2/.env`, which `__main__.py` loads with `python-dotenv`; variables passed by the MCP client take precedence. `week2/.env.example` is committed with placeholder values. Nothing in the repo contains a real client ID or secret.
> - **Gitignored:** `.env`, the real `.mcp.json`, `token.json`, `client_secret*.json`, and `credentials.json` (verified with `git check-ignore`). The cached token lives in my home directory, not the repo, so it couldn't be committed by accident even without the ignore rule. Only `.mcp.json.example` is committed.

**Token dies mid-session**: what the agent sees:
> There are two cases.
>
> 1. **Access token expires or is rejected:** the agent sees nothing. `get_credentials()` refreshes expired tokens before the request. If Gmail still returns a 401 (e.g. the token was invalidated server-side), `GmailClient._request` (`week2/gmail_mcp/gmail.py:125-127`) forces one refresh and retries the call once.
> 2. **Refresh token is dead** (access revoked, password changed, or the 7-day refresh-token expiry for apps in "Testing" mode), or the token file is missing: the server does **not** open a browser in the middle of a tool call. It raises `GmailError("auth_required", ...)` (`auth.py:82-88`, `:111-118`), and the tool returns it as a tool error. For a revoked refresh token it looks like this (the `message` text comes from Google and varies):
>
>    ```json
>    {"error": "auth_required",
>     "message": "Google rejected the refresh token (invalid_grant: Token has been expired or revoked.).",
>     "retryable": false,
>     "hint": "A human must run `uv run --directory week2 gmail-mcp auth` in a terminal to sign in again, then retry. Do not retry before that."}
>    ```
>
>    Because `retryable` is false and the server instructions say to follow the hint, the agent stops and asks me to run the auth command instead of looping. Once I've re-authenticated, the next tool call loads the new token file without restarting the server. The test `test_missing_token_gives_auth_hint` covers this path.


## Part IV: Integration

**Registration config** (`.mcp.json.example`) and the client you used:
> I used Claude Code as the client of the MCP server and .mcp.json.example is the example registration config.

**End-to-end transcript**: the prompt, the tools that fired with their arguments, the result:
```
❯ read my most recent email and respond appropriately to it

● gmail - Read recent emails (MCP)(count: 1)
{
  "result": [
    {
      "message_id": "1a1068b5ec00beb1",
      "thread_id": "1a1068b5ec00beb1",
      "date": "Sun, 4 Oct 2026 03:52:04 -0700",
      "sender": {
        "name": "Andrew Dragon",
        "email": "t6idetectives@gmail.com"
      },
      "subject": "a test email",
      "snippet": "does the mcp server work? Send me back an email if so",
      "body": "does the mcp server work? Send me back an email if so",
      "body_truncated": false,
      "labels": [
        "UNREAD",
        "IMPORTANT",
        "CATEGORY_PERSONAL",
        "INBOX"
      ]
    }
  ]
}
Allowed by auto mode classifier

● gmail - Get email recipients (MCP)(message_id: "1a1068b5ec00beb1")
{
  "message_id": "1a1068b5ec00beb1",
  "thread_id": "1a1068b5ec00beb1",
  "subject": "a test email",
  "sender": {
    "name": "Andrew Dragon",
    "email": "t6idetectives@gmail.com"
  ]
}
Allowed by auto mode classifier

● gmail - Get email recipients (MCP)(message_id: "1a1068b5ec00beb1")
{
  "message_id": "1a1068b5ec00beb1",
  "thread_id": "1a1068b5ec00beb1",
  "subject": "a test email",
  "sender": {
    "name": "Andrew Dragon",
    "email": "t6idetectives@gmail.com"
  },
  "reply_to": [],
  "to": [
    {
      "name": "",
      "email": "wesleybian@gmail.com"
    }
  ],
  "cc": [],
  "me": {
    "name": "",
    "email": "wesleybian@gmail.com"
  }
}
Allowed by auto mode classifier

                                                                                        03:52 AM claude-opus-5-5
Your most recent email is from Andrew Dragon (t6idetectives@gmail.com), subject "a test email":

▎ does the mcp server work? Send me back an email if so

They want a reply confirming the MCP server works. Here's the draft I'd send in the same thread:

▎ To: t6idetectives@gmail.com
▎ Subject: Re: a test email
▎
▎ Hi Andrew,
▎
▎ Yes, the MCP server works. I read your email and sent this reply through it.
▎
▎ Best,
▎ [your name]

Your Gmail account (wesleybian@gmail.com) has no display name set, so I need you to tell me what name to sign with. I won't guess it. Once you give me the name and confirm, I'll send it.

✻ Worked for 13s · done 3:52 AM

❯ use the name WB

● gmail - Send email (MCP)(to: ["t6idetectives@gmail.com"], body: "Hi Andrew,\n\nYes, the MCP server works. I read your email and sent this reply through it.\n\nBest,\nWB", reply_to_message_id: "1a1068b5ec00beb1", dry_run: true)
{
  "sent": false,
  "message_id": null,
  "thread_id": null,
  "preview": {
    "from": "wesleybian@gmail.com",
    "to": "t6idetectives@gmail.com",
    "cc": "",
    "subject": "Re: a test email",
    "body": "Hi Andrew,\n\nYes, the MCP server works. I read your email and sent this reply through it.\n\nBest,\nWB",
    "in_reply_to_thread": "1a1068b5ec00beb1"
  },
  "note": "Dry run: nothing was sent. Confirm with the user, then call again with dry_run=false."
}
Allowed by auto mode classifier

                                                                                        03:53 AM claude-opus-5-5
Here's the preview with your name added. Nothing has been sent yet.

▎ From: wesleybian@gmail.com
▎ To: t6idetectives@gmail.com
▎ Subject: Re: a test email (reply in the same thread)
▎
▎ Hi Andrew,
▎
▎ Yes, the MCP server works. I read your email and sent this reply through it.
▎
▎ Best,
▎ WB

Should I send it?

✻ Cooked for 9s · done 3:53 AM

❯ yes
✻ Cooked for 9s · done 3:53 AM

❯ yes

● gmail - Send email (MCP)(to: ["t6idetectives@gmail.com"], body: "Hi Andrew,\n\nYes, the MCP server works. I read your email and sent this reply through it.\n\nBest,\nWB", reply_to_message_id: "1a1068b5ec00beb1", dry_run: false)
{
  "sent": true,
  "message_id": "1a1068c79a90671a",
  "thread_id": "1a1068b5ec00beb1",
  "preview": {
    "from": "wesleybian@gmail.com",
    "to": "t6idetectives@gmail.com",
    "cc": "",
    "subject": "Re: a test email",
    "body": "Hi Andrew,\n\nYes, the MCP server works. I read your email and sent this reply through it.\n\nBest,\nWB",
    "in_reply_to_thread": "1a1068b5ec00beb1"
  },
  "note": "Sent. Do not call again for this email or it will be sent twice."
}
Allowed by auto mode classifier

                                                                                        03:53 AM claude-opus-5-5
I sent your reply to Andrew (t6idetectives@gmail.com) in the "a test email" thread. It confirms the MCP server works and is signed "WB".
```

**A failure, handled**: what you provoked, what the agent saw, what it did next:
```
❯ who sent me the  email with message id 18c0ffee00000000?

● gmail - Get email recipients (MCP)(message_id: "18c0ffee00000000")
Error: {"error": "not_found", "message": "No message with that ID.", "retryable": false, "hint": "Get a valid message_id from read_recent_emails; do not retry with the same ID."}

                                                                                        03:34 AM claude-opus-5-5
There's no email with ID 18c0ffee00000000 in your account. The ID could be mistyped, or the message may have been deleted. It also looks like a made-up placeholder ("c0ffee"), so it may never have been a real ID.

If you tell me roughly what the email was about or when it came in, I can pull up your recent emails and find the right one.
```

**Protocol-level test**: what it covers and how to run it:
> `week2/tests/test_server.py` drives the real FastMCP server through a real MCP `Client` session over FastMCP's in-memory transport. Every call goes through MCP `list_tools` / `call_tool`, so it exercises schema generation, argument validation, structured output, and error serialization the same way Claude Code sees them. Only the Gmail HTTP layer is replaced, by a `FakeGmail` subclass of `GmailClient`, so no Google account or network is needed. The six tests:
>
> 1. `test_tools_listed_with_annotations`: exactly the three tools are listed, the readers carry `readOnlyHint: true` and `send_email` doesn't, and `label` shows up in the JSON schema as an `enum`.
> 2. `test_chain_read_then_recipients_then_reply_dry_run`: the full chain. `read_recent_emails`, then pass its `message_id` to `get_email_recipients`, then pass the sender's address and `reply_to_message_id` to `send_email`. Checks that `dry_run` defaults to true and nothing is sent, the subject becomes `Re: …`, and `me` and the preview's `from` come through.
> 3. `test_send_for_real`: `dry_run=false` actually sends exactly once.
> 4. `test_bad_id_is_structured_non_retryable_error`: an unknown ID comes back as JSON `{"error": "not_found", "retryable": false, ...}`, not a traceback.
> 5. `test_schema_rejects_invalid_email`: `to: ["not-an-email"]` is rejected by schema validation before any Gmail code runs.
> 6. `test_missing_token_gives_auth_hint`: uses the real `GmailClient` and auth code with `GMAIL_MCP_TOKEN_PATH` pointed at a missing file. The tool returns `auth_required` with the `gmail-mcp auth` hint instead of opening a browser.
>
> Run from the repo root with `uv run --directory week2 pytest -v`. All 6 pass.


## Submission
1. `Command (⌘) + F` for `TODO`. No results means you're done.
2. Confirm no tokens, client secrets, cached token file, or real `.mcp.json` are committed.
3. Push all changes to your remote repository and submit via Gradescope.
4. Clean up (optional): remove the server from your agent config, delete your cached token, and revoke the OAuth app's access.
