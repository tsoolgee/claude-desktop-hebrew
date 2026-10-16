"""Validate Hebrew translations against English ICU messages. usage: validate.py in.json out.json -> prints failing ids"""
import json, re, sys

ARG = re.compile(r"\{\s*([A-Za-z0-9_]+)")
TAG = re.compile(r"</?([A-Za-z][A-Za-z0-9]*)\s*/?>")
KW = re.compile(r"(?:,\s*(?:plural|select|selectordinal)\s*,)")

def sig(s):
    return (sorted(set(ARG.findall(s))), sorted(TAG.findall(s)))

def balanced(s):
    d = 0
    for c in s:
        d += (c == "{") - (c == "}")
        if d < 0: return False
    return d == 0

def check(en, he):
    if not isinstance(he, str) or not he.strip(): return "empty"
    if not balanced(he): return "braces"
    a, b = sig(en), sig(he)
    if a[0] != b[0]: return f"args {a[0]} vs {b[0]}"
    if a[1] != b[1]: return f"tags {a[1]} vs {b[1]}"
    if KW.search(en) and "other" not in he: return "plural-other-missing"
    if en.count("{") != he.count("{"): return "brace-count"
    return None

if __name__ == "__main__":
    en = json.load(open(sys.argv[1], encoding="utf8")); he = json.load(open(sys.argv[2], encoding="utf8"))
    bad = {}
    for k, v in en.items():
        r = check(v, he.get(k))
        if r: bad[k] = r
    print(json.dumps({"total": len(en), "bad": len(bad), "ids": bad}, ensure_ascii=False))
