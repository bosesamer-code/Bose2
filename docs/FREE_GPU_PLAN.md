# Free GPU plan for Bose2

## Decision

Do not connect a notebook GPU directly to the scheduled GitHub Actions production workflow. A free GPU is not a guaranteed, always-on API, and notebook sessions can time out or be reclaimed. The production workflow must continue to work when no GPU is available.

## What is genuinely free, and what it means

- **Kaggle Notebooks GPU:** a useful browser-based, manual experiment path. GPU availability and quotas are limited, sessions are temporary, and output files must be exported before the session ends. It is not a persistent production API.
- **Google Colab free GPU:** useful for interactive experiments, but resources and limits vary. Google's own FAQ says free resources are not guaranteed and warns that GPU runtimes used as a web UI for content generation may be terminated.
- **Hugging Face Spaces:** CPU Basic is free; GPU hardware is normally billed. Community GPU grants/ZeroGPU access may be possible but must not be assumed or treated as guaranteed capacity.
- **GitHub Actions hosted runners:** do not assume a GPU is present. The existing workflow remains CPU-only unless a separately verified GPU service is deliberately configured.

## Recommended rollout

1. Keep the existing factory as the safe default; no GPU calls occur by default.
2. First test one short scene in a browser-based free GPU notebook. Start with **one model only** (CogVideoX-2B is the first candidate), low resolution and a short clip. Check whether it fits available VRAM and whether the motion is useful for a crochet lesson.
3. Review the exported clip manually for visual artifacts, especially hands, hook, yarn, and stitch continuity. Do not treat generated motion as a reliable close-up demonstration of a real stitch.
4. Only add automatic production integration after a provider has a documented free allowance, an API suitable for server-to-server calls, and a verified no-billing configuration. The integration must be opt-in, have strict per-job limits and timeouts, never print credentials, and fall back to the existing factory on unavailable quota.
5. Keep publication behind the existing human approval gate.

## Acceptance criteria before enabling automatic GPU generation

- One real short video clip is produced and downloaded successfully.
- GPU model and VRAM are recorded without exposing account secrets.
- The job fails safely on missing credentials, unavailable GPU, quota exhaustion, timeout, or invalid video.
- No payment method, paid plan, billing upgrade, or automatic publication is enabled.
- A CPU-only regression run still passes.

## Official references checked

- Google Colab FAQ and resource limits: https://research.google.com/colaboratory/faq.html
- Kaggle Notebooks documentation: https://www.kaggle.com/docs/notebooks
- Hugging Face Spaces hardware and GPU pricing: https://huggingface.co/docs/hub/spaces-overview
- Hugging Face GPU Spaces and community grants: https://huggingface.co/docs/hub/main/en/spaces-gpus
- CogVideoX-2B model card: https://huggingface.co/zai-org/CogVideoX-2b

## Current status

This document records the safe implementation decision; it does not claim that a GPU has been provisioned or that a generated video has been tested. Automatic GPU generation remains disabled until the acceptance criteria above are met.
