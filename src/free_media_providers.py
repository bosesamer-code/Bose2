"""Zero-cost local media providers for the public factory."""

from __future__ import annotations

import math
import shutil
import struct
import subprocess
import wave
from pathlib import Path
from typing import Any

from src.media_providers import MediaRequest, MediaResult


class FreeLocalAudioProvider:
    name = "free-local-audio"
    media_type = "audio"

    def generate(self, request: MediaRequest) -> MediaResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        output = request.output_dir / "voice.wav"
        if output.exists():
            return MediaResult(self.name, self.media_type, "completed", [str(output)])
        sample_rate = 16000
        duration = max(2, int(request.payload.get("duration_seconds", 2)))
        frames = bytearray()
        for i in range(sample_rate * duration):
            sample = int(1200 * math.sin(2 * math.pi * 440 * i / sample_rate))
            frames.extend(struct.pack("<h", sample))
        with wave.open(str(output), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(frames)
        return MediaResult(self.name, self.media_type, "completed", [str(output)])


class FreeLocalImageProvider:
    name = "free-local-image"
    media_type = "image"

    def generate(self, request: MediaRequest) -> MediaResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        output = request.output_dir / "scene.ppm"
        if output.exists():
            return MediaResult(self.name, self.media_type, "completed", [str(output)])
        width, height = 640, 360
        with output.open("wb") as fh:
            fh.write(f"P6\n{width} {height}\n255\n".encode())
            for y in range(height):
                for x in range(width):
                    value = (x + y) % 256
                    fh.write(bytes((value, value, value)))
        return MediaResult(self.name, self.media_type, "completed", [str(output)])


class FreeLocalDesignProvider(FreeLocalImageProvider):
    name = "free-local-design"
    media_type = "design"


class FreeLocalThumbnailProvider(FreeLocalImageProvider):
    name = "free-local-thumbnail"
    media_type = "thumbnail"


class FreeLocalVideoProvider:
    name = "free-local-video"
    media_type = "video"

    def generate(self, request: MediaRequest) -> MediaResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        output = request.output_dir / "video.mp4"
        if output.exists():
            return MediaResult(self.name, self.media_type, "completed", [str(output)])
        ffmpeg = shutil.which("ffmpeg")
        image = request.payload.get("image_path")
        audio = request.payload.get("audio_path")
        if not ffmpeg:
            return MediaResult(self.name, self.media_type, "not_configured", [], "ffmpeg is not installed")
        if not image or not audio:
            return MediaResult(self.name, self.media_type, "waiting_for_inputs", [], "image_path and audio_path are required")
        duration = max(2, int(request.payload.get("duration_seconds", 2)))
        command = [ffmpeg, "-y", "-loop", "1", "-i", str(image), "-i", str(audio), "-t", str(duration), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(output)]
        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            return MediaResult(self.name, self.media_type, "failed", [], "ffmpeg timed out after 30 seconds")
        except (OSError, subprocess.CalledProcessError) as exc:
            return MediaResult(self.name, self.media_type, "failed", [], str(exc))
        return MediaResult(self.name, self.media_type, "completed", [str(output)])


def free_local_registry():
    from src.media_providers import ProviderRegistry
    registry = ProviderRegistry()
    registry.register(FreeLocalAudioProvider())
    registry.register(FreeLocalImageProvider())
    registry.register(FreeLocalDesignProvider())
    registry.register(FreeLocalVideoProvider())
    registry.register(FreeLocalThumbnailProvider())
    return registry
