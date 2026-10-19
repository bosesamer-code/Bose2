# Real voice and hands workflow

Bose2 now has an **opt-in** real-footage provider path. It does not create a face/avatar and it does not claim generated illustrations are real footage.

## Required inputs

- `recorded_audio_path`: path to your own recorded narration as an MP3 file (at least 1 KB).
- `real_footage_paths`: one or more video paths in MP4, MOV, MKV, or WEBM format. Use footage you recorded yourself or have permission to use.
- `scene_plan`: scene dictionaries with `duration_seconds` and optional Arabic `text` for captions.
- `script`: can remain in the inputs for the rest of the factory contract; the real-footage path uses your recorded narration instead of generated TTS.

The provider scales/crops the supplied footage to 1920x1080 at 25 fps, reuses available clips to cover the planned scenes, burns Arabic scene captions, and uses the recorded narration as the soundtrack. It does not synthesize missing hands footage or voice. Review framing, caption timing, audio levels, rights, and the final MP4 manually.

## Current limitations

- The recording input accepts MP3 only for predictable compatibility with the existing artifact validator.
- This provider path is an API within the production pipeline; the scheduled GitHub Actions workflow does **not** collect media uploads from a phone or automatically discover local phone files.
- The current public workflow therefore continues to use the illustrated fallback unless a caller explicitly supplies both `recorded_audio_path` and `real_footage_paths`.
- A completed MP4 is not proof that footage is genuine or that rights have been checked.
- Publishing remains manual and requires human approval. This feature does not upload or publish anything.
- No paid APIs, GPU credits, billing, or new secrets are required.

## Selection behavior

`run_free_production(..., inputs)` selects the real-footage providers only when both `recorded_audio_path` and `real_footage_paths` are present. If those inputs are absent, the existing illustrated free provider registry is retained.
