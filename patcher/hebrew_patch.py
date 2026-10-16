#!/usr/bin/env python3
r"""Adds a Hebrew (he-IL) UI language to Claude Desktop.

Everything is patched inside resources/ion-dist (the web UI), located by content,
not by file name, so it survives the hashed file names of new releases.

  hebrew_patch.py --app <dir containing resources\>  [--dest <patched copy>] [--revert] [--check]
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path

if getattr(sys, "frozen", False):
    ROOT = Path(sys._MEIPASS)           # PyInstaller bundle
else:
    ROOT = Path(__file__).resolve().parent.parent
MARK = ".hebrew-orig"
LOCALES_RE = re.compile(r'(\["en-US","de-DE"[^\]]*?"id-ID")\]')
NAMES_RE = re.compile(r'("id-ID":\{name:"Indonesian \(Indonesia\)",localName:"Indonesia \(Indonesia\)"\})(\};)')
HE_NAME = '"he-IL":{name:"Hebrew (Israel)",localName:"\u05E2\u05D1\u05E8\u05D9\u05EA (\u05D9\u05E9\u05E8\u05D0\u05DC)"}'
SCRIPT_TAG = '<script src="/assets/he-rtl.js"></script>'


def find_app():
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-AppxPackage | ? { $_.Name -like '*Claude*' -and $_.InstallLocation -like '*WindowsApps*' } | select -First 1).InstallLocation"],
            capture_output=True, text=True).stdout.strip()
        if out and (Path(out) / "app").is_dir():
            return Path(out) / "app"
    except Exception:
        pass
    return None


def backup(p: Path):
    b = p.with_name(p.name + MARK)
    if not b.exists():
        shutil.copy2(p, b)


def read(p): return p.read_text(encoding="utf-8")
def write(p, s): p.write_text(s, encoding="utf-8", newline="")


def patch(ion: Path, translations: dict):
    done = {"locale_lists": 0, "names": 0, "html": 0, "catalog": False}
    for js in (ion / "assets").rglob("*.js"):
        s = read(js)
        if '"id-ID"' not in s:
            continue
        n = s
        n, c1 = LOCALES_RE.subn(lambda m: m.group(1) + ',"he-IL"]', n)
        n, c2 = NAMES_RE.subn(lambda m: m.group(1) + "," + HE_NAME + m.group(2), n)
        if (c1 or c2) and '"he-IL"' not in s.replace(HE_NAME, ""):
            pass
        if n != s:
            backup(js); write(js, n)
            done["locale_lists"] += c1; done["names"] += c2
    shutil.copy2(ROOT / "assets" / "he-rtl.js", ion / "assets" / "he-rtl.js")
    for name in ("index.html", "frame-shell.html", "client-shell-v1.html"):
        h = ion / name
        if h.exists():
            s = read(h)
            if SCRIPT_TAG not in s and "</head>" in s:
                backup(h); write(h, s.replace("</head>", SCRIPT_TAG + "</head>", 1)); done["html"] += 1
    en = json.loads(read(ion / "i18n" / "en-US.json"))
    he = {k: translations[v] for k, v in en.items() if v in translations}
    (ion / "i18n" / "he-IL.json").write_text(json.dumps(he, ensure_ascii=False), encoding="utf-8")
    done["catalog"] = f"{len(he)}/{len(en)} strings"
    return done


def revert(ion: Path):
    n = 0
    for b in ion.rglob("*" + MARK):
        shutil.copy2(b, b.with_name(b.name[:-len(MARK)])); b.unlink(); n += 1
    for f in (ion / "assets" / "he-rtl.js", ion / "i18n" / "he-IL.json"):
        if f.exists(): f.unlink()
    return n


def is_admin():
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def elevate():
    import ctypes
    exe = sys.executable
    args = sys.argv[1:] if getattr(sys, "frozen", False) else [os.path.abspath(sys.argv[0])] + sys.argv[1:]
    ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, " ".join(f'"{a}"' for a in args), None, 1)
    sys.exit(0)


def unlock(ion: Path):
    """WindowsApps is owned by TrustedInstaller; take ownership and grant admins write access."""
    subprocess.run(["takeown", "/F", str(ion), "/R", "/A", "/D", "Y"], capture_output=True)
    subprocess.run(["icacls", str(ion), "/grant", "*S-1-5-32-544:(OI)(CI)F", "/T", "/C", "/Q"], capture_output=True)


def main():
    ap = argparse.ArgumentParser(description="Hebrew UI for Claude Desktop")
    ap.add_argument("--app", help="folder that contains resources/ (default: installed Claude package)")
    ap.add_argument("--revert", action="store_true", help="remove the Hebrew patch")
    ap.add_argument("--translations", default=str(ROOT / "translations" / "he.json"))
    a = ap.parse_args()
    app = Path(a.app) if a.app else find_app()
    if not app:
        sys.exit("Claude Desktop not found; pass --app")
    ion = app / "resources" / "ion-dist"
    if not ion.is_dir():
        sys.exit(f"missing {ion}")
    if not a.app:
        if not is_admin():
            elevate()
        unlock(ion)
    if a.revert:
        print("restored", revert(ion), "files")
    else:
        print(patch(ion, json.loads(read(Path(a.translations)))))
        print("Done. Restart Claude and choose Settings > Language > Hebrew.")
    if getattr(sys, "frozen", False):
        input("Press Enter to close...")


if __name__ == "__main__":
    main()
