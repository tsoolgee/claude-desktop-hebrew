"""Dev server: serves ion-dist with SPA fallback to index.html (for browser-pane tests)."""
import http.server, os, sys
root, port = sys.argv[1], int(sys.argv[2])
os.chdir(root)
class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        p = self.path.split("?")[0]
        if not os.path.exists("." + p) or p.endswith("/"):
            if not p.startswith(("/assets", "/i18n")):
                self.path = "/index.html"
        super().do_GET()
http.server.ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
