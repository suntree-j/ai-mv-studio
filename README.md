# AI MV Studio · AI 翻唱 MV 制作流水线（开源）

> 把一首歌做成「指定音色 AI 翻唱 + 主题 MV」的完整可复用流水线：
> RVC 音色训练/转换 → 混音母带 → GPT 分镜交付包 → Flux 出图 → Remotion 合成 → 成片。
> 目标：本地可跑通、可复现，后续升级为 Web 应用与移动 App。

## ✨ 能力

- 🎤 **音色克隆**：RVC v2 40k 训练 + 推理（支持按歌 fine-tune）
- 🎚 **自动混音**：人声/伴奏静态增益、峰值控制、响度标准化（-14 LUFS）
- 🎬 **MV 分镜流水线**：基于「GPT 交付包」规范（逐镜提示词 + 运镜时间轴 + style guide）
- 🖼 **逐镜出图**：ComfyUI + Flux.1-dev，按 seed/prompt 批量生成
- 📝 **歌词内嵌**：LRC 对齐、书法字嵌入画面（自动断句分列、按背景亮度选高对比色）
- 🎞 **一键合成**：Remotion 运镜/叠化 + ffmpeg 音画合成
- 📦 **可配置**：每首歌一份 config，批量队列执行

## 🧱 架构

```
configs/*.json ──► scripts/audio/  (分离→RVC转换→混音→MP3)
                        │
                        ▼
                 packs/<歌名>/  (GPT 交付包: 提示词/时间轴/style)
                        │
                        ▼
scripts/mv/gen_flux.py ──► ComfyUI/Flux (逐镜出图)
                        │
                        ▼
scripts/mv/build_mvprops.py ──► remotion/ (PackMV 合成)
                        │
                        ▼
scripts/mv/make_mv.sh ──► 成品 MV（1080p + AAC）
```

## 🚀 快速开始

### 0. 环境

- GPU 服务器（推荐 RTX 3090/4090/5090，24GB+），Ubuntu 22.04
- Python 3.10、ffmpeg、Node.js 18+
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) + Flux.1-dev 权重
- [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)（语音转换）
- [audio-separator](https://github.com/nomadkaraoke/python-audio-separator) + BS-Roformer（人声/伴奏分离）

详见 [`docs/setup-gpu.md`](docs/setup-gpu.md)。

### 1. 训练音色（一次性）

```bash
# 准备 20–60 首高质量原曲 → 分离人声 → 预处理 → 训练
bash scripts/audio/train_pipeline.sh --dataset ./data/train --exp myvoice
```

### 2. 制作一首歌

```bash
cp configs/song.example.json configs/songs/mysong.json   # 填歌名/原唱/音频/交付包路径
bash scripts/audio/convert.sh configs/songs/mysong.json            # 分离 + RVC + 混音 → MP3
python scripts/mv/gen_flux.py --pack packs/mysong --out assets/mysong   # Flux 出图
python scripts/mv/build_mvprops.py --pack packs/mysong --slug mysong --lrc data/mysong.lrc --out props/mysong.json
bash scripts/mv/make_mv.sh props/mysong.json data/mysong.mp3 output/mysong.mp4
```

### 3. Remotion 渲染

```bash
cd remotion && npm install
npx remotion render src/index.ts PackMV out/mysong.mp4 --props=../props/mysong.json
```

## 📁 目录

| 目录 | 说明 |
|---|---|
| `configs/` | 歌曲配置（示例） |
| `scripts/audio/` | 分离、RVC 转换、混音、LRC 获取 |
| `scripts/mv/` | Flux 出图、时间轴生成、Remotion 渲染、ffmpeg 合成 |
| `remotion/` | Remotion 工程（PackMV 组件） |
| `packs/` | GPT 交付包规范与示例 |
| `docs/` | 环境、音频流程、MV 流程、Web/App 路线图、合规说明 |
| `examples/` | 示例配置与交付包 |

## 🗺 路线图

- [x] 本地流水线可复现（音频 + 分镜 + 出图 + 合成）
- [x] GPT 交付包规范（提示词/时间轴/style guide）
- [ ] Web 应用：任务队列 + 在线预览 + 项目管理（见 `docs/webapp-roadmap.md`）
- [ ] 移动 App：录制/选歌/生成/分享（见 `docs/app-roadmap.md`）

## ⚠️ 合规与免责声明

本项目仅用于**个人学习、非商业用途**。使用他人音色/歌曲时，请确保：

- 获得音色权利人授权，或仅用于个人研究
- 不冒充原唱、不用于商业发行、不误导听众
- 遵守歌曲版权与平台规则

详见 [`docs/policy.md`](docs/policy.md)。生成的音频/视频版权与责任由使用者承担。

## 📄 License

代码：MIT（见 [LICENSE](LICENSE)）。
素材（歌曲、歌词、音色模型、生成图片）不在本仓库内，需使用者自行提供并确保合规。
