# Week 2: Gmail MCP server (FastMCP, stdio, OAuth 2.0)

## Run (from repo root)

```bash
uv run --directory week2 gmail-mcp          # start the MCP server over stdio
uv run --directory week2 gmail-mcp auth     # one-time Google sign-in (opens a browser)
uv run --directory week2 pytest             # protocol-level tests (no Google account needed)
```

## One-time Google setup

1. https://console.cloud.google.com → create a project.
2. **APIs & Services → Library** → enable **Gmail API**.
3. **APIs & Services → OAuth consent screen** → User type *External*, add your own Gmail
   address under **Test users**. Add scopes `gmail.readonly` and `gmail.send`.
4. **APIs & Services → Credentials → Create credentials → OAuth client ID** → type **Desktop app**.
5. `cp week2/.env.example week2/.env` and paste the client ID and secret.
6. `uv run --directory week2 gmail-mcp auth` → approve in the browser. The token is cached at
   `~/.gmail-mcp/token.json` (outside the repo).

> While the consent screen is in *Testing* mode, Google expires refresh tokens after 7 days.
> When that happens the tools return `auth_required`; just re-run step 6.

## Register with Claude Code

```bash
cp week2/.mcp.json.example .mcp.json    # .mcp.json is gitignored
```

Claude Code expands `${GOOGLE_CLIENT_ID}`/`${GOOGLE_CLIENT_SECRET}` from your shell env. If
those aren't set, the server falls back to `week2/.env`.

## Tools

| Tool | R/W | Composes with |
|---|---|---|
| `read_recent_emails(count=1, label="INBOX")` | read | its `message_id` → `get_email_recipients`, `send_email.reply_to_message_id` |
| `get_email_recipients(message_id)` | read | its addresses → `send_email.to` / `cc` |
| `send_email(to, body, subject?, cc?, reply_to_message_id?, dry_run=True)` | **write** | — |
