#!/usr/bin/env bash
# 通用转换流程：原曲 → 分离 → RVC 转换 → 混音 → MP3
# 用法: bash scripts/audio/convert.sh configs/songs/mysong.json
set -euo pipefail
source "$(dirname "$0")/../common/env.sh"

CONFIG="${1:?usage: convert.sh <config.json>}"
SLUG=$(python3 -c "import json,sys;print(json.load(open('$CONFIG'))['slug'])")
SRC=$(python3 -c "import json;print(json.load(open('$CONFIG'))['audio_original'])")
INST_CFG=$(python3 -c "import json;print(json.load(open('$CONFIG')).get('instrumental',''))")
MODEL=$(python3 -c "import json;print(json.load(open('$CONFIG'))['rvc_model'])")
OUT_MP3=$(python3 -c "import json;print(json.load(open('$CONFIG'))['output_audio'])")
WORK="work/$SLUG"
mkdir -p "$WORK" "$(dirname "$OUT_MP3")"

echo "[1/4] 分离人声/伴奏（没有官方伴奏时）"
if [ -z "$INST_CFG" ] || [ ! -f "$INST_CFG" ]; then
  audio-separator "$SRC" \
    --model_filename "${SEP_MODEL:-model_bs_roformer_ep_317_sdr_12.9755.ckpt}" \
    --model_file_dir "${UVR_DIR:-./models/uvr}" \
    --output_dir "$WORK/sep" --output_format wav
  VOC=$(ls "$WORK/sep/"*Vocals*.wav | head -1)
  INST=$(ls "$WORK/sep/"*Instrumental*.wav | head -1)
else
  audio-separator "$SRC" \
    --model_filename "${SEP_MODEL:-model_bs_roformer_ep_317_sdr_12.9755.ckpt}" \
    --model_file_dir "${UVR_DIR:-./models/uvr}" \
    --output_dir "$WORK/sep" --output_format wav --single_stem Vocals
  VOC=$(ls "$WORK/sep/"*Vocals*.wav | head -1)
  INST="$INST_CFG"
fi

echo "[2/4] RVC 转换（模型: $MODEL）"
(cd "$RVC_DIR" && PYTHONPATH="$RVC_DIR" python infer/cli.py \
  --model "$MODEL" --input "$VOC" --output "$WORK/vocal_ai.wav" \
  --speaker-id 0 --f0-method rmvpe --pitch 0 --index-rate 0 \
  --protect 0.33 --rms-mix-rate 0.25 --format wav --overwrite)

echo "[3/4] 混音"
python3 scripts/audio/mix_song.py "$WORK/vocal_ai.wav" "$INST" "$WORK/mix.wav"

echo "[4/4] 输出 MP3"
ffmpeg -y -loglevel error -i "$WORK/mix.wav" -af "loudnorm=I=-14:TP=-1.5:LRA=11" -b:a 320k "$OUT_MP3"
echo "OK -> $OUT_MP3"
