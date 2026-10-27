# 架构

## 总体

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ 歌曲配置     │────▶│ 音频流水线        │────▶│ 音频成品 MP3     │
│ configs/*.json│    │ 分离→RVC→混音     │     │ output/*.mp3     │
└─────────────┘     └──────────────────┘     └─────────────────┘
        │                                              │
        ▼                                              │
┌─────────────┐     ┌──────────────────┐               │
│ GPT 交付包  │────▶│ 画面流水线        │               │
│ packs/<歌>/ │     │ Flux 出图         │               │
└─────────────┘     │ + 时间轴/歌词      │               │
                    └────────┬─────────┘               │
                             ▼                          ▼
                    ┌──────────────────┐     ┌─────────────────┐
                    │ Remotion 合成     │────▶│ 成片 MP4 1080p   │
                    └──────────────────┘     └─────────────────┘
```

## 模块

| 模块 | 代码 | 输入 | 输出 |
|---|---|---|---|
| 音色训练 | `scripts/audio/train_pipeline.sh` | 高质量原曲集 | RVC 模型 `.pth` |
| 歌曲转换 | `scripts/audio/convert.sh` + `mix_song.py` | 原曲、模型、配置 | 320k MP3 |
| LRC 获取 | `scripts/audio/get_lrc_qq.py` / `fetch_lyric_netease.py` | 歌名 | `.lrc` |
| 分镜包 | `packs/`（GPT 生成） | 歌名/时长/歌词 | 逐镜提示词/时间轴/style |
| 出图 | `scripts/mv/gen_flux.py` | 交付包 | `S01.png`… |
| 时间轴 | `scripts/mv/build_mvprops.py` | 交付包 + LRC | `props/<slug>.json` |
| 合成 | `remotion/src/PackMV.tsx` | props + 图片 | 无声视频 |
| 封装 | `scripts/mv/render_song.py` / `make_mv.sh` | 视频 + 音频 | 成片 MP4 |

## 关键设计

1. **配置驱动**：每首歌一个 JSON，字段见 `configs/song.example.json`
2. **交付包为契约**：GPT 输出固定 schema，流水线只消费不猜测
3. **可替换模型**：RVC / Flux / Remotion 均为外部依赖，可替换
4. **幂等**：出图按 `shot_id.png` 跳过已存在文件；渲染可重跑
5. **无素材耦合**：歌曲/图片/模型不进仓库

## 数据流字段

- `逐镜提示词.json`：shot_id / time_start / time_end / lyrics / scene / positive_prompt_en / negative_prompt_en / seed / motion
- `运镜时间轴_24fps.json`：fps / total_frames / shots[start_frame,end_frame,motion]
- `props/<slug>.json`：由上面两者 + LRC 合成（含 `original_artist`、`audio_start_seconds`、`lum`）
