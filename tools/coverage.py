"""Which UI messages used by the web code have no Hebrew? usage: coverage.py <ion-dist dir>"""
import glob, json, re, sys

ion = sys.argv[1].rstrip("/\\") + "/"
en = json.load(open(ion + "i18n/en-US.json", encoding="utf8"))
he = json.load(open(ion + "i18n/he.json", encoding="utf8"))
Q = r'"(?:[^"\\]|\\.)*"'
A = re.compile(r"defaultMessage:(" + Q + r")\s*,\s*id:\"([^\"]+)\"")
B = re.compile(r"id:\"([^\"]+)\"\s*,\s*defaultMessage:(" + Q + r")")
used = {}
for f in glob.glob(ion + "assets/**/*.js", recursive=True):
    s = open(f, encoding="utf8", errors="ignore").read()
    for m in A.finditer(s):
        used[m.group(2)] = m.group(1)
    for m in B.finditer(s):
        used[m.group(1)] = m.group(2)

def txt(k):
    return en.get(k) or json.loads(used[k])

not_in_catalog = [k for k in used if k not in en]
no_he = [k for k in used if k in en and k not in he]
letters = re.compile(r"[A-Za-z]{4,}")
visible_no_he = {k: txt(k) for k in no_he if letters.search(re.sub(r"\{[^}]*\}", "", txt(k)))}
print("ids used in code:", len(used))
print("used but missing from the catalog (stay English):", len(not_in_catalog))
print("in catalog, no Hebrew:", len(no_he), "| of those with real English words:", len(visible_no_he))
json.dump({"not_in_catalog": {k: txt(k) for k in not_in_catalog}, "no_he": visible_no_he},
          open(ion.replace("/ion-dist/", "/") + "../../coverage_gaps.json" if False else "coverage_gaps.json", "w", encoding="utf8"),
          ensure_ascii=False, indent=0)
for t in list(visible_no_he.values())[:25]:
    print(" -", t[:90])
