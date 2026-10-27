# MV 流水线

## 1. 交付包（GPT 生成）

每首歌一个目录 `packs/<slug>/`，必须包含：

| 文件 | 说明 |
|---|---|
| `逐镜提示词.json` | 镜头列表：prompt/seed/时长/歌词提示 |
| `运镜时间轴_24fps.json` | 每镜帧区间与运镜方式 |
| `style_guide.md` | 色调/材质/构图/禁用元素 |
| `README.md` | 主题与验收说明 |

Schema 详见 [`packs/schema/pack-schema.md`](../packs/schema/pack-schema.md)。

硬性要求：
- `total_frames = round(duration_seconds × fps)`，所有镜头首尾相接
- prompt 为英文单段，可直接喂 Flux；包含 `no text/calligraphy/seal/watermark`
- 人物只做背影/剪影，不出现五官特写

## 2. 逐镜出图

```bash
# 先启动 ComfyUI（端口 8188），Flux fp8 权重就绪
python scripts/mv/gen_flux.py --pack packs/mysong --out remotion/public/mvimages/mysong
```

- 输出：`S01.png` … 每镜一张（1536×864）
- 已存在的图会跳过；可删掉重出某镜
- 出图与 RVC 推理不要同时占 GPU

## 3. 时间轴 + 歌词 → props

```bash
python scripts/mv/build_mvprops.py packs/mysong mysong remotion/props/mysong.json data/mysong.lrc
```

生成内容：
- `shots`：帧区间 + 运镜 + 背景亮度 `lum`
- `lyrics`：清洗后的歌词与帧区间
- `original_artist`、`audio_start_seconds`

## 4. Remotion 合成

```bash
cd remotion && npm install
npx remotion render src/index.ts PackMV out/mysong.mp4 --props=props/mysong.json --concurrency=4
```

`PackMV` 组件能力：
- 镜头 Ken Burns 运镜（推/拉/平移/上移）+ 12 帧叠化
- 收音机式片头信息卡（歌名 + 原唱 + AI 声明）
- 书法歌词嵌入画面：按短语断句、自动分列、字号自适应
- 按背景亮度自动选择深墨/米白 + 描边阴影

## 5. 音画合成

```bash
bash scripts/mv/make_mv.sh out/mysong.mp4 output/mysong.mp3 output/mysong_final.mp4 0
# 或一步到位：
python scripts/mv/render_song.py --config configs/songs/mysong.json
```

## 6. 验收清单

- [ ] 前奏完整保留（除非明确要求裁剪）
- [ ] 片头含歌名、原唱、AI 合成声明、非商用提示
- [ ] 歌词无作词/作曲/歌手名等杂质
- [ ] 长句按断句分列，无单字孤列
- [ ] 歌词颜色与背景对比清晰
- [ ] 音画时长一致、口型/字幕对轴
- [ ] 输出 1920×1080，AAC 256k 48kHz
