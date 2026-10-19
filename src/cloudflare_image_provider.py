"""Cloudflare Workers AI image generation, guarded by explicit opt-in."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from src.media_providers import MediaRequest, MediaResult


class CloudflareWorkersAIImageProvider:
    """Generate scene images through Workers AI without exposing credentials."""

    name = "cloudflare-workers-ai-sdxl"
    media_type = "image"
    model = "@cf/stabilityai/stable-diffusion-xl-base-1.0"

    def __init__(self, token: str | None = None, account_id: str | None = None) -> None:
        self.token = (token if token is not None else os.getenv("CLOUDFLARE_API_TOKEN", "")).strip()
        self.account_id = (account_id if account_id is not None else os.getenv("CLOUDFLARE_ACCOUNT_ID", "")).strip()

    def generate(self, request: MediaRequest) -> MediaResult:
        if not self.token or not self.account_id:
            return MediaResult(self.name, self.media_type, "not_configured", [],
                               "Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID in the runtime secrets.")
        scenes = request.payload.get("scene_plan") or [{"scene": 1, "purpose": "lesson", "text": "Crochet lesson"}]
        if not isinstance(scenes, list) or not scenes:
            return MediaResult(self.name, self.media_type, "failed", [], "scene_plan must be a non-empty list.")
        # A hard per-job cap prevents accidental high-volume calls and protects the free quota.
        max_images = max(1, min(8, int(os.getenv("CLOUDFLARE_MAX_IMAGES_PER_JOB", "4"))))
        if len(scenes) > max_images:
            return MediaResult(
                self.name, self.media_type, "not_configured", [],
                f"Scene count ({len(scenes)}) exceeds the safety cap ({max_images}); no requests were sent.",
            )

        request.output_dir.mkdir(parents=True, exist_ok=True)
        artifacts: list[str] = []
        for index, scene in enumerate(scenes, start=1):
            purpose = str(scene.get("purpose", "lesson")).strip()
            scene_text = " ".join(str(scene.get("text", "")).split())
            prompt = (
                "High quality educational crochet tutorial still frame, realistic yarn fibers, "
                "crochet hook and hands clearly visible when relevant, soft studio lighting, "
                "clean uncluttered craft table, no words, no letters, no watermark. "
                f"Scene purpose: {purpose}. Lesson details: {scene_text or 'show crochet materials and technique'}."
            )
            url = (
                "https://api.cloudflare.com/client/v4/accounts/"
                + self.account_id
                + "/ai/run/"
                + self.model
            )
            body = json.dumps({"prompt": prompt, "width": 1024, "height": 1024}).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Authorization": "Bearer " + self.token,
                    "Content-Type": "application/json",
                    "Accept": "image/png",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=90) as response:
                    image_bytes = response.read()
                    content_type = response.headers.get("Content-Type", "").lower()
            except urllib.error.HTTPError as exc:
                # Never include response headers or request data, which could contain sensitive details.
                return MediaResult(
                    self.name, self.media_type, "failed", artifacts,
                    f"Cloudflare image request failed with HTTP {exc.code}; check token permissions, account ID, model access, and free quota.",
                )
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                return MediaResult(
                    self.name, self.media_type, "failed", artifacts,
                    f"Cloudflare image request failed ({type(exc).__name__}); check connectivity and try again.",
                )

            if not image_bytes or not (image_bytes.startswith(b"\x89PNG\r\n\x1a\n") or "image/" in content_type):
                return MediaResult(
                    self.name, self.media_type, "failed", artifacts,
                    "Cloudflare returned a non-image response; image was rejected and not saved.",
                )
            output = request.output_dir / f"scene_{index:03d}.png"
            output.write_bytes(image_bytes)
            artifacts.append(str(output))

        return MediaResult(self.name, self.media_type, "completed", artifacts)
