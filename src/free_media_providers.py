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
            command = [espeak, "-v", "ar", "-s", "150", "-w", str(output), script]
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
    """Create deterministic educational diagrams from scene purpose and text."""

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

    @staticmethod
    def _fill_rect(buf: bytearray, width: int, height: int, x0: int, y0: int, x1: int, y1: int, rgb: tuple[int, int, int]) -> None:
        x0, x1 = max(0, x0), min(width, x1)
        y0, y1 = max(0, y0), min(height, y1)
        row = bytes(rgb) * max(0, x1 - x0)
        for y in range(y0, y1):
            start = (y * width + x0) * 3
            buf[start:start + len(row)] = row

    @classmethod
    def _draw_visual(cls, width: int, height: int, scene_number: int, purpose: str, scene: dict) -> bytes:
        red, green, blue = cls._scene_rgb(scene_number, purpose)
        bg = bytearray(bytes((red, green, blue)) * (width * height))
        dark = (max(25, red - 85), max(25, green - 85), max(25, blue - 85))
        light = (min(255, red + 30), min(255, green + 30), min(255, blue + 30))
        text = str(scene.get("text", "")).lower()

        cls._fill_rect(bg, width, height, 0, 0, width, 42, dark)

        if purpose == "hook":
            # A focal card for the idea being introduced.
            cls._fill_rect(bg, width, height, 150, 85, 490, 275, light)
            cls._fill_rect(bg, width, height, 205, 125, 435, 235, dark)
            cls._fill_rect(bg, width, height, 235, 155, 405, 205, light)
        elif purpose == "lesson":
            # "steps / خَطوات / خطوات / ابدئي / قسمي" -> a numbered process.
            step_words = ("step", "steps", "خطوة", "خطوات", "ابدئي", "قسمي", "أول", "ثاني", "ثالث")
            count = 4 if any(word in text for word in step_words) else 3
            gap = 18
            block_w = (width - 2 * 55 - (count - 1) * gap) // count
            for i in range(count):
                x = 55 + i * (block_w + gap)
                cls._fill_rect(bg, width, height, x, 105, x + block_w, 230, light)
                cls._fill_rect(bg, width, height, x + 12, 122, x + block_w - 12, 142, dark)
                if i < count - 1:
                    cls._fill_rect(bg, width, height, x + block_w, 157, x + block_w + gap, 178, dark)
        elif purpose == "application":
            # "review / improve / model" -> review loop; otherwise checklist.
            review_words = ("راجع", "راجعي", "تعديل", "تحسين", "حسن", "النموذج", "improv", "review")
            if any(word in text for word in review_words):
                cls._fill_rect(bg, width, height, 120, 105, 520, 235, light)
                cls._fill_rect(bg, width, height, 170, 140, 470, 165, dark)
                cls._fill_rect(bg, width, height, 170, 178, 405, 203, dark)
                cls._fill_rect(bg, width, height, 410, 178, 470, 203, light)
            else:
                for i in range(3):
                    y = 92 + i * 72
                    cls._fill_rect(bg, width, height, 120, y, 155, y + 35, light)
                    cls._fill_rect(bg, width, height, 175, y + 7, 500, y + 28, dark)
        elif purpose == "cta":
            # Forward arrow = continue to the next lesson/action.
            cls._fill_rect(bg, width, height, 120, 145, 445, 205, light)
            for i in range(7):
                cls._fill_rect(bg, width, height, 420 + i * 18, 112 + i * 10, 438 + i * 18, 238 - i * 10, light)
        else:
            cls._fill_rect(bg, width, height, 150, 100, 490, 260, light)

        # Scene number marker makes sequence/order explicit.
        cls._fill_rect(bg, width, height, 24, 55, 92, 123, dark)
        return bytes(bg)

    def generate(self, request: MediaRequest) -> MediaResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        scenes = list(request.payload.get("scene_plan", []))
        if not scenes:
            scenes = [{"scene": 1, "purpose": "lesson", "text": ""}]

        artifacts = []
        width, height = 640, 360
        for scene in scenes:
            number = int(scene.get("scene", len(artifacts) + 1))
            purpose = str(scene.get("purpose", "lesson"))
            output = request.output_dir / f"scene_{number:03d}.ppm"
            if output.exists():
                artifacts.append(str(output))
                continue
            pixels = self._draw_visual(width, height, number, purpose, scene)
            with output.open("wb") as fh:
                fh.write(f"P6\n{width} {height}\n255\n".encode())
                fh.write(pixels)
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
            ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(audio), "-t", str(duration), "-vf", "fps=25,format=yuv420p",
            "-map", "0:v:0", "-map", "1:a:0", "-af", "apad", "-c:v", "libx264", "-c:a", "aac",
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
