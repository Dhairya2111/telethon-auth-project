"""
main.py — Entry point for the Telethon authentication demo.

Run with:
    python -m src.main

What this script does:
  1. Loads Telegram API credentials (from .env or interactive prompts).
  2. Explains where the Telethon .session file will be stored and why it matters.
  3. Delegates the actual authentication flow to src/auth_flow.py.
  4. Prints a clear result message.

SECURITY NOTE:
  The .session file that Telethon creates contains your active Telegram
  session token — treat it like a password.  Never commit it to version
  control.  The included .gitignore already excludes *.session files.
"""

import asyncio
import sys

from src.auth_flow import run_auth_flow
from src.config import load_config

# Name used as the prefix for the Telethon session file.
# Telethon will create '<SESSION_NAME>.session' in the current directory.
SESSION_NAME = "telegram_session"


def _print_banner() -> None:
    print("=" * 60)
    print("  Telethon Authentication Demo")
    print("  Educational project — beginner-friendly Telegram login")
    print("=" * 60)


def _print_session_info() -> None:
    """Explain session files to the user before authentication starts."""
    print(
        f"\n[INFO] About Telethon session files:\n"
        f"  Telethon stores your login session in a file called\n"
        f"  '{SESSION_NAME}.session' in the current directory.\n"
        f"\n"
        f"  This file works like a browser cookie — if it exists and\n"
        f"  is still valid, future runs will skip the login prompt entirely.\n"
        f"\n"
        f"  ⚠  IMPORTANT SECURITY WARNINGS:\n"
        f"     • Never share this file with anyone.\n"
        f"     • Never commit it to Git (the .gitignore already excludes it).\n"
        f"     • Delete the file to log out of this session.\n"
        f"     • If compromised, revoke the session in Telegram:\n"
        f"       Settings → Devices → Terminate session.\n"
    )


async def main() -> None:
    _print_banner()

    # Load credentials (from .env if available, otherwise prompt interactively).
    try:
        config = load_config()
    except ValueError as exc:
        print(f"\n[✗] Configuration error: {exc}")
        sys.exit(1)

    _print_session_info()

    # Run the authentication flow and capture the result message.
    result = await run_auth_flow(
        api_id=config["api_id"],
        api_hash=config["api_hash"],
        phone=config["phone"],
        session_name=SESSION_NAME,
    )

    # Print the final outcome — success or a friendly error explanation.
    print(f"\n{result}\n")


if __name__ == "__main__":
    asyncio.run(main())
