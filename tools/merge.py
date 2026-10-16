"""Merge _work/chunks/out_*.json into translations/he.json (English text -> Hebrew), validating ICU safety."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from validate import check

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}
bad = 0
for inp in sorted(glob.glob(os.path.join(ROOT, "_work/chunks/in_*.json"))):
    o = inp.replace("in_", "out_")
    if not os.path.exists(o):
        continue
    a = json.load(open(inp, encoding="utf8")); b = json.load(open(o, encoding="utf8"))
    for k, en in a.items():
        he = b.get(k)
        if check(en, he):
            bad += 1
        elif he != en:
            out[en] = he
path = os.path.join(ROOT, "translations/he.json")
json.dump(out, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=0, sort_keys=True)
print(f"{len(out)} translations written, {bad} rejected")
