"""Structured, agent-readable errors.

Every failure the agent can hit is turned into a GmailError, which the server
serializes into the tool result. The `retryable` flag is the key bit: it tells
the agent whether calling again could possibly help.
"""

from __future__ import annotations

import json
from typing import Literal

ErrorCode = Literal[
    "auth_required",  # no token / token revoked -> human must run `gmail-mcp auth`
    "not_found",  # bad message_id -> don't retry with the same ID
    "invalid_request",  # Gmail rejected the arguments -> fix args, don't retry as-is
    "permission_denied",  # scope missing -> re-run auth
    "rate_limited",  # retry after `retry_after_seconds`
    "upstream_unavailable",  # Gmail 5xx / network blip -> retry shortly
]


class GmailError(Exception):
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        *,
        retryable: bool,
        hint: str | None = None,
        retry_after_seconds: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable
        self.hint = hint
        self.retry_after_seconds = retry_after_seconds

    def to_dict(self) -> dict:
        data: dict = {"error": self.code, "message": self.message, "retryable": self.retryable}
        if self.hint:
            data["hint"] = self.hint
        if self.retry_after_seconds is not None:
            data["retry_after_seconds"] = self.retry_after_seconds
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


AUTH_HINT = (
    "A human must run `uv run --directory week2 gmail-mcp auth` in a terminal to sign in "
    "again, then retry. Do not retry before that."
)
