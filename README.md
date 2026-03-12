# Telethon Authentication Demo

A beginner-friendly Python project that demonstrates how to authenticate with Telegram using the [Telethon](https://github.com/LonamiWebs/Telethon) library (MTProto API).

---

## Table of Contents

1. [What This Project Does](#what-this-project-does)
2. [Prerequisites](#prerequisites)
3. [Getting Your Telegram API Credentials](#getting-your-telegram-api-credentials)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Project](#running-the-project)
7. [How Telethon Session Files Work](#how-telethon-session-files-work)
8. [Handled Login Scenarios](#handled-login-scenarios)
9. [Telegram Rate Limits and Privacy Rules](#telegram-rate-limits-and-privacy-rules)
10. [Project Structure](#project-structure)

---

## What This Project Does

This project walks you through the complete Telegram login flow step by step:

1. Connects to Telegram's servers using the MTProto protocol via Telethon.
2. Sends a login code to your phone number.
3. Accepts the code you received and signs you in.
4. Handles Two-Factor Authentication (2FA) if enabled on your account.
5. Saves the session so future runs skip the login prompt.

It is intentionally simple and heavily commented so that beginners can follow along.

---

## Prerequisites

- Python **3.8** or newer
- A Telegram account (the phone number you will log in with)
- Telegram API credentials (see next section)

---

## Getting Your Telegram API Credentials

You need an **API ID** and an **API Hash** to use the Telegram API. These are free and tied to your Telegram account.

1. Open [https://my.telegram.org](https://my.telegram.org) in your browser.
2. Log in with your Telegram phone number.
3. Click **API development tools**.
4. Fill in the form (App title and Short name can be anything, e.g. `MyTestApp`).
5. Click **Create application**.
6. Copy your **App api_id** (a number) and **App api_hash** (a 32-character string).

> **Keep these credentials private.** Anyone with your API ID + Hash can make requests on behalf of your Telegram application.

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/Dhairya2111/telethon-auth-project.git
cd telethon-auth-project

# 2. Create a virtual environment (keeps dependencies isolated)
python -m venv venv

# 3. Activate the virtual environment
#    On Linux / macOS:
source venv/bin/activate
#    On Windows (Command Prompt):
venv\Scripts\activate.bat
#    On Windows (PowerShell):
venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

You can supply your credentials in two ways:

### Option A — `.env` file (recommended)

Create a file named `.env` in the project root (it is already in `.gitignore` so it will not be committed):

```env
TG_API_ID=12345678
TG_API_HASH=0123456789abcdef0123456789abcdef
TG_PHONE=+919876543210
```

Replace the values with your own credentials.

### Option B — Interactive prompts

If no `.env` file is present (or a variable is missing), the script will ask you to type the values at runtime.

---

## Running the Project

```bash
python -m src.main
```

The script will:
1. Load your credentials.
2. Explain the session file.
3. Connect to Telegram and send a login code to your phone.
4. Ask you to enter the code.
5. Handle 2FA if needed.
6. Print a clear success or error message.

---

## How Telethon Session Files Work

After a successful login, Telethon creates a file called `telegram_session.session` in the directory where you ran the script.

| What it is | A SQLite database containing your session token |
|---|---|
| What it does | Lets you skip the login flow on the next run |
| Where it is | Current working directory (`telegram_session.session`) |
| How to log out | Delete the file, or go to Telegram → Settings → Devices → Terminate session |

### ⚠ Security warnings

- **Never share** the `.session` file with anyone — it grants full access to your Telegram account.
- **Never commit** it to Git. The `.gitignore` in this project already excludes `*.session` files.
- **Store it safely** — treat it like a password or a private key.
- If you suspect a session has been compromised, revoke it immediately in the Telegram app:  
  **Settings → Privacy and Security → Active Sessions → Terminate all other sessions**.

---

## Handled Login Scenarios

| Scenario | How the code handles it |
|---|---|
| Code sent successfully | Prints a confirmation and waits for the code |
| Already logged in | Detects existing session and skips login |
| Invalid phone number | `PhoneNumberInvalidError` — friendly message with formatting hint |
| Phone not registered | `PhoneNumberUnoccupiedError` — tells user to create an account first |
| Two-Factor Authentication required | `SessionPasswordNeededError` — securely prompts for the 2FA password |
| Wrong / invalid code entered | `PhoneCodeInvalidError` — explains the mistake |
| Login code expired | `PhoneCodeExpiredError` — tells user to re-run and get a fresh code |
| Rate limiting | `FloodWaitError` — shows the exact number of seconds to wait |
| Invalid API credentials | `ApiIdInvalidError` — points to my.telegram.org |

---

## Telegram Rate Limits and Privacy Rules

### Rate limits (FloodWait)

Telegram enforces strict rate limits to prevent abuse. If you make too many requests in a short period, you will receive a `FloodWaitError` with a mandatory wait time (in seconds). Common triggers:

- Sending login codes too frequently (e.g. running the script repeatedly without waiting).
- Making a large number of API calls in a short window.

**Best practice:** Wait the full duration indicated in the error before retrying. Repeated violations can result in a temporary ban on the phone number.

### Privacy and ethical use

- **Personal use only:** These credentials are for your own Telegram account. Do not use them to access other people's data.
- **No scraping / spamming:** The Telegram Terms of Service prohibit scraping user data, sending unsolicited messages (spam), and automating actions that mimic abuse.
- **User accounts vs bots:** This project logs in as a *user* (not a bot). Bot tokens are separate and should be used via the `TelegramClient` with a bot token or via the official [Bot API](https://core.telegram.org/bots/api).
- **Respect other users' privacy:** Do not build tools that monitor, track, or harvest information about other Telegram users without their consent.

Violating Telegram's Terms of Service can result in your account or phone number being permanently banned.

---

## Project Structure

```
telethon-auth-project/
├── .env                  # Your credentials (NOT committed — excluded by .gitignore)
├── .gitignore            # Excludes .env, *.session, venv, __pycache__, etc.
├── README.md             # This file
├── requirements.txt      # Python dependencies
└── src/
    ├── __init__.py
    ├── main.py           # Entry point — run with: python -m src.main
    ├── auth_flow.py      # Core Telethon authentication logic
    ├── config.py         # Loads credentials from .env or prompts the user
    └── utils.py          # Helper functions for interactive prompts
```