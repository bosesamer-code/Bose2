# Kaggle free-GPU trial for Bose2

## Why Kaggle first
Kaggle documents free NVIDIA GPU access for notebooks and a weekly GPU quota that is commonly up to 30 hours, subject to resource availability and demand. GPU availability is not guaranteed. See the official docs:
- https://www.kaggle.com/docs/notebooks
- https://www.kaggle.com/docs/efficient-gpu-usage

## Open the experiment
Notebook: [bose2_kaggle_ai_cinematic_voice_trial.ipynb](../notebooks/bose2_kaggle_ai_cinematic_voice_trial.ipynb)

1. Sign in to Kaggle and create/import a notebook from this repository file.
2. In Notebook Settings, select GPU only if available for free. Enable Internet if available so the model and Edge TTS can download what they need.
3. Run the first cell to verify GPU availability. If it fails, stop; do not enable billing or buy credits.
4. Run the generation cell to attempt one short CogVideoX-2B crochet scene with Egyptian Arabic narration.
5. Play the MP4 and review visual plausibility, motion flicker, narration clarity, and timing. This sample does not include burned-in Arabic captions yet.

## Production integration policy
- This notebook is a manual experiment, not a production runtime or guaranteed API.
- Do not add Kaggle credentials/secrets to GitHub Actions and do not schedule this notebook.
- Download the MP4 manually and review it before considering any integration.
- Keep the existing CPU production factory unchanged until an actual sample passes review.
- Human approval remains required. Automatic publishing stays disabled.
- Never enable paid compute, billing, or credits for this trial.
