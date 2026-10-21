# Bose2 AI cinematic video + Egyptian Arabic voice trial

## Goal
Test one short AI-generated crochet scene combined with Egyptian Arabic neural narration before changing the production default. This is an experiment, not a production guarantee.

## Free-first path
1. Open the existing [CogVideoX trial notebook in Colab](https://colab.research.google.com/github/bosesamer-code/Bose2/blob/research/free-gpu-production-path/notebooks/free_gpu_cogvideox_trial.ipynb).
2. Sign in with a Google account if prompted.
3. Select a GPU runtime only if Colab offers one at no cost. If it does not, stop. Do not add billing, buy credits, or upgrade.
4. Generate one short clip and inspect hands, crochet hook, yarn, lighting, flicker, and stitch continuity.
5. Use the existing Egyptian Arabic voice path (Edge TTS, voice `ar-EG-SalmaNeural`) for the first audio comparison. The voice must be listened to and judged; a successful API call is not proof that it sounds natural enough.
6. Combine the selected clip and narration locally in the notebook, then review the MP4 and Arabic captions before any production integration.

## Cinematic scene direction
Use English prompts for the video model because its model card documents English prompt support. Start with a close-up of hands crocheting cream yarn on a wooden table, warm natural window light, shallow depth of field, slow camera push-in, realistic yarn fibers, documentary craft-film style, stable framing, no on-screen text or logos. AI-generated hands and stitches can be wrong, so do not present the output as a reliable close-up demonstration until manually checked.

## Architecture decision
- Keep the existing production factory as the default until a real generated sample passes review.
- Keep the AI video experiment opt-in and outside scheduled production.
- Keep manual human approval required; do not publish or upload automatically.
- If free GPU access is unavailable, stop rather than enabling paid compute.
- Do not add a paid API, billing requirement, or secret to the repository for this trial.

## Acceptance gate
A real short MP4 must be generated, played back, and checked for voice clarity, visual stability, plausible hands/tools, timing, and captions. Notebook/CI success alone does not pass this gate. Only after review should we decide whether to integrate the provider into the production pipeline.

## Current status
This is a test plan. No live GPU generation or natural-voice quality approval is claimed.
