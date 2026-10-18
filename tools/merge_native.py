"""Merge _work/n/out_*.json (native-shell strings) into translations/he.json (English text -> Hebrew)."""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from validate import check

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, "translations", "he.json")
he = json.load(open(path, encoding="utf8"))
added = bad = 0
for inp in sorted(glob.glob(os.path.join(ROOT, "_work/n/in_*.json"))):
    out = inp.replace("in_", "out_")
    if not os.path.exists(out):
        continue
    a = json.load(open(inp, encoding="utf8")); b = json.load(open(out, encoding="utf8"))
    for k, en in a.items():
        t = b.get(k)
        if check(en, t): bad += 1
        elif t != en: he[en] = t; added += 1
json.dump(he, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=0, sort_keys=True)
print(f"added {added}, rejected {bad}, total {len(he)}")
