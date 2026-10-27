# 从零到成片：完整制作流程

本文以「一首歌」为单位，按顺序走完：训练 → 素材 → 交付包 → 音频 → 出图 → 渲染 → 合成 → 验收。

## 0. 目录与配置

```
project/
├─ data/train/            # 训练素材（一次性）
├─ data/<slug>/           # 目标曲素材
├─ models/rvc/            # 音色模型
├─ packs/<slug>/          # GPT 交付包
├─ remotion/              # Remotion 工程
├─ output/<slug>/         # 成品
└─ configs/songs/<slug>.json
```

复制配置模板：

```bash
mkdir -p configs/songs
cp configs/song.example.json configs/songs/<slug>.json
```

## 1. 训练音色（一次性，2–4 小时）

准备素材见 [`materials.md`](materials.md) 第一节。

```bash
bash scripts/audio/train_pipeline.sh --dataset data/train --exp myvoice --epochs 100
```

产物：`assets/weights/myvoice_e10…e100.pth`（每 10 epoch 一个检查点）。

**检查点选择**：先听 e60/e80/e100 三版，选杂音最少、音色最像的；不必盲信最后一个。

## 2. 准备目标曲素材

```
data/<slug>/
├─ original.flac      # 原唱（必须，版本要正确）
├─ instrumental.flac  # 官方伴奏（推荐）
└─ lyrics.lrc         # 歌词（推荐，没有可抓取）
```

没有 LRC 时：

```bash
python scripts/audio/get_lrc_qq.py '歌名'                       # 搜索
python scripts/audio/get_lrc_qq.py '歌名' <songmid> <slug>      # 下载
```

**时长核对**：`ffprobe` 看原唱时长，记下来（GPT 交付包要用）。

## 3. 生成 MV 交付包（GPT）

按 [`guide-gpt-pack.md`](guide-gpt-pack.md) 三步对话，得到 4 个文件放入 `packs/<slug>/`。

校验：

```bash
python - <<'PY'
import json
p=json.load(open("packs/<slug>/逐镜提示词.json",encoding="utf-8"))
t=json.load(open("packs/<slug>/运镜时间轴_24fps.json",encoding="utf-8"))
assert len(p["shots"])==len(t["shots"])
last=0
for s in t["shots"]:
    assert s["start_frame"]==last; last=s["end_frame"]
assert last==t["total_frames"]
print("pack OK", len(p["shots"]), "shots")
PY
```

## 4. 音频：分离 → 转换 → 混音

编辑 `configs/songs/<slug>.json`（原唱、伴奏、模型、输出路径），然后：

```bash
bash scripts/audio/convert.sh configs/songs/<slug>.json
```

产物：`output/<slug>/<slug>_320k.mp3`

验收：
- 人声轨单独听：无爆音、无电音、无杂音
- 伴奏轨单独听：无残留人声
- 混音：人声不糊、伴奏不盖人声、峰值 ≤ -1dB、响度 ≈ -14 LUFS

## 5. 出图（Flux）

先启动 ComfyUI（8188），确认 Flux 权重就绪：

```bash
python scripts/mv/gen_flux.py --pack packs/<slug> --out remotion/public/mvimages/<slug>
```

- 每镜输出 `S01.png`…`S36.png`（1536×864）
- 已存在的会跳过；某镜不满意：删掉该 png 重跑
- 出图期间不要同时跑 RVC（显存争用会 OOM）

**画风一致性检查**：抽 3–5 张不同镜头的图，确认色调/材质/人物比例一致。

## 6. 构建时间轴 props（含歌词清洗）

```bash
python scripts/mv/build_mvprops.py packs/<slug> <slug> remotion/props/<slug>.json data/<slug>/lyrics.lrc
```

输出包含：
- `shots`（帧区间、运镜、背景亮度 `lum`）
- `lyrics`（已清洗：去作词/作曲/原唱/歌手名前缀）
- `original_artist`、`audio_start_seconds`

## 7. Remotion 渲染

```bash
cd remotion
npm install
npx remotion render src/index.ts PackMV out/<slug>.mp4 --props=props/<slug>.json --concurrency=4
```

画面能力：
- 每镜 Ken Burns 运镜 + 12 帧叠化
- 片头信息卡（歌名/原唱/AI 声明）
- 书法歌词嵌入：按短语断句、自动分列、字号自适应、按背景亮度选高对比色

## 8. 合成与验收

```bash
bash scripts/mv/make_mv.sh remotion/out/<slug>.mp4 output/<slug>/<slug>_320k.mp3 output/<slug>/<slug>_MV_1080p.mp4 0
```

或一步：

```bash
python scripts/mv/render_song.py --config configs/songs/<slug>.json
```

验收清单：

- [ ] 画面：1920×1080、24fps、无黑帧/花屏
- [ ] 音频：AAC 256k、48kHz、与画面时长一致
- [ ] 前奏完整（除非要求裁剪）
- [ ] 片头有歌名/原唱/AI 声明/非商用
- [ ] 歌词无杂质、断句自然、颜色可读
- [ ] 音画同步（字幕与唱词对轴）

## 9. 交付物命名

```
output/<slug>/
├─ <slug>_320k.mp3                  # 音频
└─ <slug>_MV_1080p.mp4              # 成片
```

## 时间估算（单卡 4090/5090）

| 步骤 | 耗时 |
|---|---|
| 训练（30 首，100 epoch） | 2–4 h（一次性） |
| 单曲分离+转换+混音 | 5–15 min |
| 出图（30–40 镜） | 15–40 min |
| Remotion 渲染 | 5–10 min |
| 合成 | < 1 min |
