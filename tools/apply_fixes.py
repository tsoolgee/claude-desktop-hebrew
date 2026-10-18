"""Apply reviewer corrections: _work/audit/fix_*.json ({English: Hebrew}) and _work/gaps_he.json into translations/he.json."""
import sys as _s; _s.stdout.reconfigure(encoding="utf8", errors="replace")
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from validate import check

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
path = os.path.join(ROOT, "translations", "he.json")
he = json.load(open(path, encoding="utf8"))
applied = rejected = 0
files = sorted(glob.glob(os.path.join(ROOT, "_work/audit/fix_*.json"))) + [os.path.join(ROOT, "_work/gaps_he.json")]
for f in files:
    if not os.path.exists(f):
        continue
    try:
        fx = json.load(open(f, encoding="utf8"))
    except Exception as e:
        print("skip", f, e); continue
    for en, t in fx.items():
        if check(en, t):
            rejected += 1; print("rejected:", en[:60], "->", check(en, t))
        else:
            he[en] = t; applied += 1
json.dump(he, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=0, sort_keys=True)
print(f"applied {applied}, rejected {rejected}, total {len(he)}")
