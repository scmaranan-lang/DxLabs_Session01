import json
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
STATIC_FILES = {
    "/static/app.css": ("static/app.css", "text/css; charset=utf-8"),
    "/static/app.js": ("static/app.js", "text/javascript; charset=utf-8"),
}
MAX_REQUEST_BYTES = 64 * 1024
MAX_NAMES = 500
MAX_NAME_LENGTH = 100


def normalize_names(names: Any) -> list[str]:
    if not isinstance(names, list):
        raise ValueError("Names must be provided as a list.")
    if not names or len(names) > MAX_NAMES:
        raise ValueError(f"Enter between 1 and {MAX_NAMES} names.")

    normalized = []
    for name in names:
        if not isinstance(name, str):
            raise ValueError("Every name must be text.")
        name = name.strip()
        if not name:
            raise ValueError("Names cannot be blank.")
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError(f"Each name must be {MAX_NAME_LENGTH} characters or fewer.")
        normalized.append(name)
    return normalized


def choose_name(names: Any) -> str:
    return random.SystemRandom().choice(normalize_names(names))


class NamePickerHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/":
            self._serve_file("index.html", "text/html; charset=utf-8")
            return

        static_file = STATIC_FILES.get(self.path)
        if static_file:
            self._serve_file(*static_file)
            return

        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        if self.path != "/api/pick":
            self.send_error(404, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "Invalid request size."})
            return

        if content_length < 1:
            self._send_json(400, {"error": "Request body is required."})
            return
        if content_length > MAX_REQUEST_BYTES:
            self._send_json(413, {"error": "Request body is too large."})
            return

        try:
            payload = json.loads(self.rfile.read(content_length))
            winner = choose_name(payload.get("names") if isinstance(payload, dict) else None)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "Request body must be valid JSON."})
            return
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return

        self._send_json(200, {"name": winner})

    def _serve_file(self, relative_path: str, content_type: str = "text/html; charset=utf-8") -> None:
        try:
            content = (ROOT / relative_path).read_bytes()
        except OSError:
            self.send_error(500, "Application file could not be read.")
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, status: int, payload: dict[str, str]) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    server = ThreadingHTTPServer(("127.0.0.1", 8000), NamePickerHandler)
    print("Random Name Picker is running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down Random Name Picker.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
