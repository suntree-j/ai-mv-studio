# 环境搭建（GPU 服务器）

## 硬件建议

| 项目 | 最低 | 推荐 |
|---|---|---|
| GPU | RTX 3060 12G | RTX 4090 / 5090 24–32G |
| 内存 | 32G | 64G |
| 硬盘 | 100G | 500G+（模型 + 素材） |
| 系统 | Ubuntu 22.04 | Ubuntu 22.04 |

## 1. 基础依赖

```bash
sudo apt update && sudo apt install -y ffmpeg git wget curl build-essential
# Python 3.10 / Node 18+
```

## 2. RVC（声音转换）

```bash
git clone https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git vendor/rvc
cd vendor/rvc
pip install -r requirements.txt
# 需要：assets/pretrained_v2/f0G40k.pth、f0D40k.pth、hubert_base、rmvpe
# 下载来源：HuggingFace lj1995/VoiceConversionWebUI（可用 hf-mirror.com 镜像）
```

## 3. 人声分离（audio-separator + BS-Roformer）

```bash
pip install "audio-separator[gpu]"
mkdir -p models/uvr
# 下载 model_bs_roformer_ep_317_sdr_12.9755.ckpt 放入 models/uvr
```

## 4. ComfyUI + Flux

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git vendor/ComfyUI
cd vendor/ComfyUI && pip install -r requirements.txt
# 权重放到 models/：
#   unet/flux1-dev-fp8.safetensors
#   clip/t5xxl_fp8_e4m3fn.safetensors
#   clip/clip_l.safetensors
#   vae/ae.safetensors
python main.py --listen 0.0.0.0 --port 8188
```

## 5. Remotion

```bash
cd remotion
npm install
# 字体：MaShanZheng（OFL）已在 public/fonts；可选 Noto Serif SC
```

## 6. 环境变量

```bash
cp scripts/common/env.sh.example scripts/common/env.sh
# 修改 RVC_DIR / UVR_DIR / COMFY_URL / REMOTION_DIR
```

## 常见问题

- **ComfyUI 启动缺 yaml 等包**：`pip install -r requirements.txt` 用清华镜像重试
- **RVC 训练脚本循环导入**：用 `runpy.run_path` 方式执行（见 `train_pipeline.sh`）
- **显存不足**：出图与 RVC 推理不要同时跑；训练 `-bs 4~8`
- **中文路径问题**：素材/输出目录尽量使用 ASCII 路径
