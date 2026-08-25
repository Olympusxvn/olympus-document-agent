"""One-time OAuth for the dedicated Gmail inbox. Prints a refresh token."""

from __future__ import annotations

import os

from google_auth_oauthlib.flow import InstalledAppFlow

from ingest.gmail_api import GMAIL_SCOPES


def main() -> None:
    client_id = os.environ["GMAIL_CLIENT_ID"]
    client_secret = os.environ["GMAIL_CLIENT_SECRET"]
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, GMAIL_SCOPES)
    creds = flow.run_local_server(port=0)
    if not creds.refresh_token:
        raise SystemExit("No refresh token. Remove prior grant and retry with prompt=consent.")
    print(creds.refresh_token)


if __name__ == "__main__":
    main()
