"""Upload one MP4 to the owner-authorized YouTube channel."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main() -> int:
    video = Path(sys.argv[1]); meta = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    client_id = os.environ["YOUTUBE_CLIENT_ID"]
    client_secret = os.environ["YOUTUBE_CLIENT_SECRET"]
    refresh_token = os.environ["YOUTUBE_REFRESH_TOKEN"]
    creds = Credentials(None, refresh_token=refresh_token, token_uri="https://oauth2.googleapis.com/token", client_id=client_id, client_secret=client_secret, scopes=SCOPES)
    youtube = build("youtube", "v3", credentials=creds)
    body = {"snippet": {"title": meta["title"], "description": meta["description"], "defaultLanguage": "ar"}, "status": {"privacyStatus": os.getenv("YOUTUBE_PRIVACY_STATUS", "public")}}
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(str(video), mimetype="video/mp4", resumable=True))
    response = request.execute()
    print(json.dumps({"destination":"youtube","status":"published","video_id":response["id"]}, ensure_ascii=False))
    return 0

if __name__ == "__main__": raise SystemExit(main())
