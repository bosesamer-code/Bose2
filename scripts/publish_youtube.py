"""Upload one MP4 only after verifying the authorized YouTube channel."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

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

    if os.getenv("YOUTUBE_UPLOAD_CONFIRMATION") != "UPLOAD_ONE_PRIVATE_TEST_VIDEO":
        raise SystemExit("Missing explicit one-video private-upload confirmation; refusing upload.")

    video = Path(sys.argv[1])
    package = Path(sys.argv[2])
    if not video.is_file() or video.stat().st_size == 0 or video.suffix.lower() != ".mp4":
        raise SystemExit(f"Video file is missing, empty, or not an MP4: {video}")

    try:
        meta = json.loads(package.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Publishing package cannot be read as JSON: {package} ({exc})")
    if not isinstance(meta, dict):
        raise SystemExit("Publishing package must be a JSON object.")
    approval = meta.get("approval")
    if not isinstance(approval, dict) or approval.get("required") is not True:
        raise SystemExit("Publishing package does not require human approval; refusing upload.")
    if meta.get("automatic_publish") is not False:
        raise SystemExit("Automatic publishing must remain disabled; refusing upload.")
    if meta.get("owner_controlled") is not True:
        raise SystemExit("Publishing package is not owner-controlled; refusing upload.")
    destinations = meta.get("destinations")
    if not isinstance(destinations, list) or "youtube" not in destinations:
        raise SystemExit("YouTube is not an approved destination for this package.")
    title = meta.get("title")
    description = meta.get("description")
    if not isinstance(title, str) or not title.strip():
        raise SystemExit(f"Missing title in {package}")
    if not isinstance(description, str) or not description.strip():
        raise SystemExit(f"Missing description in {package}")

    missing_credentials = [
        key for key in ("YOUTUBE_CLIENT_ID", "YOUTUBE_CLIENT_SECRET", "YOUTUBE_REFRESH_TOKEN")
        if not os.getenv(key, "").strip()
    ]
    if missing_credentials:
        raise SystemExit("Missing required YouTube credential environment variables: " + ", ".join(missing_credentials))

    # Import network client dependencies only after every local safety check passes.
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

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
    target_channel_id = verify_target_channel(youtube)

    # This project is configured for private-only uploads. Fail closed even if a workflow
    # accidentally passes "public" or "unlisted".
    privacy_status = os.getenv("YOUTUBE_PRIVACY_STATUS", "private").strip().lower()
    if privacy_status != "private":
        raise SystemExit("Safety guard: this project only permits YOUTUBE_PRIVACY_STATUS=private")

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
    uploaded_id = response.get("id")
    uploaded_channel_id = response.get("snippet", {}).get("channelId")
    uploaded_privacy = response.get("status", {}).get("privacyStatus")
    if not uploaded_id:
        raise SystemExit("YouTube upload response did not include a video ID; inspect upload status manually.")
    if uploaded_channel_id != target_channel_id:
        raise SystemExit(
            "Safety alert: YouTube response channel ID does not match the verified target channel. "
            "Do not retry blindly; inspect the video in YouTube Studio."
        )
    if uploaded_privacy != "private":
        raise SystemExit(
            f"Safety alert: YouTube did not confirm private visibility (reported {uploaded_privacy!r}). "
            "Inspect the video in YouTube Studio immediately."
        )
    print(json.dumps({
        "destination": "youtube",
        "status": "uploaded",
        "privacy_status": uploaded_privacy,
        "video_id": uploaded_id,
        "channel_id": uploaded_channel_id,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
