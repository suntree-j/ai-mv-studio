#!/usr/bin/env bash
# 简易合成：把音频合进无声视频（画面不重编码）
# 用法: bash scripts/mv/make_mv.sh <video.mp4> <audio.mp3> <out.mp4> [audio_start_seconds]
set -euo pipefail
VIDEO="${1:?usage: make_mv.sh video audio out [start]}"
AUDIO="${2:?}"
OUT="${3:?}"
START="${4:-0}"
FF="${FFMPEG:-ffmpeg}"
mkdir -p "$(dirname "$OUT")"
$FF -y -hide_banner -loglevel error -ss "$START" -i "$AUDIO" -i "$VIDEO" \
  -map 1:v:0 -map 0:a:0 -c:v copy -c:a aac -ar 48000 -b:a 256k \
  -shortest -movflags +faststart "$OUT"
echo "OK -> $OUT"
