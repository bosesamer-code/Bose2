"""Upload one MP4 only after verifying the authorized YouTube channel."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Read access is required for the fail-closed channel identity preflight.
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def verify_target_channel(youtube) -> str:
    expected_handle = os.environ.get("YOUTUBE_EXPECTED_CHANNEL_HANDLE", "").strip().lstrip("@")
    if not expected_handle:
        raise SystemExit("Missing YOUTUBE_EXPECTED_CHANNEL_HANDLE; refusing upload.")

    target_response = youtube.channels().list(
        part="id,snippet",
        forHandle=expected_handle,
    ).execute()
    targets = target_response.get("items", [])
    if len(targets) != 1:
        raise SystemExit(
            f"Could not uniquely resolve target handle @{expected_handle}; refusing upload."
        )
    target = targets[0]
    target_id = target.get("id")
    if not target_id:
        raise SystemExit("Target channel lookup returned no channel ID; refusing upload.")

    mine_response = youtube.channels().list(part="id,snippet", mine=True, maxResults=50).execute()
    mine = mine_response.get("items", [])
    # Do not guess which of multiple channels an upload token will publish to.
    if len(mine) != 1:
        raise SystemExit(
            "OAuth identity returned zero or multiple YouTube channels. "
            "Re-authorize using the intended channel, then retry; refusing upload."
        )
    authorized_id = mine[0].get("id")
    if authorized_id != target_id:
        authorized_title = mine[0].get("snippet", {}).get("title", "(unknown)")
        raise SystemExit(
            f"Wrong YouTube channel connected: '{authorized_title}'. "
            f"Expected @{expected_handle} ({target_id}); refusing upload."
        )
    print(json.dumps({
        "destination": "youtube",
        "channel_verified": True,
        "channel_handle": f"@{expected_handle}",
        "channel_id": target_id,
    }, ensure_ascii=False))
    return target_id


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
    verify_target_channel(youtube)

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
    print(json.dumps({
        "destination": "youtube",
        "status": "uploaded",
        "privacy_status": privacy_status,
        "video_id": response["id"],
        "channel_id": response.get("snippet", {}).get("channelId"),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
