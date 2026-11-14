#!/usr/bin/env bash
# Trim silences, speed up slightly (x1.06) and loudness-normalize each voiceover clip.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build/vo
for f in assets/vo/s*.mp3; do
  k=$(basename "$f" .mp3)
  ffmpeg -hide_banner -loglevel error -y -i "$f" -af "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.02,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse,atempo=1.06,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-16:TP=-1.5:LRA=7" -ar 48000 -ac 2 "build/vo/$k.wav"
  printf '%s %s\n' "$k" "$(ffprobe -v error -show_entries format=duration -of csv=p=0 "build/vo/$k.wav")"
done > build/vo/durations.txt
cat build/vo/durations.txt
