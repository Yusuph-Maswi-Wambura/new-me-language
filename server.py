"""Tiny zero-dependency web server for the NovaLang playground."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from novalang import NovaError, run

ROOT = Path(__file__).parent


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/health":
            self.send_json(200, {"ok": True, "language": "NovaLang"})
            return
        if path == "/" or path == "/index.html":
            self.serve_file("web/index.html", "text/html; charset=utf-8")
            return
        if path == "/style.css":
            self.serve_file("web/style.css", "text/css; charset=utf-8")
            return
        if path == "/app.js":
            self.serve_file("web/app.js", "text/javascript; charset=utf-8")
            return
        self.send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/run":
            self.send_json(404, {"error": "Not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            output = run(payload.get("source", ""))
            self.send_json(200, {"ok": True, "output": output})
        except (json.JSONDecodeError, NovaError, TypeError, ValueError) as error:
            self.send_json(400, {"ok": False, "error": str(error)})

    def serve_file(self, relative_path: str, content_type: str) -> None:
        try:
            data = (ROOT / relative_path).read_bytes()
        except FileNotFoundError:
            self.send_json(404, {"error": "Asset not found"})
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format_string: str, *args: object) -> None:
        print(f"[novalang] {format_string % args}")


if __name__ == "__main__":
    port = 8000
    print(f"NovaLang playground: http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
