"""
utils.py — Small helper utilities for interactive prompts.

These are kept separate so that auth_flow.py stays focused on Telegram
logic, and so that tests can easily substitute these helpers with mocks.
"""

import getpass


def prompt_login_code() -> str:
    """
    Ask the user to type the login code that Telegram sent to their device.

    Telegram sends a short numeric code (usually 5 digits) via:
      - The Telegram app on another logged-in device, OR
      - An SMS to the phone number (as a fallback).
    """
    print("\nTelegram has sent a login code to your phone/app.")
    code = input("Enter the login code: ").strip()
    if not code:
        raise ValueError("Login code cannot be empty.")
    return code


def prompt_2fa_password() -> str:
    """
    Securely prompt for the Two-Factor Authentication (2FA) password.

    Two-Factor Authentication (also called Cloud Password in Telegram) is an
    *optional* extra security layer that users can enable on their account.
    When enabled, every new login also requires this password.

    We use getpass so the password is not echoed to the terminal.
    """
    print("\nThis account has Two-Factor Authentication (2FA) enabled.")
    password = getpass.getpass("Enter your 2FA cloud password: ").strip()
    if not password:
        raise ValueError("2FA password cannot be empty.")
    return password
