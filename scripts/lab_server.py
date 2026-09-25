from __future__ import annotations

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class State:
    lock = threading.Lock()
    count = 0


class Handler(BaseHTTPRequestHandler):
    server_version = "EgressBenchLab/0.1"

    def _reply(self, status: int, payload: dict, delay_ms: int = 0):
        if delay_ms:
            time.sleep(delay_ms / 1000)
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        with State.lock:
            State.count += 1
            n = State.count

        if self.path.startswith("/ok"):
            self._reply(200, {"ok": True, "request": n})
        elif self.path.startswith("/slow"):
            self._reply(200, {"ok": True, "request": n, "slow": True}, delay_ms=250)
        elif self.path.startswith("/rate-limit"):
            status = 429 if n % 5 == 0 else 200
            self._reply(status, {"ok": status == 200, "request": n, "simulated": True})
        elif self.path.startswith("/forbidden"):
            self._reply(403, {"ok": False, "request": n, "simulated": True})
        else:
            self._reply(404, {"ok": False, "request": n})

    def log_message(self, fmt, *args):
        return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Lab server: http://{args.host}:{args.port}")
    print("Endpoints: /ok /slow /rate-limit /forbidden")
    server.serve_forever()


if __name__ == "__main__":
    main()
