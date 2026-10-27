import json
import os
import re
import sys

try:
    from PIL import Image
except Exception:
    Image = None

PACK_DIR = sys.argv[1]
SLUG = sys.argv[2]
OUT_PROPS = sys.argv[3]
LRC = sys.argv[4] if len(sys.argv) > 4 else ""
ARTIST_FALLBACK = {"tianhe": "银临/司南", "chuimie": "国风堂/司南"}
COMMON_NAMES = ["司南", "银临", "国风堂", "汐音社", "国风新语", "房东的猫", "小阿七", "Pig小优", "萧忆情Alex", "伦桑"]

shots_json = json.load(open(os.path.join(PACK_DIR, "逐镜提示词.json"), encoding="utf-8"))
tl_json = json.load(open(os.path.join(PACK_DIR, "运镜时间轴_24fps.json"), encoding="utf-8"))
fps = tl_json.get("fps", 24)
tl = {s["shot_id"]: s for s in tl_json["shots"]}

CREDIT_KEYS = ["作词", "作曲", "编曲", "和声", "混音", "母带", "制作", "制作人", "原制作人", "监制", "出品", "发行",
               "录音", "吉他", "电吉他", "贝斯", "鼓", "弦乐", "策划", "企划", "统筹", "配唱", "文案", "宣发",
               "题字", "曲绘", "封面", "OP", "SP", "原唱", "演唱", "翻唱", "分轨", "贴混", "未经许可", "纯音乐",
               "系列作品", "化用", "酷狗音乐", "国风新语", "尺八", "箫", "萧", "笛", "古筝", "琵琶", "二胡",
               "马头琴", "和音", "合音", "伴唱", "念白", "童声", "录音师", "混音师", "母带工程师", "人声编辑", "弦乐编写",
               "故事", "设计", "协力", "视觉", "插画", "监修", "录音棚", "工作室", "出品人", "策划人"]
SKIP_START = re.compile(r"^\s*(作词|作曲|编曲|和声|混音|母带|制作|制作人|原制作人|监制|出品|发行|录音|吉他|电吉他|贝斯|鼓|弦乐|策划|企划|统筹|配唱|文案|宣发|题字|曲绘|封面|OP|SP|演唱|原唱|翻唱|词|曲|分轨|贴混|未经许可|纯音乐)")

artist_names = list(COMMON_NAMES)
artist_meta = ""
lyrics_raw = []

if LRC and os.path.exists(LRC):
    lines = open(LRC, encoding="utf-8", errors="ignore").read().splitlines()
    for raw in lines:
        m = re.match(r"\[ar:(.*)\]", raw.strip())
        if m:
            artist_meta = m.group(1).strip()
            for part in re.split(r"[/、,，&]", artist_meta):
                part = part.strip()
                if part:
                    artist_names.append(part)
    for part in re.split(r"[/、,，&]", ARTIST_FALLBACK.get(SLUG, "")):
        part = part.strip()
        if part:
            artist_names.append(part)
    pat = re.compile(r"\[(\d+):(\d+)\.(\d+)\](.*)")
    for raw in lines:
        m = pat.match(raw.strip())
        if not m:
            continue
        t = int(m.group(1)) * 60 + int(m.group(2)) + int(m.group(3)) / (10 ** len(m.group(3)))
        text = m.group(4).strip()
        if not text:
            continue
        if SKIP_START.match(text):
            continue
        if any(k in text for k in CREDIT_KEYS):
            continue
        if re.fullmatch(r"[^：:]{1,12}[：:]", text):
            continue
        if (" - " in text and len(text) < 40) or text.startswith("-") or text.startswith("—") or text.endswith("-"):
            continue
        pm = re.match(r"^([^：:]{1,12})[：:]\s*(.*)$", text)
        if pm:
            prefix, rest = pm.group(1).strip(), pm.group(2).strip()
            if prefix in artist_names or prefix in ("合", "合唱", "独唱", "齐", "男", "女", "双"):
                text = rest
        text = text.strip()
        if not text:
            continue
        if lyrics_raw and lyrics_raw[-1][1] == text:
            continue
        lyrics_raw.append([t, text])

artist_meta = artist_meta or ARTIST_FALLBACK.get(SLUG, "")
start_time = 0.0  # 保留完整前奏，不做截断
start_frame = int(round(start_time * fps))
new_total = max(1, int(tl_json["total_frames"]) - start_frame)

props = {"song": shots_json.get("song", SLUG), "original_artist": artist_meta, "fps": fps,
         "total_frames": new_total, "audio_start_seconds": round(start_time, 3),
         "shots": [], "lyrics": []}

for s in shots_json["shots"]:
    sid = s["shot_id"]
    t = tl[sid]
    a = int(t["start_frame"]) - start_frame
    b = int(t["end_frame"]) - start_frame
    if b <= 0:
        continue
    a = max(0, a)
    rem = os.path.dirname(os.path.dirname(os.path.abspath(OUT_PROPS)))
    img_path = os.path.join(rem, "public", "mvimages", SLUG, sid + ".png")
    lum = 0.5
    try:
        if Image is not None and os.path.exists(img_path):
            im = Image.open(img_path).convert("L").resize((32, 18))
            px = list(im.getdata())
            lum = round(sum(px) / len(px) / 255.0, 3)
    except Exception:
        lum = 0.5
    props["shots"].append({"file": f"mvimages/{SLUG}/{sid}.png", "start": a, "end": b, "motion": t.get("motion", ""), "lum": lum})

for i, (t, text) in enumerate(lyrics_raw):
    end = lyrics_raw[i + 1][0] if i + 1 < len(lyrics_raw) else t + 5.0
    a = int(round(t * fps)) - start_frame
    b = int(round(end * fps)) - start_frame
    if b <= 0:
        continue
    props["lyrics"].append({"start": max(0, a), "end": max(a + 1, b), "text": text})

os.makedirs(os.path.dirname(os.path.abspath(OUT_PROPS)), exist_ok=True)
json.dump(props, open(OUT_PROPS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("props", OUT_PROPS, "shots", len(props["shots"]), "lyrics", len(props["lyrics"]),
      "frames", props["total_frames"], "audio_start", props["audio_start_seconds"], "artist", artist_meta)
