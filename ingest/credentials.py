from __future__ import annotations

import os

import google.auth
from google.auth.credentials import Credentials

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]


def gmail_credentials() -> Credentials:
    """ADC on Cloud Run (runtime service account). No OAuth client or refresh token.

    If GMAIL_ADDRESS is set and credentials support domain-wide delegation
    (service account), impersonate that mailbox.
    """
    credentials, _project = google.auth.default(scopes=GMAIL_SCOPES)
    subject = (os.environ.get("GMAIL_ADDRESS") or "").strip()
    if subject and hasattr(credentials, "with_subject"):
        credentials = credentials.with_subject(subject)
    return credentials
