# Free no-GPU cinematic montage

## Purpose
This optional workflow assembles a narrated crochet lesson from user-supplied or properly licensed video clips. FFmpeg normalizes clips to 1080p/25 fps, adds scene captions, mixes Egyptian Arabic speech generated with Edge TTS, and exports an MP4.

## What it solves
- Does not require a GPU or video-diffusion model.
- Produces a more natural-looking result than the illustrated-only default when suitable real footage is supplied.
- Avoids paid video-generation APIs and GPU billing.
- Keeps speech and captions in a repeatable editing pipeline.

## What it does not solve
- It does not invent or generate new realistic footage; the operator must provide suitable clips.
- It does not guarantee perfect speech-to-caption synchronization. Scene lengths and captions should be reviewed and adjusted.
- Edge TTS needs internet access and may be rate-limited; it is not a local/offline voice model.
- The free notebook runtime may disconnect or be unavailable.

## Run it
1. Open the notebook: [Bose2 no-GPU cinematic montage notebook](../notebooks/bose2_free_no_gpu_cinematic_montage.ipynb).
2. Run cells in order in a free Colab runtime. Do not upgrade or enable billing.
3. Upload only footage you own or are licensed to use.
4. Edit the Arabic narration script and scene captions.
5. Generate audio, render the MP4, download it, and watch it all the way through.

## Rollout guardrails
- This is an optional manual trial, not the scheduled production default.
- Do not add automatic publishing, scheduled uploads, paid APIs, or secret values.
- Keep the AI video GPU notebook as a separate experiment; it remains unvalidated until a real GPU run and manual quality review succeed.
- Do not merge into the default production path until an end-to-end render is tested and reviewed.
