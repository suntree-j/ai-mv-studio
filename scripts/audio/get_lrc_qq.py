import json
import os
import sys
import urllib.parse
import urllib.request

H = {"Referer": "https://y.qq.com", "User-Agent": "Mozilla/5.0"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=20).read().decode("utf-8", "ignore")


def search(q):
    url = "https://c.y.qq.com/soso/fcgi-bin/client_search_cp?" + urllib.parse.urlencode({"w": q, "format": "json", "n": 10})
    d = json.loads(get(url))
    return d["data"]["song"]["list"]


def lyric(songmid):
    url = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?" + urllib.parse.urlencode({"songmid": songmid, "format": "json", "nobase64": "1"})
    d = json.loads(get(url))
    return d.get("lyric", "")


q = sys.argv[1]
outdir = "/root/lrc"
os.makedirs(outdir, exist_ok=True)
for s in search(q):
    name = s["songname"]
    singers = "/".join(x["name"] for x in s.get("singer", []))
    print(s["songmid"], "|", name, "|", s["interval"], "s |", singers)
if len(sys.argv) > 2:
    mid = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else mid
    lrc = lyric(mid)
    path = os.path.join(outdir, name + ".lrc")
    open(path, "w", encoding="utf-8").write(lrc)
    print("saved", path, len(lrc))
    print(lrc[:500])
