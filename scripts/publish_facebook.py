"""Publish one MP4 to the owner-authorized Facebook Page after explicit confirmation."""
from __future__ import annotations
import json, os, sys
from pathlib import Path

def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: publish_facebook.py VIDEO.mp4 publishing_package.json")
    if os.getenv("FACEBOOK_PUBLISH_CONFIRMATION") != "I_APPROVE_FACEBOOK_PAGE_PUBLICATION":
        raise SystemExit("Missing explicit Facebook Page publication confirmation; refusing upload.")

    video = Path(sys.argv[1])
    package_path = Path(sys.argv[2])
    if not video.is_file() or video.stat().st_size == 0 or video.suffix.lower() != ".mp4":
        raise SystemExit(f"Video is missing, empty, or not an MP4: {video}")
    meta = json.loads(package_path.read_text(encoding="utf-8"))
    if not isinstance(meta.get("title"), str) or not meta["title"].strip():
        raise SystemExit("Publishing package is missing a title.")
    if not isinstance(meta.get("description"), str) or not meta["description"].strip():
        raise SystemExit("Publishing package is missing a description.")
    if meta.get("approval", {}).get("required") is not True:
        raise SystemExit("Publishing package does not require human approval; refusing upload.")
    if meta.get("automatic_publish") is not False:
        raise SystemExit("Automatic publishing must remain disabled; refusing upload.")
    if meta.get("owner_controlled") is not True:
        raise SystemExit("Publishing package is not owner-controlled; refusing upload.")
    if "facebook" not in meta.get("destinations", []):
        raise SystemExit("Facebook is not an approved destination for this package.")

    page_id = os.environ["FACEBOOK_PAGE_ID"]
    token = os.environ["FACEBOOK_PAGE_ACCESS_TOKEN"]
    version = os.getenv("FACEBOOK_GRAPH_VERSION", "v26.0")
    url = f"https://graph.facebook.com/{version}/{page_id}/videos"
    import requests

    with video.open("rb") as fh:
        response = requests.post(url, data={"access_token":token,"title":meta["title"],"description":meta["description"]}, files={"source":(video.name,fh,"video/mp4")}, timeout=300)
    response.raise_for_status()
    data = response.json()
    video_id = data.get("id")
    if not video_id:
        raise SystemExit("Facebook response did not include a video ID; inspect the Page before retrying.")
    print(json.dumps({"destination":"facebook","status":"published","video_id":video_id}, ensure_ascii=False))
    return 0

if __name__ == "__main__": raise SystemExit(main())
