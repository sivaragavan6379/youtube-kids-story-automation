from pathlib import Path
import json, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "input" / "episode.mp4"
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
]


def main():
    file_id = os.getenv("GOOGLE_DRIVE_FILE_ID", "").strip()
    token_json = os.getenv("YOUTUBE_OAUTH_TOKEN_JSON", "").strip()
    if not file_id:
        raise RuntimeError("Missing workflow input GOOGLE_DRIVE_FILE_ID.")
    if not token_json:
        raise RuntimeError("Missing GitHub secret YOUTUBE_OAUTH_TOKEN_JSON.")
    credentials = Credentials.from_authorized_user_info(json.loads(token_json), scopes=SCOPES)
    drive = build("drive", "v3", credentials=credentials, cache_discovery=False)
    metadata = drive.files().get(
        fileId=file_id, fields="id,name,mimeType,size,capabilities(canDownload)"
    ).execute()
    if metadata.get("mimeType") != "video/mp4":
        raise RuntimeError(f"Drive file must be MP4; found {metadata.get('mimeType')}.")
    if metadata.get("capabilities", {}).get("canDownload") is False:
        raise RuntimeError("The OAuth Google account cannot download this Drive file.")
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    request = drive.files().get_media(fileId=file_id)
    with OUTPUT_PATH.open("wb") as output:
        downloader = MediaIoBaseDownload(output, request, chunksize=8 * 1024 * 1024)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            if status:
                print(f"Drive download progress: {int(status.progress() * 100)}%")
    if not OUTPUT_PATH.is_file() or OUTPUT_PATH.stat().st_size == 0:
        raise RuntimeError("Drive download produced an empty MP4.")
    print(f"Downloaded {metadata.get('name')} ({OUTPUT_PATH.stat().st_size} bytes).")


if __name__ == "__main__":
    main()
