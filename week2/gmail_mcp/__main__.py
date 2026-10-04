"""Single entrypoint.

    uv run --directory week2 gmail-mcp         # start the MCP server (stdio)
    uv run --directory week2 gmail-mcp auth    # one-time browser sign-in
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv


def main() -> None:
    # Load week2/.env if present; env vars passed by the MCP client take precedence.
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

    parser = argparse.ArgumentParser(prog="gmail-mcp")
    parser.add_argument("command", nargs="?", choices=["serve", "auth"], default="serve")
    args = parser.parse_args()

    if args.command == "auth":
        from .auth import run_login

        path = run_login()
        print(f"Signed in. Token cached at {path}", file=sys.stderr)
        return

    from .server import mcp

    mcp.run(transport="stdio", show_banner=False)


if __name__ == "__main__":
    main()
