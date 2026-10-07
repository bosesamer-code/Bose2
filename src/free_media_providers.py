"""Zero-cost local media providers for the public factory."""

from __future__ import annotations

import math
import shutil
import struct
import subprocess
import wave
from pathlib import Path

from src.media_providers import MediaRequest, MediaResult


class FreeLocalAudioProvider:
    name = "free-local-audio"
    media_type = "audio"

    def generate(self, request: MediaRequest) -> MediaResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        output = request.output_dir / "voice.wav"
        if output.exists():
            return MediaResult(self.name, self.media_type, "completed", [str(output)])

        script = str(request.payload.get("script", "")).strip()
        espeak = shutil.which("espeak-ng") or shutil.which("espeak")
        if espeak and script:
            command = [
                espeak,
                "-v", "ar",
                "-s", "150",
                "-w", str(output),
                script,
            ]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
                return MediaResult(self.name, self.media_type, "completed", [str(output)])
            except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
                pass

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

    @staticmethod
    def _scene_rgb(scene_number: int, purpose: str) -> tuple[int, int, int]:
        palette = {
            "hook": (225, 190, 120),
            "lesson": (150, 190, 220),
            "application": (170, 205, 160),
            "cta": (210, 165, 205),
        }
        base = palette.get(purpose, (180, 180, 180))
        shift = (scene_number * 11) % 24
        return tuple(min(255, channel + shift) for channel in base)

    def generate(self, request: MediaRequest) -> MediaResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        scenes = list(request.payload.get("scene_plan", []))
        if not scenes:
            scenes = [{"scene": 1, "purpose": "lesson"}]

        artifacts = []
        width, height = 640, 360
        for scene in scenes:
            number = int(scene.get("scene", len(artifacts) + 1))
            purpose = str(scene.get("purpose", "lesson"))
            output = request.output_dir / f"scene_{number:03d}.ppm"
            if output.exists():
                artifacts.append(str(output))
                continue
            red, green, blue = self._scene_rgb(number, purpose)
            with output.open("wb") as fh:
                fh.write(f"P6\n{width} {height}\n255\n".encode())
                for y in range(height):
                    for x in range(width):
                        stripe = ((x // 40) + (y // 40) + number) % 2
                        factor = 0.82 if stripe else 1.0
                        fh.write(bytes((
                            int(red * factor),
                            int(green * factor),
                            int(blue * factor),
                        )))
            artifacts.append(str(output))
        return MediaResult(self.name, self.media_type, "completed", artifacts)


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
        images = list(request.payload.get("image_paths", []))
        audio = request.payload.get("audio_path")
        scenes = list(request.payload.get("scene_plan", []))
        if not ffmpeg:
            return MediaResult(self.name, self.media_type, "not_configured", [], "ffmpeg is not installed")
        if not images or not audio:
            return MediaResult(self.name, self.media_type, "waiting_for_inputs", [], "image_paths and audio_path are required")

        durations = [max(1, int(scene.get("duration_seconds", 1))) for scene in scenes]
        if len(durations) != len(images):
            durations = [max(1, int(request.payload.get("duration_seconds", 2))) // len(images)] * len(images)
        concat_file = request.output_dir / "scenes.txt"
        lines = []
        for image, duration in zip(images, durations):
            escaped = str(Path(image).resolve()).replace("'", "'\\''")
            lines.append(f"file '{escaped}'")
            lines.append(f"duration {duration}")
        lines.append(f"file '{str(Path(images[-1]).resolve()).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'")
        concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        duration = max(2, int(request.payload.get("duration_seconds", sum(durations))))
        command = [
            ffmpeg, "-y",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(audio),
            "-t", str(duration),
            "-vf", "fps=25,format=yuv420p",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-af", "apad",
            "-c:v", "libx264",
            "-c:a", "aac",
            str(output),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
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
