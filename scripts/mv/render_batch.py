#!/usr/bin/env python3
"""批量渲染：遍历 configs/songs/*.json 逐首渲染。

用法:
  python scripts/mv/render_batch.py [--configs configs/songs] [--only song1,song2]
"""
import argparse
import glob
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


ap = argparse.ArgumentParser()
ap.add_argument("--configs", default=os.path.join(BASE, "configs", "songs"))
ap.add_argument("--only", default="", help="只渲染指定 slug，逗号分隔")
args = ap.parse_args()
only = set(x.strip() for x in args.only.split(",") if x.strip())

files = sorted(glob.glob(os.path.join(args.configs, "*.json")))
for f in files:
    slug = os.path.splitext(os.path.basename(f))[0]
    if only and slug not in only:
        continue
    print("=" * 50)
    print("RENDER", slug)
    r = subprocess.run([sys.executable, os.path.join(BASE, "scripts", "mv", "render_song.py"), "--config", f])
    print("RESULT", slug, "ok" if r.returncode == 0 else "failed")
print("ALL_DONE")
