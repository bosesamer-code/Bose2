"""Upload one MP4 to the owner-authorized YouTube channel."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: publish_youtube.py VIDEO.mp4 publishing_package.json")

    video = Path(sys.argv[1])
    package = Path(sys.argv[2])
    if not video.is_file() or video.stat().st_size == 0:
        raise SystemExit(f"Video file is missing or empty: {video}")

    meta = json.loads(package.read_text(encoding="utf-8"))
    title = meta.get("title")
    description = meta.get("description")
    if not isinstance(title, str) or not title.strip():
        raise SystemExit(f"Missing title in {package}")
    if not isinstance(description, str) or not description.strip():
        raise SystemExit(f"Missing description in {package}")

    client_id = os.environ["YOUTUBE_CLIENT_ID"]
    client_secret = os.environ["YOUTUBE_CLIENT_SECRET"]
    refresh_token = os.environ["YOUTUBE_REFRESH_TOKEN"]
    creds = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    youtube = build("youtube", "v3", credentials=creds)
    privacy_status = os.getenv("YOUTUBE_PRIVACY_STATUS", "unlisted")
    if privacy_status not in {"private", "unlisted", "public"}:
        raise SystemExit("YOUTUBE_PRIVACY_STATUS must be private, unlisted, or public")

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "defaultLanguage": "ar",
        },
        "status": {"privacyStatus": privacy_status},
    }
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=MediaFileUpload(str(video), mimetype="video/mp4", resumable=True),
    )
    response = request.execute()
    print(
        json.dumps(
            {
                "destination": "youtube",
                "status": "uploaded",
                "privacy_status": privacy_status,
                "video_id": response["id"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
