"""Google OAuth 2.0: authorization-code flow, token caching, silent refresh.

- `run_login()` is the ONLY place a browser is opened. It is invoked by the
  `gmail-mcp auth` CLI command, never from inside a tool call.
- `get_credentials()` is used by the running server. It loads the cached token,
  refreshes it silently if expired, and raises an actionable GmailError if the
  token is missing or has been revoked.

Client ID/secret come from the environment (GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET),
never from a file in the repo. The token cache lives outside the repo by default.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

from google.auth.exceptions import RefreshError, TransportError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .errors import AUTH_HINT, GmailError

# Minimal scopes:
#   gmail.readonly -> read message headers/bodies (needed by the two read tools)
#   gmail.send     -> send mail only; cannot read, modify, or delete anything
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]

_refresh_lock = threading.Lock()


def token_path() -> Path:
    default = Path.home() / ".gmail-mcp" / "token.json"
    return Path(os.environ.get("GMAIL_MCP_TOKEN_PATH", default)).expanduser()


def _client_config() -> dict:
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit(
            "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set (see week2/.env.example)."
        )
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }


def _save(creds: Credentials) -> None:
    path = token_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(creds.to_json(), encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass  # best effort on Windows


def run_login() -> Path:
    """Interactive authorization-code flow (opens a browser). CLI use only."""
    flow = InstalledAppFlow.from_client_config(_client_config(), SCOPES)
    # access_type=offline + prompt=consent guarantees we get a refresh token.
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
    _save(creds)
    return token_path()


def get_credentials(force_refresh: bool = False) -> Credentials:
    """Return valid credentials, refreshing silently. Never opens a browser."""
    path = token_path()
    if not path.exists():
        raise GmailError(
            "auth_required",
            f"No cached Google token at {path}.",
            retryable=False,
            hint=AUTH_HINT,
        )

    creds = Credentials.from_authorized_user_file(str(path), SCOPES)
    missing = set(SCOPES) - set(creds.scopes or [])
    if missing:
        raise GmailError(
            "permission_denied",
            f"Cached token is missing scopes: {sorted(missing)}.",
            retryable=False,
            hint=AUTH_HINT,
        )

    if creds.valid and not force_refresh:
        return creds

    if not creds.refresh_token:
        raise GmailError(
            "auth_required", "Token expired and has no refresh token.", retryable=False, hint=AUTH_HINT
        )

    with _refresh_lock:
        try:
            creds.refresh(Request())
        except RefreshError as e:
            # invalid_grant: user revoked access, password change, or 7-day testing-app expiry
            raise GmailError(
                "auth_required",
                f"Google rejected the refresh token ({e.args[0] if e.args else 'invalid_grant'}).",
                retryable=False,
                hint=AUTH_HINT,
            ) from e
        except TransportError as e:
            raise GmailError(
                "upstream_unavailable",
                "Network error while refreshing the Google token.",
                retryable=True,
                retry_after_seconds=5,
            ) from e
        _save(creds)
    return creds
