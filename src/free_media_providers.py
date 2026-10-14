"""Zero-cost local media providers for the public factory."""

from __future__ import annotations

import math
import shutil
import struct
import subprocess
import textwrap
import wave
from pathlib import Path

from src.media_providers import MediaRequest, MediaResult


def _wrap_subtitle_text(text: str, width: int = 34) -> str:
    """Wrap Arabic captions into readable lines for a 1920x1080 master."""
    normalized = " ".join(str(text).split())
    if not normalized:
        return ""
    return "\n".join(
        textwrap.wrap(normalized, width=max(12, width), break_long_words=False, break_on_hyphens=False)
    )


class FreeLocalAudioProvider:
    """Generate real Egyptian Arabic speech; never substitute a tone for narration."""

    name = "free-edge-tts-ar-eg"
    media_type = "audio"

    def generate(self, request: MediaRequest) -> MediaResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        output = request.output_dir / "voice.mp3"
        script = str(request.payload.get("script", "")).strip()
        if not script:
            return MediaResult(self.name, self.media_type, "failed", [], "Arabic narration script is empty")

        edge_tts = shutil.which("edge-tts")
        if not edge_tts:
            return MediaResult(
                self.name, self.media_type, "not_configured", [],
                "edge-tts is not installed; refusing to create fake/silent narration",
            )

        command = [
            edge_tts, "--voice", "ar-EG-SalmaNeural",
            "--rate", "+0%", "--text", script, "--write-media", str(output),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=90)
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            output.unlink(missing_ok=True)
            return MediaResult(self.name, self.media_type, "failed", [], f"Egyptian Arabic TTS failed: {exc}")

        if not output.is_file() or output.stat().st_size < 1024:
            output.unlink(missing_ok=True)
            return MediaResult(self.name, self.media_type, "failed", [], "TTS output is missing or too small")
        return MediaResult(self.name, self.media_type, "completed", [str(output)])


