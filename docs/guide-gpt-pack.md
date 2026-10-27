# 用 GPT 生成 MV 交付包（完整指导）

本流程把「歌名 + 时长 + 歌词」变成能直接喂流水线的分镜交付包。

## 一、准备输入信息

在跟 GPT 对话前，先填好这张表：

```
歌名：
原唱：
歌曲时长（精确到 0.01 秒）：
BPM / 曲风：
主题关键词（3–6 个）：
是否有故事/需要解说：否（默认只放歌词）
整体风格方向（示例）：
  - 江湖侠气：水墨、刀剑、风雪、孤影
  - 江南烟雨：画舫、雨、柳、青灰
  - 青春遗憾：城市雨夜、校服、路灯、暖黄
  - 苍茫山河：雪山、长河、风、留白
参考画面（可选）：
禁用元素（可选）：
必须出现的意象（可选）：
```

> 时长必须来自**最终音频文件**（用 `ffprobe 音频.mp3` 看 `Duration`），不要用平台页面标注的近似值。

## 二、分三步对话

### 第 1 步：先定风格与分镜大纲（不要急着出 JSON）

复制以下提示词：

```
你是国风 AI 音乐 MV 分镜师。我要为歌曲《{歌名}》制作一支 1920x1080、24fps、约 {时长} 秒的 MV。
风格方向：{风格}
主题关键词：{关键词}
请先输出：
1. 一段 style_guide 草案（主题、色板 HEX、材质、构图规则、意象清单、禁用元素）
2. 分镜大纲：按歌词段落分章，每章 3–8 镜，说明每镜的画面内容与情绪，不要写英文 prompt
先不要输出 JSON。
```

检查大纲：镜头是否覆盖前奏/间奏/尾奏、每章是否服务主题、有没有跑题。

### 第 2 步：确认大纲后，生成逐镜提示词 + 时间轴

```
风格与大纲确认，请输出可直接执行的交付包，严格按以下格式：
1. 逐镜提示词.json
2. 运镜时间轴_24fps.json
硬性要求：
- total_frames = round({时长} × 24)，所有镜头首尾相接、不重叠、不跳帧
- 每镜 2–10 秒，前奏/间奏/尾奏也要有画面
- positive_prompt_en 为英文单段 80–200 词，可直接喂 Flux，包含场景+主体+材质+光线+构图，并加 "no text, no calligraphy, no seal, no watermark"
- 人物只做背影/剪影，占画面 6–15% 高度，禁止五官特写
- 画面内不得出现任何可读文字
- 每镜给出 seed、motion（push_in / pull_out / pan_left / pan_right / drift_up）

字段格式（逐镜）：
shot_id, time_start, time_end, duration_seconds, lyric_hint, section, scene, subject,
positive_prompt_en, negative_prompt_en, composition, motion, seed

字段格式（时间轴）：
shot_id, start_frame, end_frame, duration_frames, time_start, time_end, motion,
crossfade_in_frames, crossfade_out_frames
```

### 第 3 步：自检 + 补 README

```
请检查：
1. 每镜时长是否在 2–10 秒
2. 时间轴是否首尾相接，末帧是否等于 total_frames
3. 镜头数量与时间轴数量是否一致
4. prompt 是否中英混排（若混排请重写为纯英文）
5. 是否出现文字、印章、人脸特写等禁用元素
修正后，再输出 README.md（主题说明、分章结构、字幕要求、验收清单）。
```

## 三、必须校验的硬指标

用下面命令校验（本仓库也提供 `build_mvprops.py` 会做部分检查）：

```python
import json
p = json.load(open("packs/<slug>/逐镜提示词.json", encoding="utf-8"))
t = json.load(open("packs/<slug>/运镜时间轴_24fps.json", encoding="utf-8"))
assert len(p["shots"]) == len(t["shots"])
last = 0
for s in t["shots"]:
    assert s["start_frame"] == last, "时间轴有断层"
    last = s["end_frame"]
assert last == t["total_frames"], "末帧 != total_frames"
assert t["total_frames"] == round(p["master_duration_seconds"] * t["fps"]), "帧数计算错误"
for s in p["shots"]:
    assert 2 <= s["duration_seconds"] <= 10, "镜头时长越界"
print("OK")
```

## 四、常见问题与纠正话术

| 问题 | 纠正话术 |
|---|---|
| 时间轴对不上时长 | 「末帧必须等于 round(时长×24)=X，请重算并保证首尾相接」 |
| 中英混排 prompt | 「positive_prompt_en 必须是纯英文单段，中文只保留在 scene 字段」 |
| 画面出现文字/印章 | 「画面内不能出现任何文字、书法、印章、水印，prompt 里要显式排除」 |
| 镜头太长（>10s） | 「每镜限制 2–10 秒，超长镜头拆成两镜，并用同一场景不同构图」 |
| 风格不统一 | 「所有 prompt 共享同一套风格前缀：{你的风格前缀}」 |
| 人物正脸 | 「人物只允许背影/剪影/远小，禁止五官特写」 |
| 漏了间奏画面 | 「间奏和尾奏也必须有画面，不能留空」 |
| 同一镜头内容重复 | 「相邻镜头需要有构图/景别/意象变化，避免重复」 |

## 五、交付包落地

把 GPT 输出的 4 个文件保存到：

```
packs/<slug>/
├─ 逐镜提示词.json
├─ 运镜时间轴_24fps.json
├─ style_guide.md
└─ README.md
```

然后进入 [`end-to-end-walkthrough.md`](end-to-end-walkthrough.md) 的第 5 步出图。

## 六、一条可直接复制的完整提示词（懒人版）

见仓库根目录示例与 `packs/PROMPT_TEMPLATE.md`，把表格信息替换后整段发送即可。
