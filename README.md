# AI MV Studio · AI 翻唱 MV 制作流水线（开源）

> 把一首歌做成「指定音色 AI 翻唱 + 主题 MV」的完整可复用流水线：
> RVC 音色训练/转换 → 混音母带 → GPT 分镜交付包 → Flux 出图 → Remotion 合成 → 成片。

## ✨ 能力

- 🎤 **音色克隆**：RVC v2 40k 训练 + 推理（支持按歌 fine-tune）
- 🎚 **自动混音**：人声/伴奏静态增益、峰值控制、响度标准化（-14 LUFS）
- 🎬 **MV 分镜流水线**：基于「GPT 交付包」规范（逐镜提示词 + 运镜时间轴 + style guide）
- 🖼 **逐镜出图**：ComfyUI + Flux.1-dev，按 seed/prompt 批量生成
- 📝 **歌词内嵌**：LRC 对齐，按语义断句分列，书法字嵌入画面，按背景亮度自动选高对比色
- 🎞 **一键合成**：Remotion 运镜/叠化 + ffmpeg 音画合成
- 📦 **配置驱动**：每首歌一份 config，可批量排队渲染

## 🧱 架构

```
configs/songs/*.json ──► scripts/audio/  (分离→RVC转换→混音→MP3)
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

- GPU 服务器（推荐 24GB+ 显存），Ubuntu 22.04
- Python 3.10、ffmpeg、Node.js 18+
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) + Flux.1-dev 权重
- [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI)
- [audio-separator](https://github.com/nomadkaraoke/python-audio-separator) + BS-Roformer

详细步骤见 [`docs/setup-gpu.md`](docs/setup-gpu.md)。

### 1. 训练音色（一次性）

```bash
bash scripts/audio/train_pipeline.sh --dataset data/train --exp myvoice --epochs 100
```

### 2. 制作一首歌

```bash
cp configs/song.example.json configs/songs/mysong.json   # 填歌名/原唱/音频/交付包路径
bash scripts/audio/convert.sh configs/songs/mysong.json            # 音频
python scripts/mv/gen_flux.py --pack packs/mysong --out remotion/public/mvimages/mysong   # 出图
python scripts/mv/build_mvprops.py packs/mysong mysong remotion/props/mysong.json data/mysong/lyrics.lrc
python scripts/mv/render_song.py --config configs/songs/mysong.json
```

## 📖 制作细节（重点）

| 文档 | 内容 |
|---|---|
| [素材清单与要求](docs/materials.md) | 训练集/原唱/伴奏/歌词/交付包分别需要什么、质量门槛、目录组织 |
| [用 GPT 生成交付包](docs/guide-gpt-pack.md) | 三步对话提示词、硬性指标校验、常见问题纠正话术 |
| [完整制作流程](docs/end-to-end-walkthrough.md) | 从训练到成片每一步命令、验收点、时间估算 |
| [音频流水线](docs/audio-pipeline.md) | 训练参数、转换参数、混音链、LRC 清洗 |
| [MV 流水线](docs/mv-pipeline.md) | 交付包→出图→props→Remotion→合成 |
| [常见问题](docs/troubleshooting.md) | 爆音/杂音/发白/字幕排版/渲染报错排查 |
| [架构说明](docs/architecture.md) | 模块与数据流 |
| [合规说明](docs/policy.md) | 个人使用与非商用边界 |

## 📁 目录

| 目录 | 说明 |
|---|---|
| `configs/` | 歌曲与训练配置示例 |
| `scripts/audio/` | 分离、RVC 转换、混音、LRC 获取 |
| `scripts/mv/` | Flux 出图、时间轴构建、Remotion 渲染、ffmpeg 合成 |
| `remotion/` | Remotion 工程（PackMV 组件） |
| `packs/` | GPT 交付包规范、提示词模板 |
| `examples/` | 示例配置与交付包 |
| `docs/` | 全部文档 |

## 🗺 路线图

- [x] 本地流水线可复现（音频 + 分镜 + 出图 + 合成）
- [x] GPT 交付包规范与提示词模板
- [ ] CLI 统一入口 `ai-mv`
- [ ] props/交付包 JSON Schema 校验
- [ ] 失败重试与断点续跑
- [ ] 单元测试与 Docker 环境

## ⚠️ 合规与免责声明

本项目仅用于**个人学习、非商业用途**。使用他人音色/歌曲时请确保获得授权或仅作个人研究；
不冒充原唱、不商业发行、遵守平台规则。详见 [`docs/policy.md`](docs/policy.md)。
生成内容的责任由使用者承担。

## 📄 License

代码 MIT（见 `LICENSE`）。
素材（歌曲、歌词、音色模型、生成图片）不在本仓库内，需自行提供并确保合规。
