"""Publish one MP4 to the owner-authorized Facebook Page."""
from __future__ import annotations
import json, os, sys
from pathlib import Path
import requests

def main() -> int:
    video = Path(sys.argv[1]); meta = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    page_id = os.environ["FACEBOOK_PAGE_ID"]
    token = os.environ["FACEBOOK_PAGE_ACCESS_TOKEN"]
    version = os.getenv("FACEBOOK_GRAPH_VERSION", "v26.0")
    url = f"https://graph.facebook.com/{version}/{page_id}/videos"
    with video.open("rb") as fh:
        response = requests.post(url, data={"access_token":token,"title":meta["title"],"description":meta["description"]}, files={"source":(video.name,fh,"video/mp4")}, timeout=300)
    response.raise_for_status()
    data = response.json()
    print(json.dumps({"destination":"facebook","status":"published","video_id":data.get("id")}, ensure_ascii=False))
    return 0

if __name__ == "__main__": raise SystemExit(main())
