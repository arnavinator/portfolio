#!/usr/bin/env python3
"""Preview the portfolio locally (default http://localhost:8000).

Unlike `python3 -m http.server`, this answers HTTP Range requests (Safari won't
play <video> without them), disables caching so edits show up on refresh, and
only listens on localhost.
"""
import argparse
import http.server
import os
import re
import sys
import webbrowser
from functools import partial

ROOT = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_head(self):
        self.range_len = None
        path = self.translate_path(self.path)
        m = re.fullmatch(r"bytes=(\d+)-(\d*)", self.headers.get("Range", ""))
        if not (m and os.path.isfile(path)):
            return super().send_head()
        size = os.path.getsize(path)
        start, end = int(m[1]), min(int(m[2] or size - 1), size - 1)
        if start > end:  # unsatisfiable or malformed; ignoring Range is allowed
            return super().send_head()
        f = open(path, "rb")
        f.seek(start)
        self.range_len = end - start + 1
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(self.range_len))
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        if self.range_len is None:
            return super().copyfile(source, outputfile)
        remaining = self.range_len
        while remaining and (chunk := source.read(min(remaining, 1 << 16))):
            outputfile.write(chunk)
            remaining -= len(chunk)

    def handle(self):
        try:
            super().handle()
        except ConnectionError:
            pass  # browser dropped a video stream mid-transfer (e.g. navigated away)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", nargs="?", type=int, default=8000)
    parser.add_argument("--no-open", action="store_true", help="don't open a browser tab")
    args = parser.parse_args()

    try:
        server = http.server.ThreadingHTTPServer(
            ("127.0.0.1", args.port), partial(Handler, directory=ROOT))
    except OSError as e:
        sys.exit(f"Can't use port {args.port} ({e.strerror}); pass another, e.g. {args.port + 1}")

    url = f"http://localhost:{args.port}/"
    print(f"Serving {ROOT} at {url} (Ctrl-C to stop)", flush=True)
    if not args.no_open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
