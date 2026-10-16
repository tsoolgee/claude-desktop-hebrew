"""Dev server: serves ion-dist with SPA fallback to index.html (for browser-pane tests)."""
import http.server, os, sys
root, port = sys.argv[1], int(sys.argv[2])
os.chdir(root)
class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        p = self.path.split("?")[0]
        if p.startswith("/i18n/dynamic/") and not os.path.exists("." + p):   # the app returns {} for missing catalogs
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b"{}"); return
        if not os.path.exists("." + p) or p.endswith("/"):
            if not p.startswith(("/assets", "/i18n")):
                self.path = "/index.html"
        super().do_GET()
http.server.ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
