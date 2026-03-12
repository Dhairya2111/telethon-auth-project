"""
auth_flow.py — Core Telegram authentication logic using Telethon.

How Telegram MTProto authentication works (high level):
  1. The client connects to Telegram's servers using the MTProto protocol.
  2. We call send_code_request() with the user's phone number.
     Telegram sends a short numeric code to an already-logged-in Telegram app
     (or via SMS as a fallback).
  3. We call sign_in() with the phone number + the code the user received.
     - If the account has 2FA (a "cloud password") enabled, Telegram raises
       SessionPasswordNeededError — we then call sign_in() again with the
       password instead of the code.
  4. On success Telethon writes a .session file so that future runs skip the
     login flow entirely (the session acts like a cookie).
"""

import asyncio

from telethon import TelegramClient
from telethon.errors import (
    ApiIdInvalidError,
    FloodWaitError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberBannedError,
    PhoneNumberInvalidError,
    PhoneNumberUnoccupiedError,
    SessionPasswordNeededError,
)

from src.utils import prompt_2fa_password, prompt_login_code


async def run_auth_flow(api_id: int, api_hash: str, phone: str, session_name: str = "telegram_session") -> str:
    """
    Attempt to authenticate with Telegram and return a status message.

    Parameters
    ----------
    api_id : int
        Your Telegram application API ID (from my.telegram.org).
    api_hash : str
        Your Telegram application API hash (from my.telegram.org).
    phone : str
        The phone number to log in with, in international format (+XXXXXXXXXXX).
    session_name : str
        Base name for the Telethon .session file (stored in the current directory).

    Returns
    -------
    str
        A human-readable message describing the final outcome.
    """

    # TelegramClient manages the connection and the persistent session file.
    # The session_name is the filename prefix — Telethon appends '.session'.
    print(f"\n[+] Connecting to Telegram (session file: {session_name}.session) …")
    client = TelegramClient(session_name, api_id, api_hash)

    try:
        await client.connect()

        # --- Check if we are already logged in (session file exists and is valid) ---
        if await client.is_user_authorized():
            me = await client.get_me()
            return (
                f"[✓] Already logged in as {me.first_name} "
                f"(username: @{me.username}, id: {me.id}).\n"
                "    No new authentication was needed — existing session reused."
            )

        # --- Step 1: Request a login code from Telegram ---
        print(f"[+] Sending login code to {phone} …")
        try:
            sent = await client.send_code_request(phone)
        except PhoneNumberInvalidError:
            return (
                "[✗] Invalid phone number.\n"
                "    Make sure you include the country code, e.g. +919876543210."
            )
        except PhoneNumberBannedError:
            return (
                "[✗] This phone number has been banned by Telegram.\n"
                "    If you believe this is a mistake, contact Telegram support."
            )
        except ApiIdInvalidError:
            return (
                "[✗] The API ID / API Hash combination is invalid.\n"
                "    Double-check the values at https://my.telegram.org."
            )
        except FloodWaitError as exc:
            return (
                f"[✗] Telegram rate-limit hit (FloodWait).\n"
                f"    You must wait {exc.seconds} seconds before trying again.\n"
                "    This happens when too many requests are made in a short time."
            )

        print(f"[✓] Code sent! Check your Telegram app (or SMS) for the login code.")

        # --- Step 2: Ask the user for the code and attempt sign-in ---
        code = prompt_login_code()

        try:
            await client.sign_in(phone, code, phone_code_hash=sent.phone_code_hash)

        except PhoneNumberUnoccupiedError:
            # The phone number is valid but has no Telegram account.
            return (
                "[✗] This phone number is not registered on Telegram.\n"
                "    You must create a Telegram account first (via the official app)."
            )

        except PhoneCodeInvalidError:
            return (
                "[✗] The login code you entered is incorrect.\n"
                "    Please check the code and try again."
            )

        except PhoneCodeExpiredError:
            return (
                "[✗] The login code has expired.\n"
                "    Telegram codes are valid for a limited time.\n"
                "    Re-run the script to request a new code."
            )

        except SessionPasswordNeededError:
            # --- Step 3 (conditional): Handle Two-Factor Authentication ---
            # This exception means the account has 2FA (a "cloud password") enabled.
            # We must now supply the password to complete the login.
            print("[!] Two-Factor Authentication is enabled on this account.")
            password = prompt_2fa_password()

            try:
                await client.sign_in(password=password)
            except PasswordHashInvalidError:
                return (
                    "[✗] The 2FA password you entered is incorrect.\n"
                    "    Please check your cloud password and try again."
                )
            except Exception as exc:
                return f"[✗] 2FA sign-in failed: {str(exc)}"

        except FloodWaitError as exc:
            return (
                f"[✗] Telegram rate-limit hit during sign-in (FloodWait).\n"
                f"    Please wait {exc.seconds} seconds before trying again."
            )

        # --- Login successful ---
        me = await client.get_me()
        return (
            f"[✓] Successfully logged in as {me.first_name} "
            f"(username: @{me.username}, id: {me.id}).\n"
            f"    Session saved to '{session_name}.session' — keep this file private!"
        )

    finally:
        # Always disconnect cleanly so sockets are released.
        await client.disconnect()
