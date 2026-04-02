import json
import mimetypes
import os
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from trading_system.config import load_env_file, load_runtime_config
from trading_system.live_scanner import LiveScannerService
from trading_system.sample_provider import SampleMarketProvider
from trading_system.upstox_provider import UpstoxProvider


ROOT = Path(__file__).resolve().parent
STATIC_ROOT = ROOT / "web"


def build_scanner_service() -> LiveScannerService:
    load_env_file(ROOT / ".env")
    config = load_runtime_config(ROOT / "config" / "watchlist.json")

    token = os.environ.get("UPSTOX_ACCESS_TOKEN", "").strip()
    provider = SampleMarketProvider()
    
    # Only try Upstox if token is not the placeholder value
    if token and token != "your_upstox_access_token_here":
        try:
            print("Connecting to Upstox...")
            provider = UpstoxProvider(token)
            # Test the connection with a simple call
            print("Testing Upstox connection...")
            provider.resolve_query(config.market_index_query, prefer_equity=False)
            print("✓ Upstox connected successfully!")
        except Exception as e:
            print(f"✗ Upstox connection failed: {e}")
            print("→ Falling back to sample mode...")
            provider = SampleMarketProvider()
    else:
        print("No Upstox token found, using sample mode...")
    
    service = LiveScannerService(provider, config)
    
    try:
        print("Running initial scan...")
        service.run_scan()
        print("✓ Initial scan complete!")
    except Exception as e:
        print(f"⚠ Initial scan had issues: {e}")
        print("→ Scanner will continue and retry...")
    
    return service


SERVICE = build_scanner_service()


def background_loop() -> None:
    poll_seconds = SERVICE.config.scanner.poll_seconds
    while True:
        try:
            SERVICE.run_scan()
        except Exception as e:
            print(f"⚠ Scan error: {e}")
            # Continue running despite errors
        threading.Event().wait(poll_seconds)


threading.Thread(target=background_loop, daemon=True).start()


class DashboardHandler(BaseHTTPRequestHandler):
    server_version = "TradingDashboard/0.1"

    def _write_json(self, payload, status=HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_static(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self._write_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)
            return

        content = file_path.read_bytes()
        content_type, _ = mimetypes.guess_type(str(file_path))
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        if self.path in {"/", "/index.html"}:
            self._write_static(STATIC_ROOT / "index.html")
            return

        if self.path.startswith("/assets/"):
            relative_path = self.path.removeprefix("/assets/")
            self._write_static(STATIC_ROOT / relative_path)
            return

        if self.path == "/api/health":
            self._write_json(
                {
                    "status": "ok",
                    "provider": SERVICE.snapshot.get("provider"),
                    "mode": SERVICE.snapshot.get("mode"),
                }
            )
            return

        if self.path == "/api/dashboard":
            self._write_json(SERVICE.snapshot)
            return

        self._write_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path == "/api/scan-now":
            try:
                snapshot = SERVICE.run_scan()
            except Exception as exc:
                self._write_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._write_json(snapshot)
            return

        self._write_json({"error": "Not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> int:
    # For cloud hosting (Render, Railway, etc.), bind to 0.0.0.0 and use PORT env var
    # For local development, use 127.0.0.1:8010
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8010"))
    
    httpd = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"Live dashboard running at http://{host}:{port}")
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
