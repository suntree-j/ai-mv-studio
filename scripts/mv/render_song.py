#!/usr/bin/env python3
"""单首歌 MV 渲染：props → Remotion → ffmpeg 合成（音频+视频）。

用法:
  python scripts/mv/render_song.py --config configs/songs/mysong.json
环境变量:
  REMOTION_DIR   Remotion 工程目录（默认 ./remotion）
  FFMPEG         ffmpeg 路径（默认 ffmpeg）
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REM = os.environ.get("REMOTION_DIR", os.path.join(BASE, "remotion"))
FF = os.environ.get("FFMPEG", "ffmpeg")


def prop(props, key, default=None):
    return props.get(key, default)


ap = argparse.ArgumentParser()
ap.add_argument("--config", required=True)
args = ap.parse_args()
cfg = json.load(open(args.config, encoding="utf-8"))
slug = cfg["slug"]
pack = os.path.join(BASE, cfg["pack"]) if not os.path.isabs(cfg["pack"]) else cfg["pack"]
props_dir = os.path.join(REM, "props")
image_dir = os.path.join(REM, "public", "mvimages", slug)
assets_img = os.path.join(BASE, "assets", slug)
os.makedirs(props_dir, exist_ok=True)
os.makedirs(image_dir, exist_ok=True)
if os.path.isdir(assets_img):
    for f in os.listdir(assets_img):
        if f.endswith(".png"):
            shutil.copy2(os.path.join(assets_img, f), os.path.join(image_dir, f))

props = os.path.join(props_dir, f"{slug}.json")
lrc = cfg.get("lrc", "")
subprocess.run([sys.executable, os.path.join(BASE, "scripts", "mv", "build_mvprops.py"),
                pack, slug, props, lrc], check=True)

data = json.load(open(props, encoding="utf-8"))
outv = os.path.join(REM, "out", f"{slug}.mp4")
os.makedirs(os.path.dirname(outv), exist_ok=True)
cmd = f'cd /d "{REM}" && npx remotion render src/index.ts PackMV "out/{slug}.mp4" --props="props/{slug}.json" --concurrency=4'
print("render:", cmd)
if subprocess.run(cmd, shell=True).returncode != 0:
    sys.exit("render failed")

audio_in = os.path.join(BASE, cfg["output_audio"]) if not os.path.isabs(cfg["output_audio"]) else cfg["output_audio"]
final = os.path.join(BASE, cfg.get("output_video", f"output/{slug}.mp4"))
os.makedirs(os.path.dirname(final), exist_ok=True)
ss = data.get("audio_start_seconds", 0)
subprocess.run([FF, "-y", "-hide_banner", "-loglevel", "error", "-ss", str(ss), "-i", audio_in, "-i", outv,
                "-map", "1:v:0", "-map", "0:a:0", "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-b:a", "256k",
                "-shortest", "-movflags", "+faststart", final], check=True)
print("DONE", final)
