import json
import sys
import urllib.parse
import urllib.request

HEADERS = {"Referer": "https://music.163.com", "User-Agent": "Mozilla/5.0"}


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")


def search(q):
    url = "https://music.163.com/api/search/get?" + urllib.parse.urlencode({"s": q, "type": 1, "limit": 10})
    d = json.loads(get(url))
    return d.get("result", {}).get("songs", [])


def lyric(sid):
    url = f"https://music.163.com/api/song/lyric?id={sid}&lv=-1&kv=-1&tv=-1"
    d = json.loads(get(url))
    return d.get("lrc", {}).get("lyric", "")


q = sys.argv[1]
for s in search(q):
    artists = "/".join(a["name"] for a in s.get("artists", []))
    print(s["id"], "|", s["name"], "|", s["duration"], "ms |", artists)
if len(sys.argv) > 2:
    sid = int(sys.argv[2])
    print("---LYRIC---")
    print(lyric(sid))
