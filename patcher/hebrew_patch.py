#!/usr/bin/env python3
r"""Adds a Hebrew (he) UI language to Claude Desktop.

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


def run(cmd, **kw):
    """subprocess.run that never shows a console window (powershell, takeown, icacls, schtasks...)."""
    if os.name == "nt":
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0                                   # SW_HIDE
        kw.setdefault("startupinfo", si)
        kw.setdefault("creationflags", subprocess.CREATE_NO_WINDOW)
    return subprocess.run(cmd, **kw)


LOCALES_RE = re.compile(r'(\["en-US","de-DE"[^\]]*?"id-ID")\]')
NAMES_RE = re.compile(r'("id-ID":\{name:"Indonesian \(Indonesia\)",localName:"Indonesia \(Indonesia\)"\})(\};)')
HE_NAME = '"he":{name:"Hebrew",localName:"\\u05E2\\u05D1\\u05E8\\u05D9\\u05EA"}'
# The language picker lists only the catalogs the server offers; append Hebrew to that list (one memoised wrapper).
PICKER_RE = re.compile(r'(function \w+\(\{localeNames:\w+,\.\.\.(\w+)\}\)\{let \w+=)(\w+)\(\2\);')
PICKER_WRAP = '(x=>{if(!Array.isArray(x))return x;let m=(globalThis.__heM??=new WeakMap),r=m.get(x);return r||(r=x.includes("he")?x:[...x,"he"],m.set(x,r),r)})('
# Choosing Hebrew must not depend on the server accepting the locale (it does not offer Hebrew): skip that call for "he".
SWITCH_RE = re.compile(r'try\{await (\w+)\(\{locale:(\w+)\}\)\}catch\((\w+)\)\{')
SCRIPT_TAG = '<script src="/assets/he-rtl.js"></script>'


def find_app():
    try:
        out = run(
            ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-NonInteractive", "-Command",
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


def write_bytes(p: Path, data: bytes):
    """Atomic when possible (temp file + replace), so a running Claude never reads a half-written file.
    Never touches processes or user data: a live Claude session stays connected while files are swapped."""
    tmp = p.with_name(p.name + ".hebrew-tmp")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, p)
    except PermissionError:
        try: tmp.unlink()
        except OSError: pass
        p.write_bytes(data)          # file held open by Claude without share-delete: overwrite in place


def write(p, s): write_bytes(p, s.encode("utf-8"))


def patch(ion: Path, translations: dict):
    """Order matters for a running app: first add the catalogs and the RTL script (nothing references them yet),
    and only then switch on the locale lists, so Claude never sees a language entry without its catalog."""
    done = {"locale_lists": 0, "names": 0, "html": 0, "picker": 0, "switch": 0, "catalog": False}
    remove_legacy(ion)
    for b in ion.rglob("*" + MARK):                       # start from pristine files, whatever an older version of this tool did
        try: write_bytes(b.with_name(b.name[:-len(MARK)]), b.read_bytes())
        except OSError: pass
    write_bytes(ion / "assets" / "he-rtl.js", (ROOT / "assets" / "he-rtl.js").read_bytes())
    en = json.loads(read(ion / "i18n" / "en-US.json"))
    he = {k: translations[v] for k, v in en.items() if v in translations}
    extra = ROOT / "translations" / "extra_ids.json"      # messages used in code but absent from the shipped catalog (by id)
    if extra.exists():
        he.update(json.loads(read(extra)))
    write_bytes(ion / "i18n" / "he.json", json.dumps(he, ensure_ascii=False).encode("utf-8"))
    done["catalog"] = f"{len(he)}/{len(en)} strings"
    res = ion.parent                       # resources/: the desktop shell (main process) reads its own catalogs here
    nat_src = res / "en-US.json"
    if nat_src.exists():
        nen = json.loads(read(nat_src))
        nhe = {k: translations[v] for k, v in nen.items() if isinstance(v, str) and v in translations}
        write_bytes(res / "he.json", json.dumps(nhe, ensure_ascii=False, indent=2).encode("utf-8"))
        done["native"] = f"{len(nhe)}/{len(nen)} strings"
    dyn_src = ion / "i18n" / "dynamic" / "en-US.json"
    if dyn_src.exists():
        den = json.loads(read(dyn_src))
        dhe = {k: translations[v] for k, v in den.items() if isinstance(v, str) and v in translations}
        write_bytes(ion / "i18n" / "dynamic" / "he.json", json.dumps(dhe, ensure_ascii=False).encode("utf-8"))
    for js in (ion / "assets").rglob("*.js"):
        s = read(js)
        if '"id-ID"' not in s:
            continue
        n = s
        n, c1 = LOCALES_RE.subn(lambda m: m.group(1) + ',"he"]', n)
        n, c2 = NAMES_RE.subn(lambda m: m.group(1) + "," + HE_NAME + m.group(2), n)
        n, c3 = PICKER_RE.subn(lambda m: m.group(1) + PICKER_WRAP + m.group(3) + "(" + m.group(2) + "));", n)
        c4 = 0
        if "switchLocale:async" in n:
            n, c4 = SWITCH_RE.subn(lambda m: "try{(" + m.group(2) + '==="he")||await ' + m.group(1) + "({locale:" + m.group(2) + "})}catch(" + m.group(3) + "){", n, count=1)
        if n != s:
            backup(js); write(js, n)
            done["locale_lists"] += c1; done["names"] += c2; done["picker"] += c3; done["switch"] += c4
    for name in ("index.html", "frame-shell.html", "client-shell-v1.html"):
        h = ion / name
        if h.exists():
            s = read(h)
            if SCRIPT_TAG not in s and "</head>" in s:
                backup(h); write(h, s.replace("</head>", SCRIPT_TAG + "</head>", 1)); done["html"] += 1
    return done


LEGACY = ("he-IL.json",)


def remove_legacy(ion: Path):
    for f in (ion / "i18n" / "he-IL.json", ion / "i18n" / "dynamic" / "he-IL.json", ion.parent / "he-IL.json"):
        try:
            if f.exists(): f.unlink()
        except OSError:
            pass


def revert(ion: Path):
    remove_legacy(ion)
    n = 0
    for b in ion.rglob("*" + MARK):
        shutil.copy2(b, b.with_name(b.name[:-len(MARK)])); b.unlink(); n += 1
    for f in (ion / "assets" / "he-rtl.js", ion / "i18n" / "he.json", ion / "i18n" / "dynamic" / "he.json", ion.parent / "he.json"):
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
    run(["takeown", "/F", str(ion), "/R", "/A", "/D", "Y"], capture_output=True)
    run(["icacls", str(ion), "/grant", "*S-1-5-32-544:(OI)(CI)F", "/T", "/C", "/Q"], capture_output=True)
    res = ion.parent   # the folder itself only (no /R, no inheritance flags): enough to add resources/he.json
    run(["takeown", "/F", str(res), "/A"], capture_output=True)
    run(["icacls", str(res), "/grant", "*S-1-5-32-544:F", "/C", "/Q"], capture_output=True)


TASK = "ClaudeHebrewPatch"


def is_patched(ion: Path):
    return ((ion / "i18n" / "he.json").exists() and (ion / "assets" / "he-rtl.js").exists()
            and ((ion.parent / "en-US.json").exists() <= (ion.parent / "he.json").exists()))


def task_exists():
    return run(["schtasks", "/Query", "/TN", TASK], capture_output=True).returncode == 0


def install_task():
    """Opt-in only: re-run this exe at logon and every 3 hours with --auto (patches only if a Claude update removed the patch)."""
    exe = sys.executable
    ps = (f"$a=New-ScheduledTaskAction -Execute '{exe}' -Argument '--auto';"
          "$t=@((New-ScheduledTaskTrigger -AtLogOn),(New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 3)));"
          "$p=New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest -LogonType Interactive;"
          "$s=New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 10);"
          f"Register-ScheduledTask -TaskName {TASK} -Action $a -Trigger $t -Principal $p -Settings $s -Force | Out-Null")
    return run(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-NonInteractive", "-Command", ps], capture_output=True).returncode == 0


def remove_task():
    run(["schtasks", "/Delete", "/TN", TASK, "/F"], capture_output=True)


def ask_yes_no(q):
    try:
        return input(q + " [y/N] ").strip().lower() in ("y", "yes", "כן")
    except EOFError:
        return False


def main():
    ap = argparse.ArgumentParser(description="Hebrew UI for Claude Desktop")
    ap.add_argument("--app", help="folder that contains resources/ (default: installed Claude package)")
    ap.add_argument("--revert", action="store_true", help="remove the Hebrew patch (and the update task)")
    ap.add_argument("--auto", action="store_true", help="silent mode used by the scheduled task")
    ap.add_argument("--translations", default=str(ROOT / "translations" / "he.json"))
    a = ap.parse_args()
    app = Path(a.app) if a.app else find_app()
    if not app:
        sys.exit("Claude Desktop not found; pass --app")
    ion = app / "resources" / "ion-dist"
    if not ion.is_dir():
        sys.exit(f"missing {ion}")
    if a.auto and is_patched(ion):
        return
    if not a.app:
        if not is_admin():
            elevate()
        unlock(ion)
    if a.revert:
        print("restored", revert(ion), "files")
        if not a.app:
            remove_task()
    else:
        print(patch(ion, json.loads(read(Path(a.translations)))))
        print("Done. Claude was NOT closed or restarted, so your signed-in session and any running work stay connected.")
        print("To see Hebrew: fully quit Claude (also from the tray) and open it again, then Settings > Language > Hebrew.")
        if not a.app and not a.auto and getattr(sys, "frozen", False) and not task_exists():
            if ask_yes_no("Re-apply the patch automatically after Claude updates (scheduled task, runs at logon and every 3 hours)?"):
                print("Task installed." if install_task() else "Could not install the task.")
    if getattr(sys, "frozen", False) and not a.auto:
        input("Press Enter to close...")


if __name__ == "__main__":
    main()
