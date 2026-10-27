#!/usr/bin/env python3
"""批量按「逐镜提示词.json」调用 ComfyUI(Flux) 出图。

用法:
  python scripts/mv/gen_flux.py --pack packs/mysong --out remotion/public/mvimages/mysong [--limit 1]
环境变量:
  COMFY_URL   ComfyUI 服务地址（默认 http://127.0.0.1:8188）
  FLUX_UNET   UNET 权重文件名（默认 flux1-dev-fp8.safetensors）
"""
import argparse
import json
import os
import time
import urllib.parse
import urllib.request

BASE = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")
UNET = os.environ.get("FLUX_UNET", "flux1-dev-fp8.safetensors")
W, H = 1536, 864


def post(path, data):
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))


def build(shot, outname):
    pos = shot["positive_prompt_en"]
    neg = shot.get("negative_prompt_en", "")
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "fp8_e4m3fn"}},
        "2": {"class_type": "DualCLIPLoader", "inputs": {"clip_name1": "t5xxl_fp8_e4m3fn.safetensors", "clip_name2": "clip_l.safetensors", "type": "flux"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "ae.safetensors"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["2", 0]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["2", 0]}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "7": {"class_type": "KSampler", "inputs": {"model": ["10", 0], "seed": int(shot.get("seed", 1)), "steps": 20, "cfg": 1.0,
                                                    "sampler_name": "euler", "scheduler": "simple",
                                                    "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["6", 0], "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "mvgen/" + outname + "/" + shot["shot_id"]}},
        "10": {"class_type": "ModelSamplingFlux", "inputs": {"model": ["1", 0], "max_shift": 1.15, "base_shift": 0.5, "width": W, "height": H}},
    }


ap = argparse.ArgumentParser()
ap.add_argument("--pack", required=True, help="交付包目录（含逐镜提示词.json）")
ap.add_argument("--out", required=True, help="图片输出目录")
ap.add_argument("--limit", type=int, default=0, help="只生成前 N 张（测试用）")
args = ap.parse_args()

os.makedirs(args.out, exist_ok=True)
pack = json.load(open(os.path.join(args.pack, "逐镜提示词.json"), encoding="utf-8"))
shots = pack["shots"][: args.limit] if args.limit else pack["shots"]
outname = os.path.basename(os.path.abspath(args.out))

for shot in shots:
    sid = shot["shot_id"]
    out = os.path.join(args.out, sid + ".png")
    if os.path.exists(out) and os.path.getsize(out) > 1024:
        print("skip", sid)
        continue
    t0 = time.time()
    try:
        pid = post("/prompt", {"prompt": build(shot, outname)})["prompt_id"]
    except Exception as e:
        print("submit fail", sid, e)
        continue
    for _ in range(600):
        hist = json.load(urllib.request.urlopen(BASE + "/history/" + pid))
        if pid in hist:
            imgs = []
            for node in hist[pid]["outputs"].values():
                imgs += node.get("images", [])
            if imgs:
                q = urllib.parse.urlencode({"filename": imgs[0]["filename"], "subfolder": imgs[0].get("subfolder", ""), "type": "output"})
                open(out, "wb").write(urllib.request.urlopen(BASE + "/view?" + q).read())
                print("done", sid, round(time.time() - t0, 1), "s")
                break
        time.sleep(2)
    else:
        print("timeout", sid)
print("GEN_DONE")
