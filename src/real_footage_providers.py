"""Optional real-footage production mode using user-owned clips and recorded narration.

This mode deliberately has no face/avatar path. It requires real recorded audio
and real crochet footage supplied by the operator; otherwise the existing
illustrated free factory remains unchanged.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from src.free_media_providers import (
    FreeLocalDesignProvider,
    FreeLocalImageProvider,
    FreeLocalThumbnailProvider,
)
from src.media_providers import MediaRequest, MediaResult, ProviderRegistry

VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm"}


class RecordedAudioProvider:
    name = "recorded-audio-input"
    media_type = "audio"

    def generate(self, request: MediaRequest) -> MediaResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        source_value = str(request.payload.get("recorded_audio_path", "")).strip()
        if not source_value:
            return MediaResult(self.name, self.media_type, "waiting_for_inputs", [], "recorded_audio_path is required")
        source = Path(source_value).expanduser().resolve()
        # Keep the initial workflow intentionally simple and predictable: accept
        # MP3 recordings only, which are supported by the existing artifact gate.
        if not source.is_file() or source.suffix.lower() != ".mp3" or source.stat().st_size < 1024:
            return MediaResult(self.name, self.media_type, "failed", [], "Recorded narration must be an existing MP3 file of at least 1 KB.")
        output = request.output_dir / "voice.mp3"
        try:
            shutil.copyfile(source, output)
        except OSError as exc:
            return MediaResult(self.name, self.media_type, "failed", [], f"Could not copy recorded narration: {exc}")
        return MediaResult(self.name, self.media_type, "completed", [str(output)])


class RealFootageVideoProvider:
    name = "real-crochet-footage"
    media_type = "video"

    def generate(self, request: MediaRequest) -> MediaResult:
        request.output_dir.mkdir(parents=True, exist_ok=True)
        output = request.output_dir / "video.mp4"
        output.unlink(missing_ok=True)
        ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
        if not ffmpeg or not ffprobe:
            return MediaResult(self.name, self.media_type, "not_configured", [], "ffmpeg and ffprobe are required")
        raw_paths = request.payload.get("real_footage_paths", [])
        if isinstance(raw_paths, str):
            raw_paths = [raw_paths]
        clips = [Path(str(item)).expanduser().resolve() for item in raw_paths]
        clips = [p for p in clips if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS and p.stat().st_size > 0]
        audio_value = request.payload.get("audio_path")
        audio = Path(str(audio_value)).expanduser().resolve() if audio_value else None
        if not clips:
            return MediaResult(self.name, self.media_type, "waiting_for_inputs", [], "Provide real_footage_paths with at least one MP4/MOV/MKV/WEBM clip.")
        if not audio or not audio.is_file():
            return MediaResult(self.name, self.media_type, "waiting_for_inputs", [], "A valid recorded MP3 narration is required.")
        scenes = list(request.payload.get("scene_plan", [])) or [{"scene": 1, "text": ""}]
        base_durations = [max(1, int(s.get("duration_seconds", 1))) for s in scenes]
        try:
            probe = subprocess.run(
                [ffprobe, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(audio)],
                check=True, capture_output=True, text=True, timeout=15,
            )
            audio_duration = float(probe.stdout.strip())
            if audio_duration <= 0:
                raise ValueError("narration duration must be positive")
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            return MediaResult(self.name, self.media_type, "failed", [], f"Could not measure recorded narration: {exc}")
        planned = sum(base_durations)
        target_duration = max(planned, int(audio_duration + 0.999))
        durations = [max(1, int(d * target_duration / planned)) for d in base_durations]
        durations[-1] += target_duration - sum(durations)

        def srt_time(seconds: float) -> str:
            whole = int(seconds)
            millis = int(round((seconds - whole) * 1000))
            if millis == 1000:
                whole, millis = whole + 1, 0
            hours, remainder = divmod(whole, 3600)
            minutes, secs = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

        subtitle_path = request.output_dir / "scene_subtitles.srt"
        subtitle_lines, cursor = [], 0
        for index, scene in enumerate(scenes):
            text = " ".join(str(scene.get("text", "")).split())
            if text:
                wrapped = []
                words, line = text.split(), ""
                for word in words:
                    if line and len(line) + len(word) + 1 > 34:
                        wrapped.append(line)
                        line = word
                    else:
                        line = (line + " " + word).strip()
                if line:
                    wrapped.append(line)
                subtitle_lines.extend([str(index + 1), f"{srt_time(cursor)} --> {srt_time(cursor + durations[index])}", "\n".join(wrapped), ""])
            cursor += durations[index]
        subtitle_path.write_text("\n".join(subtitle_lines), encoding="utf-8")

        segments_dir = request.output_dir / "real_footage_segments"
        segments_dir.mkdir(exist_ok=True)
        segments = []
        try:
            for index, scene_duration in enumerate(durations):
                clip = clips[index % len(clips)]
                segment = segments_dir / f"segment_{index + 1:03d}.mp4"
                subprocess.run(
                    [ffmpeg, "-y", "-stream_loop", "-1", "-i", str(clip), "-t", str(scene_duration),
                     "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25,format=yuv420p",
                     "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", str(segment)],
                    check=True, capture_output=True, text=True, timeout=180,
                )
                if not segment.is_file() or segment.stat().st_size < 512:
                    raise RuntimeError(f"Footage segment {index + 1} was not created.")
                segments.append(segment)
            concat_path = request.output_dir / "real_footage_segments.txt"
            concat_path.write_text(
                "\n".join("file '" + str(p.resolve()).replace("'", "'\\''") + "'" for p in segments) + "\n",
                encoding="utf-8",
            )
            subtitle_filter = (
                f"subtitles='{subtitle_path.resolve()}':"
                "force_style='FontName=Noto Naskh Arabic,FontSize=20,BorderStyle=3,Outline=1,"
                "Shadow=0,BackColour=&H80000000,Alignment=2,MarginV=28'"
            )
            subprocess.run(
                [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path), "-i", str(audio),
                 "-t", str(target_duration), "-vf", subtitle_filter, "-map", "0:v:0", "-map", "1:a:0",
                 "-af", "loudnorm=I=-16:TP=-1.5:LRA=11,acompressor=threshold=-18dB:ratio=2:attack=20:release=250,apad",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                 "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(output)],
                check=True, capture_output=True, text=True, timeout=240,
            )
        except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
            output.unlink(missing_ok=True)
            detail = getattr(exc, "stderr", "") or getattr(exc, "stdout", "") or str(exc)
            return MediaResult(self.name, self.media_type, "failed", [], f"Real-footage render failed: {str(detail)[-1200:]}")
        if not output.is_file() or output.stat().st_size < 1024:
            output.unlink(missing_ok=True)
            return MediaResult(self.name, self.media_type, "failed", [], "Real-footage render did not produce a valid MP4.")
        return MediaResult(self.name, self.media_type, "completed", [str(output)])


def real_footage_registry() -> ProviderRegistry:
    """Keep all existing visual providers; replace only audio and video inputs."""
    registry = ProviderRegistry()
    registry.register(RecordedAudioProvider())
    registry.register(FreeLocalImageProvider())
    registry.register(FreeLocalDesignProvider())
    registry.register(RealFootageVideoProvider())
    registry.register(FreeLocalThumbnailProvider())
    return registry
