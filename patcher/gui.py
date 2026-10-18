"""Hebrew GUI installer for Claude Desktop (pywebview + HTML, RTL).

  gui.py                      opens the installer window
  gui.py --app <dir>          same, but patches a copy (no admin / ownership changes) - for testing
  gui.py --auto | --revert    command-line mode (used by the optional scheduled task)
"""
import json, re, subprocess, sys
from pathlib import Path

import hebrew_patch as hp

CLI_FLAGS = {"--auto", "--revert", "--cli"}


def _app_override():
    if "--app" in sys.argv:
        i = sys.argv.index("--app")
        if i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return None


def _claude_running():
    try:
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq claude.exe", "/FO", "CSV", "/NH"],
                             capture_output=True, text=True).stdout
        return "claude.exe" in out.lower()
    except Exception:
        return False


class Api:
    def __init__(self):
        self.override = _app_override()

    def _app(self):
        return self.override or hp.find_app()

    def status(self):
        app = self._app()
        if not app or not (app / "resources" / "ion-dist").is_dir():
            return {"found": False}
        ion = app / "resources" / "ion-dist"
        m = re.search(r"Claude_([\d.]+)_", str(app))
        return {
            "found": True,
            "version": m.group(1) if m else "?",
            "patched": hp.is_patched(ion),
            "running": _claude_running(),
            "task": hp.task_exists() if not self.override else False,
            "can_task": bool(getattr(sys, "frozen", False)) and not self.override,
        }

    def _prepare(self, log):
        app = self._app()
        if not app:
            raise RuntimeError("Claude Desktop לא נמצא במחשב הזה.")
        ion = app / "resources" / "ion-dist"
        if not ion.is_dir():
            raise RuntimeError(f"לא נמצאה תיקיית הממשק: {ion}")
        if not self.override:
            if not hp.is_admin():
                raise RuntimeError("נדרשות הרשאות מנהל. הפעילו את המתקין בלחיצה ימנית ← הפעלה כמנהל.")
            log.append("לוקח בעלות על קבצי הממשק של Claude (נדרש כי הם בתיקייה מוגנת)…")
            hp.unlock(ion)
        return ion

    def install(self, with_task):
        log = []
        try:
            ion = self._prepare(log)
            log.append("מוסיף קבצי שפה וכיוון RTL (Claude לא נסגר)…")
            res = hp.patch(ion, json.loads(hp.read(hp.ROOT / "translations" / "he.json")))
            log.append(f"קטלוג עברית: {res['catalog']}")
            log.append(f"רשימות שפות שעודכנו: {res['locale_lists']}, דפי HTML: {res['html']}")
            if with_task and not self.override:
                log.append("משימה מתוזמנת נוצרה." if hp.install_task() else "לא הצלחתי ליצור את המשימה המתוזמנת.")
            elif not with_task and not self.override and hp.task_exists():
                hp.remove_task(); log.append("המשימה המתוזמנת הוסרה.")
            return {"ok": True, "log": log,
                    "summary": "קבצי העברית נוספו. Claude לא נסגר, כך שהחיבור והשיחות הפעילות נשארו כמו שהיו."}
        except Exception as e:
            log.append(f"שגיאה: {e}")
            return {"ok": False, "log": log, "error": str(e)}

    def uninstall(self):
        log = []
        try:
            ion = self._prepare(log)
            n = hp.revert(ion)
            log.append(f"שוחזרו {n} קבצים.")
            if not self.override:
                hp.remove_task(); log.append("המשימה המתוזמנת הוסרה (אם הייתה).")
            return {"ok": True, "log": log}
        except Exception as e:
            log.append(f"שגיאה: {e}")
            return {"ok": False, "log": log, "error": str(e)}


def main():
    if CLI_FLAGS & set(sys.argv[1:]):
        hp.main()
        return
    import webview
    html = (hp.ROOT / "patcher" / "gui_ui.html") if getattr(sys, "frozen", False) else (Path(__file__).parent / "gui_ui.html")
    webview.create_window("ממשק עברי עבור Claude", html=html.read_text(encoding="utf-8"),
                          js_api=Api(), width=640, height=800, min_size=(520, 600))
    webview.start()


if __name__ == "__main__":
    main()
