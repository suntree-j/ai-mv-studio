#!/usr/bin/env bash
# 训练流程：高质量原曲 → 分离人声 → 切片预处理 → f0/特征 → RVC v2 训练
# 用法: bash scripts/audio/train_pipeline.sh --dataset data/train --exp myvoice
set -euo pipefail
source "$(dirname "$0")/../common/env.sh"

DATASET="./data/train"
EXP="myvoice"
EPOCHS=100

while [ $# -gt 0 ]; do
  case "$1" in
    --dataset) DATASET="$2"; shift 2;;
    --exp) EXP="$2"; shift 2;;
    --epochs) EPOCHS="$2"; shift 2;;
    *) echo "unknown $1"; exit 1;;
  esac
done

cd "$RVC_DIR"
export PYTHONPATH="$RVC_DIR"
PY=${PYTHON:-python3}
EXP_DIR="logs/$EXP"
mkdir -p "$EXP_DIR" work/train_vocals

echo "[1/5] 分离训练集人声"
for f in "$DATASET"/*.{flac,wav,mp3}; do
  [ -f "$f" ] || continue
  audio-separator "$f" \
    --model_filename "${SEP_MODEL:-model_bs_roformer_ep_317_sdr_12.9755.ckpt}" \
    --model_file_dir "${UVR_DIR:-./models/uvr}" \
    --output_dir work/train_vocals --output_format wav --single_stem Vocals \
    || echo "skip $f"
done

echo "[2/5] 切片预处理"
$PY -c "import sys,runpy; sys.argv=['preprocess.py','work/train_vocals','40000','4','$EXP_DIR','True','3.7']; runpy.run_path('train/preprocess.py', run_name='__main__')"

echo "[3/5] f0 提取"
$PY -c "import sys,runpy; sys.argv=['extract_f0.py','cuda','1','0','0','$EXP_DIR','true']; runpy.run_path('train/dataset/extract_f0.py', run_name='__main__')"

echo "[4/5] HuBERT 特征"
$PY -c "import sys,runpy; sys.argv=['extract_hubert_feature.py','cuda','1','0','0','$EXP_DIR','v2','true']; runpy.run_path('train/dataset/extract_hubert_feature.py', run_name='__main__')"

echo "[5/5] 构建 filelist 并训练"
$PY - <<EOF
import os
exp='$EXP_DIR'
gt=os.path.abspath(exp+'/0_gt_wavs'); feat=os.path.abspath(exp+'/3_feature768')
f0=os.path.abspath(exp+'/2a_f0'); fnsf=os.path.abspath(exp+'/2b-f0nsf')
names=set(n.split('.')[0] for n in os.listdir(gt)) & set(n.split('.')[0] for n in os.listdir(feat)) & set(n.split('.')[0] for n in os.listdir(f0)) & set(n.split('.')[0] for n in os.listdir(fnsf))
lines=[f"{gt}/{n}.wav|{feat}/{n}.npy|{f0}/{n}.wav.npy|{fnsf}/{n}.wav.npy|0" for n in sorted(names)]
open(exp+'/filelist.txt','w').write('\n'.join(lines))
print('filelist', len(lines))
EOF
cp logs/shuangshengA/config.json "$EXP_DIR/config.json" 2>/dev/null || cp configs/v2/40k.json "$EXP_DIR/config.json"
$PY -c "import sys,runpy; sys.argv=['train.py','-e','$EXP','-sr','40k','-f0','1','-bs','8','-g','0','-te','$EPOCHS','-se','10','-pg','assets/pretrained_v2/f0G40k.pth','-pd','assets/pretrained_v2/f0D40k.pth','-l','1','-c','0','-sw','1','-v','v2']; runpy.run_path('train/train.py', run_name='__main__')"

echo "训练完成，模型在 $RVC_DIR/assets/weights/${EXP}_*.pth"
