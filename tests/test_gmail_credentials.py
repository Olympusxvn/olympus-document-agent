from ingest.credentials import gmail_credentials


def test_gmail_credentials_use_adc_not_oauth_env(monkeypatch):
    captured = {}

    class FakeCreds:
        def with_subject(self, email: str):
            captured["subject"] = email
            return self

    def fake_default(*, scopes=None):
        captured["scopes"] = scopes
        return FakeCreds(), "olympus-vat-agent"

    monkeypatch.setattr("ingest.credentials.google.auth.default", fake_default)
    monkeypatch.setenv("GMAIL_ADDRESS", "vat@org.example")
    monkeypatch.delenv("GMAIL_CLIENT_ID", raising=False)
    monkeypatch.delenv("GMAIL_CLIENT_SECRET", raising=False)
    monkeypatch.delenv("GMAIL_REFRESH_TOKEN", raising=False)

    creds = gmail_credentials()
    assert captured["scopes"] == [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
        "https://www.googleapis.com/auth/spreadsheets",
    ]
    assert captured["subject"] == "vat@org.example"
    assert creds is not None
