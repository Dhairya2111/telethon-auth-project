"""
config.py — Load Telegram API credentials from a .env file or prompt the user.

Environment variables used (all optional — will be prompted if missing):
    TG_API_ID     : Your Telegram API ID (integer)
    TG_API_HASH   : Your Telegram API hash (string)
    TG_PHONE      : Your phone number in international format, e.g. +919876543210
"""

import os

from dotenv import load_dotenv

# Load variables from a .env file if one exists in the working directory.
# If no .env file is found, this call is a no-op.
load_dotenv()


def _prompt(env_key: str, label: str, secret: bool = False) -> str:
    """Return the value of *env_key* from the environment, or ask the user."""
    value = os.getenv(env_key, "").strip()
    if value:
        return value

    # Fall back to an interactive prompt.
    if secret:
        import getpass
        value = getpass.getpass(f"{label}: ").strip()
    else:
        value = input(f"{label}: ").strip()

    if not value:
        raise ValueError(f"{label} cannot be empty.")
    return value


def load_config() -> dict:
    """
    Return a dict with keys: api_id (int), api_hash (str), phone (str).

    Values are sourced from (in order of priority):
      1. Environment variables / .env file
      2. Interactive terminal prompts
    """
    print("\n--- Telegram API credentials ---")
    print("(You can set TG_API_ID, TG_API_HASH, TG_PHONE in a .env file to skip these prompts.)\n")

    # --- API ID ---
    raw_api_id = _prompt("TG_API_ID", "API ID (from my.telegram.org)")
    try:
        api_id = int(raw_api_id)
    except ValueError:
        raise ValueError(f"API ID must be an integer, got: {raw_api_id!r}")

    # --- API Hash ---
    api_hash = _prompt("TG_API_HASH", "API Hash (from my.telegram.org)")
    if len(api_hash) != 32:  # Telegram API hashes are always 32 hex chars
        print(f"  ⚠  API hash looks unusual (expected 32 characters, got {len(api_hash)}). Continuing anyway.")

    # --- Phone number ---
    phone = _prompt("TG_PHONE", "Phone number (international format, e.g. +919876543210)")
    if not phone.startswith("+"):
        raise ValueError("Phone number must include the country code and start with '+', e.g. +919876543210")

    return {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone,
    }