class FreeLocalImageProvider:
    """Create deterministic educational diagrams from scene purpose and text."""

    name = "free-local-image"
    media_type = "image"

    @staticmethod
    def _fill_rect(buf: bytearray, width: int, height: int, x0: int, y0: int, x1: int, y1: int, rgb: tuple[int, int, int]) -> None:
        x0, x1 = max(0, x0), min(width, x1)
        y0, y1 = max(0, y0), min(height, y1)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(rgb) * (x1 - x0)
        for y in range(y0, y1):
            start = (y * width + x0) * 3
            buf[start:start + len(row)] = row

    @classmethod
    def _circle(cls, buf: bytearray, width: int, height: int, cx: int, cy: int, radius: int, rgb: tuple[int, int, int]) -> None:
        r2 = radius * radius
        for y in range(max(0, cy-radius), min(height, cy+radius+1)):
            span = int(max(0, r2 - (y-cy)*(y-cy)) ** 0.5)
            cls._fill_rect(buf, width, height, cx-span, y, cx+span+1, y+1, rgb)

    @classmethod
    def _line(cls, buf: bytearray, width: int, height: int, x0: int, y0: int, x1: int, y1: int, rgb: tuple[int, int, int], thickness: int = 4) -> None:
        steps = max(abs(x1-x0), abs(y1-y0), 1)
        for step in range(steps + 1):
            x = int(x0 + (x1-x0) * step / steps)
            y = int(y0 + (y1-y0) * step / steps)
            cls._circle(buf, width, height, x, y, thickness, rgb)

    @classmethod
    def _avatar(cls, buf: bytearray, width: int, height: int) -> None:
        """A consistent friendly illustrated host, repeated in every scene."""
        skin = (235, 177, 139)
        hair = (65, 43, 36)
        shirt = (112, 72, 133)
        outline = (65, 43, 52)
        cls._fill_rect(buf, width, height, 55, 220, 190, 335, shirt)
        cls._circle(buf, width, height, 122, 158, 65, hair)
        cls._circle(buf, width, height, 122, 166, 48, skin)
        cls._circle(buf, width, height, 91, 130, 27, hair)
        cls._circle(buf, width, height, 151, 132, 26, hair)
        cls._fill_rect(buf, width, height, 73, 124, 170, 145, hair)
        cls._line(buf, width, height, 91, 156, 104, 156, outline, 3)
        cls._line(buf, width, height, 139, 156, 152, 156, outline, 3)
        cls._line(buf, width, height, 104, 183, 122, 190, (155, 65, 68), 3)
        cls._line(buf, width, height, 122, 190, 140, 183, (155, 65, 68), 3)
        cls._fill_rect(buf, width, height, 104, 222, 140, 244, (246, 230, 218))

    @classmethod
    def _yarn_and_crochet(cls, buf: bytearray, width: int, height: int, variant: int) -> None:
        yarns = [(205, 91, 116), (74, 139, 157), (224, 167, 77)]
        yarn = yarns[variant % len(yarns)]
        cream = (250, 240, 219)
        dark = (85, 65, 60)
        cls._circle(buf, width, height, 390, 210, 70, yarn)
        cls._line(buf, width, height, 335, 190, 435, 240, cream, 5)
        cls._line(buf, width, height, 340, 235, 430, 175, cream, 5)
        cls._line(buf, width, height, 355, 160, 415, 258, cream, 4)
        cls._line(buf, width, height, 350, 255, 430, 165, cream, 4)
        cls._line(buf, width, height, 455, 120, 530, 265, dark, 5)
        cls._circle(buf, width, height, 454, 119, 7, (236, 196, 126))
        cls._fill_rect(buf, width, height, 300, 285, 505, 326, (235, 211, 173))
        for y in (292, 303, 314):
            for x in range(307, 500, 20):
                cls._circle(buf, width, height, x, y, 5, yarn)

    @classmethod
    def _draw_visual(cls, width: int, height: int, scene_number: int, purpose: str, scene: dict) -> bytes:
        palettes = {
            "hook": (255, 244, 226),
            "lesson": (238, 247, 242),
            "application": (246, 239, 250),
            "cta": (255, 241, 231),
        }
        bg_color = palettes.get(purpose, (246, 244, 237))
        bg = bytearray(bytes(bg_color) * (width * height))
        cls._fill_rect(bg, width, height, 0, 0, width, 38, (75, 56, 75))
        cls._avatar(bg, width, height)
        cls._yarn_and_crochet(bg, width, height, scene_number)
        accents = {"hook": (205, 91, 116), "lesson": (74, 139, 157), "application": (224, 167, 77), "cta": (112, 72, 133)}
        accent = accents.get(purpose, (112, 72, 133))
        cls._circle(bg, width, height, 575, 92, 28, accent)
        cls._circle(bg, width, height, 575, 92, 13, (255, 250, 240))
        cls._circle(bg, width, height, 35, 66, 17, (75, 56, 75))
        cls._circle(bg, width, height, 35, 66, 7, (255, 244, 226))
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
            fallback_total = max(len(images), int(request.payload.get("duration_seconds", 2)))
            durations = [max(1, fallback_total // len(images))] * len(images)

        # Narration length is authoritative: never truncate spoken words to fit
        # an estimated scene plan. Stretch scene timings proportionally when needed.
        planned_duration = sum(durations)
        ffprobe = shutil.which("ffprobe")
        if ffprobe:
            try:
                probe = subprocess.run(
                    [ffprobe, "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=noprint_wrappers=1:nokey=1", str(audio)],
                    check=True, capture_output=True, text=True, timeout=15,
                )
                narration_duration = float(probe.stdout.strip())
                if narration_duration <= 0:
                    raise ValueError("narration duration must be positive")
                target_duration = max(planned_duration, math.ceil(narration_duration))
                if target_duration > planned_duration:
                    scaled = [max(1, int(value * target_duration / planned_duration)) for value in durations]
                    scaled[-1] += target_duration - sum(scaled)
                    durations = scaled
            except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                return MediaResult(self.name, self.media_type, "failed", [], f"Could not validate narration duration: {exc}")
        concat_file = request.output_dir / "scenes.txt"
        lines = []
        for image, duration in zip(images, durations):
            escaped = str(Path(image).resolve()).replace("'", "'\\''")
            lines.append(f"file '{escaped}'")
            lines.append(f"duration {duration}")
        lines.append(f"file '{str(Path(images[-1]).resolve()).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'")
        concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        # Burn each scene's Arabic teaching line into the video so it remains
        # understandable even when viewers watch with sound off.
        def srt_time(seconds: float) -> str:
            whole = int(seconds)
            millis = int(round((seconds - whole) * 1000))
            if millis == 1000:
                whole += 1
                millis = 0
            hours, remainder = divmod(whole, 3600)
            minutes, secs = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        subtitle_path = request.output_dir / "scene_subtitles.srt"
        subtitle_lines = []
        cursor = 0.0
        for index, scene in enumerate(scenes):
            scene_duration = durations[index] if index < len(durations) else 2
            caption = _wrap_subtitle_text(str(scene.get("text", "")).strip())
            if caption:
                subtitle_lines.extend([
                    str(index + 1),
                    f"{srt_time(cursor)} --> {srt_time(cursor + scene_duration)}",
                    caption,
                    "",
                ])
            cursor += scene_duration
        subtitle_path.write_text("\n".join(subtitle_lines), encoding="utf-8")

        duration = max(2, sum(durations))
        subtitle_filter = (
            f"subtitles='{subtitle_path.resolve()}':"
            "force_style='FontName=Noto Naskh Arabic,FontSize=34,BorderStyle=3,Outline=1,"
            "Shadow=0,BackColour=&H80000000,Alignment=2,MarginV=64'"
        )
        # Full-HD delivery master with subtle Ken Burns motion.
        # This animates illustrated artwork; it is not live-action or a photorealistic presenter.
        motion_filter = (
            "fps=25,scale=3840:2160:force_original_aspect_ratio=increase,"
            "crop=3840:2160,zoompan=z='min(zoom+0.00004,1.06)':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=1920x1080:fps=25,"
            f"{subtitle_filter},format=yuv420p"
        )
        command = [
            ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-i", str(audio), "-t", str(duration), "-vf", motion_filter,
            "-map", "0:v:0", "-map", "1:a:0", "-af", "apad",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(output),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            return MediaResult(self.name, self.media_type, "failed", [], "ffmpeg timed out after 60 seconds")
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
