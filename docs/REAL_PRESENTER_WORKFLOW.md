# Bose2 Real-Voice + Real-Hands Video Workflow

## Decision

Bose2 ("Production City") will use the creator's **real voice and real hands** while demonstrating crochet. The creator's face is not required. This is a trust-first format: the lesson is presented by a real person, and the key crochet steps are shown in genuine footage.

Bose1 ("Center of Secrets") remains a separate project and must not be changed as part of this work.

## Non-negotiable safeguards

- Keep the existing production pipeline working; introduce changes incrementally.
- Keep publishing manual. Do not enable automatic uploads, scheduling, or public publishing.
- Do not add paid APIs, billing, GPU subscriptions, or paid upgrades as part of the free-first trial.
- Never log, commit, or request API keys, refresh tokens, or other secrets.
- Do not describe AI-generated footage as a real recording. AI may help draft scripts, clean up captions, or plan edits, but real crochet instructions must be demonstrated with genuine footage.
- If an AI-generated visual or voice is used in a way that could confuse viewers about who is presenting, clearly disclose that it is AI-generated.
- Only use music, images, and clips the creator owns or has permission to use.

## Target video specification

- Length: 1–3 minutes.
- Language: clear Egyptian Arabic, conversational and beginner-friendly.
- Presenter: creator's real voice; hands visible during the crochet demonstration; no face required.
- Visuals: real close-up footage of yarn, hook, stitches, and the finished result.
- Captions: Arabic subtitles, reviewed for crochet terms and stitch counts.
- Export: MP4 (H.264 video + AAC audio), 1080p when practical; use a vertical 9:16 layout for Reels/Shorts when the platform is the target. Keep important text away from screen edges.
- Sharing: include a useful title/cover, one clear learning outcome, and a brief invitation to save or share the tutorial.

## Repeatable lesson structure

1. **0–5 sec — Outcome:** show the finished crochet result and state what the viewer will learn.
2. **5–15 sec — Materials:** show the yarn, hook, and any required supplies.
3. **15–90 sec — Demonstration:** show the hands close-up; explain one action at a time; pause or zoom at critical stitch points.
4. **90–150 sec — Common mistake + fix:** show a likely beginner mistake and how to correct it.
5. **Final 5–10 sec — Recap:** restate the key step and invite viewers to save/share the lesson.

For a lesson shorter than 90 seconds, keep the same order and trim the number of steps rather than rushing the demonstration.

## Phone-only recording checklist

- Place the phone on a stable stand or stack of books; frame only the hands, hook, yarn, and work area.
- Record in a quiet room; keep the phone close enough to capture speech clearly without clipping.
- Use bright, soft light from the front or side; avoid a strong light behind the hands.
- Use a plain, contrasting background so stitches are easy to see.
- Record a short test first and check focus, sound, and whether both hands remain in frame.
- Record each difficult stitch as a separate close-up if needed.
- Keep the original recordings until the final export has been reviewed.

## Free-first editing and production path

1. Record the real demonstration and voice on a phone.
2. Use the existing Bose2 script workflow to draft a simple Egyptian Arabic explanation; verify every instruction against the actual technique.
3. Assemble the real footage, voice, and Arabic captions with a free editor available to the creator. Free-plan limits and watermarks can change, so verify export options before relying on a tool.
4. Use existing Bose2 automation only for tasks it already supports reliably. Do not make a video generator a required dependency.
5. Export a draft MP4 and review it manually on a phone before sharing.
6. Only after the creator approves the file should they upload it manually to the intended platform.

## Acceptance criteria before integrating new automation

A pilot video is accepted only if all checks pass:

- [ ] It shows genuine crochet footage, not a still image standing in for the demonstration.
- [ ] The creator's real voice is audible and understandable throughout.
- [ ] The hands, hook, yarn, and stitch being explained remain visible at critical moments.
- [ ] The spoken steps and captions agree; stitch counts and terminology are checked.
- [ ] No fabricated identity claims, unlicensed media, credentials, or private information appear.
- [ ] The MP4 plays from beginning to end on a phone.
- [ ] The creator has explicitly approved the exact final file.
- [ ] No automatic upload or public publishing was triggered.

## Implementation sequence

1. Preserve the current factory and its existing tests.
2. Make a single manually recorded pilot lesson before adding AI video generation.
3. Review the pilot against the acceptance criteria above.
4. If useful, add a separate optional real-footage assembly/caption step behind an explicit opt-in flag; default it off until tested.
5. Keep GPU-generated clips as an optional experiment only. They must not replace genuine stitch demonstrations or block the normal factory when no free GPU is available.

This document is a workflow specification, not a claim that a real-footage recorder/editor or GPU video generation has already been integrated or verified.
