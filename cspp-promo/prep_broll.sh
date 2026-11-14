#!/usr/bin/env bash
# Extract b-roll clips (assets/broll/{city,globe,leaves,hands}.mp4) to JPEG frames for the renderer.
set -euo pipefail
cd "$(dirname "$0")"
for f in assets/broll/*.mp4; do
  [ -e "$f" ] || continue
  k=$(basename "$f" .mp4)
  rm -rf "build/broll/$k" && mkdir -p "build/broll/$k"
  ffmpeg -hide_banner -loglevel error -y -i "$f" -vf "fps=30,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,eq=saturation=1.05" -q:v 3 "build/broll/$k/f_%04d.jpg"
  echo "$k: $(ls build/broll/$k | wc -l) frames"
done
