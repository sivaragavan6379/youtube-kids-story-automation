from __future__ import annotations
import json, os, sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

BASE_DIR = Path(__file__).resolve().parent.parent
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
]


def main():
    relative_path = os.getenv("VIDEO_PATH", "input/episode.mp4").strip()
    video_path = (BASE_DIR / relative_path).resolve()
    if BASE_DIR.resolve() not in video_path.parents:
        raise RuntimeError("VIDEO_PATH must point inside the repository workspace.")
    if not video_path.is_file() or video_path.stat().st_size == 0:
        raise FileNotFoundError(f"Missing or empty video: {relative_path}")

    token_info = json.loads(os.getenv("YOUTUBE_OAUTH_TOKEN_JSON", "").strip())
    credentials = Credentials.from_authorized_user_info(token_info, scopes=SCOPES)
    youtube = build("youtube", "v3", credentials=credentials, cache_discovery=False)

    title = os.getenv("YOUTUBE_TITLE", "Kathaikalam | Tamil Animated Story — One-Shot Test").strip()[:100]
    description = os.getenv(
        "YOUTUBE_DESCRIPTION",
        "Tamil animated story test clip created with the Kathaikalam production pipeline.",
    ).strip()
    tags = [t.strip() for t in os.getenv(
        "YOUTUBE_TAGS", "Kathaikalam,Tamil story,Tamil animation,kids story"
    ).split(",") if t.strip()][:500]
    privacy = os.getenv("YOUTUBE_PRIVACY_STATUS", "unlisted").strip().lower()
    if privacy not in {"private", "unlisted", "public"}:
        raise ValueError("Privacy must be private, unlisted, or public.")
    made_for_kids = os.getenv("YOUTUBE_MADE_FOR_KIDS", "true").strip().lower() in {
        "1", "true", "yes", "on"
    }
    body = {
        "snippet": {
            "title": title or "Kathaikalam Tamil Animated Story",
            "description": description,
            "tags": tags,
            "categoryId": "1",
            "defaultLanguage": "ta",
            "defaultAudioLanguage": "ta",
        },
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": made_for_kids},
    }
    media = MediaFileUpload(str(video_path), mimetype="video/mp4",
                            chunksize=8 * 1024 * 1024, resumable=True)
    try:
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Upload progress: {int(status.progress() * 100)}%")
        video_id = response.get("id")
        if not video_id:
            raise RuntimeError(f"YouTube returned no video ID: {response}")
        print("YOUTUBE_UPLOAD_SUCCESS")
        print(f"VIDEO_ID={video_id}")
        print(f"VIDEO_URL=https://www.youtube.com/watch?v={video_id}")
        print(f"PRIVACY_STATUS={privacy}")
        print(f"MADE_FOR_KIDS={made_for_kids}")
    except HttpError as error:
        print(f"YouTube API upload failed: {error}", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
