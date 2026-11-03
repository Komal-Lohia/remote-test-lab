"""A fake IP camera: http://localhost:8080/shot.jpg shows every fake board and its LED."""
import io
import json
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from PIL import Image, ImageDraw

STATE_DIR = Path(__file__).resolve().parent / "state"


def draw_frame():
    boards = [json.loads(p.read_text()) for p in sorted(STATE_DIR.glob("*.json"))]
    img = Image.new("RGB", (640, 120 + 110 * max(len(boards), 1)), "#1b2a49")
    d = ImageDraw.Draw(img)
    d.text((20, 20), f"cam-01  {datetime.now():%Y-%m-%d %H:%M:%S}", fill="white")
    for i, b in enumerate(boards):
        y = 70 + i * 110
        d.rectangle([20, y, 620, y + 90], outline="#9fd8e0", width=2)
        d.text((40, y + 15), f"{b['name']}   firmware {b['version']}", fill="white")
        stale = time.time() - b["updated"] > 600
        status = "HUNG" if b["hung"] else ("NO DATA" if stale else "running")
        d.text((40, y + 45), f"status: {status}", fill="#ffb3b3" if status != "running" else "#b7f0c0")
        colour = "#3ddc84" if b["led"] else "#444444"
        d.ellipse([540, y + 25, 580, y + 65], fill=colour, outline="white")
        d.text((535, y + 70), "LED", fill="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/shot.jpg":
            self.send_error(404)
            return
        body = draw_frame()
        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass                                   # keep the terminal quiet


if __name__ == "__main__":
    print("fake camera on http://localhost:8080/shot.jpg  (Ctrl+C to stop)", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
