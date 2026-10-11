from __future__ import annotations

import json
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = Path(__file__).resolve().parent.parent
CLIENT_SECRETS = BASE_DIR / "client_secrets.json"
OUTPUT_TOKEN = BASE_DIR / "youtube_token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> None:
    if not CLIENT_SECRETS.is_file():
        raise FileNotFoundError(
            "Place your downloaded Google OAuth Desktop client JSON at "
            f"{CLIENT_SECRETS}. Never commit this file to GitHub."
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRETS),
        scopes=SCOPES,
    )
    credentials = flow.run_local_server(
        host="localhost",
        port=0,
        access_type="offline",
        prompt="consent",
    )

    OUTPUT_TOKEN.write_text(credentials.to_json(), encoding="utf-8")
    print(f"OAuth token saved locally to: {OUTPUT_TOKEN}")
    print("Open youtube_token.json and copy its FULL JSON contents.")
    print("Add those contents as the GitHub Actions secret:")
    print("YOUTUBE_OAUTH_TOKEN_JSON")
    print("Never commit or share youtube_token.json.")


if __name__ == "__main__":
    main()
