# Free no-GPU cinematic montage

Bose2 has an opt-in montage mode for producing a narrated crochet lesson without a GPU.

## What it does

- Uses locally uploaded video clips in MP4, MOV, MKV, or WEBM format.
- Generates Egyptian Arabic narration with the existing Edge TTS provider and voice `ar-EG-SalmaNeural`.
- Uses FFmpeg to normalize clips to 1080p/25fps, assemble scenes, burn Arabic captions, and mux the narration.
- Produces an MP4 for download and manual review.

## What it does not do

- It does not generate new photorealistic footage. The visuals come from supplied clips.
- It does not download stock footage or decide whether a clip is licensed. Use your own clips or material you have permission to use.
- It does not require a GPU, paid API, billing, or new secrets. Edge TTS still needs an internet connection and may fail temporarily.
- It does not upload or publish the resulting video.

## Try it from a phone

Open the [free Colab notebook](https://colab.research.google.com/github/bosesamer-code/Bose2/blob/feature/real-hands-footage-mode/notebooks/no_gpu_cinematic_montage_colab.ipynb). Upload one or more authorized crochet clips, edit the Egyptian Arabic narration and caption examples, run the cells, and download the MP4. Keep the browser open during rendering; free runtimes can disconnect.

## Pipeline selection

The normal illustrated factory remains the default. The montage provider is selected only when `real_footage_paths` and either `script` or `recorded_audio_path` are provided. When a recording is supplied, it is preferred; otherwise the Egyptian Arabic TTS provider generates narration from `script`.

This is an opt-in feature branch and has not yet been validated with a full live Colab render. Run a short trial and inspect audio, captions, crop, and playback before considering production use. Human review and manual publishing remain mandatory.
