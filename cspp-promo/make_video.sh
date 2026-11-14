#!/usr/bin/env bash
# Full pipeline: voiceover prep -> timeline/HTML -> frames -> music/SFX mix -> final MP4
set -euo pipefail
cd "$(dirname "$0")"
bash prep_audio.sh
bash prep_broll.sh
python3 build.py
rm -rf build/frames
WORKERS=${WORKERS:-4} node render.js frames
python3 audio_mix.py
mkdir -p output
ffmpeg -hide_banner -y -framerate 30 -i build/frames/f_%05d.jpg -i build/mix_raw.wav \
  -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -profile:v high -tune animation \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart -shortest output/CSPP_Promo_EasyPM_Vertical.mp4
node render.js stills 22.5 && cp build/stills/t_22.50.jpg output/cover.jpg
echo "done -> output/CSPP_Promo_EasyPM_Vertical.mp4"
