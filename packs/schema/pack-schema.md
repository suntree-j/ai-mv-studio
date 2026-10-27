# 交付包规范（Pack Schema）

每个交付包放在 `packs/<slug>/`，至少包含 4 个文件。本规范由 GPT（或任何 LLM）按模板生成，流水线只消费该格式。

## 1. `逐镜提示词.json`

```json
{
  "song": "歌名",
  "artist": "原唱",
  "fps": 24,
  "total_frames": 5760,
  "master_duration_seconds": 240.0,
  "shots": [
    {
      "shot_id": "S01",
      "time_start": 0.0,
      "time_end": 8.0,
      "duration_seconds": 8.0,
      "lyric_hint": ["关键词1", "关键词2"],
      "section": "序章",
      "scene": "中文场景描述",
      "subject": "画面主体",
      "positive_prompt_en": "English Flux prompt, single paragraph",
      "negative_prompt_en": "text, letters, watermark, close-up face",
      "composition": "构图说明（人物位置/留白）",
      "motion": "push_in",
      "seed": 12345
    }
  ]
}
```

## 2. `运镜时间轴_24fps.json`

```json
{
  "fps": 24,
  "total_frames": 5760,
  "crossfade_frames_default": 12,
  "shots": [
    {
      "shot_id": "S01",
      "start_frame": 0,
      "end_frame": 192,
      "duration_frames": 192,
      "time_start": 0.0,
      "time_end": 8.0,
      "motion": "push_in",
      "crossfade_in_frames": 0,
      "crossfade_out_frames": 12
    }
  ]
}
```

约束：
- `total_frames = round(master_duration_seconds × fps)`
- 每镜 `start_frame` 等于上一镜 `end_frame`，首镜 0，末镜 total_frames

## 3. `style_guide.md`

必须包含：
- 主题一句话
- 色板（HEX）
- 材质/笔触
- 构图规则（留白、人物比例）
- 意象清单
- 禁用元素

## 4. `README.md`

- 主题说明
- 分镜结构
- 字幕要求（歌词 / 是否解说）
- 验收清单

## 镜头规则

| 规则 | 说明 |
|---|---|
| 时长 | 每镜 2–10 秒 |
| 连续性 | 时间轴首尾相接，不重叠不跳帧 |
| prompt | 英文单段，80–200 词 |
| 人物 | 背影/剪影，6–15% 画面高度，禁止五官特写 |
| 文字 | 画面内不得出现任何可读文字 |

## 运镜取值

`push_in` / `pull_out` / `pan_left` / `pan_right` / `drift_up`（PackMV 组件会映射到缩放/位移）
