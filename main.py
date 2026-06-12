from flask import Flask, abort, Response, send_file
from pathlib import Path
from html import escape
import shutil
import subprocess
app = Flask(__name__)
losvideos = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".mpg", ".mpeg"}
video_paths = []
eatingthumbs = Path(__file__).parent / "thumbs"
eatingthumbs.mkdir(exist_ok=True)
def scan_videos(folder: Path):
    if not folder.exists() or not folder.is_dir():
        return []
    return sorted(
        [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in losvideos],
        key=lambda p: p.name.lower(),
    )
def makedavidtitle(video_path: Path) -> str:
    return video_path.stem.replace("_", " ").replace("-", " ").title()
def getthetypeig(video_path: Path) -> str:
    ext = video_path.suffix.lower()
    if ext == ".mp4":
        return "video/mp4"
    if ext == ".mkv":
        return "video/x-matroska"
    if ext == ".mov":
        return "video/quicktime"
    if ext == ".webm":
        return "video/webm"
    return "video/mp4"


def yessythumb(video_path: Path, index: int) -> Path:
    safe_name = "".join(ch if ch.isalnum() else "_" for ch in video_path.stem)[:60]
    thumb_path = eatingthumbs / f"{index}_{safe_name}.jpg"
    if thumb_path.exists():
        return thumb_path

    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        cmd = [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-ss",
            "00:00:02",
            "-vframes",
            "1",
            "-vf",
            "scale=320:180:force_original_aspect_ratio=decrease",
            str(thumb_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and thumb_path.exists():
            return thumb_path

    fallback_path = eatingthumbs / f"{index}_{safe_name}.svg"
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='320' height='180'>
  <rect width='100%' height='100%' fill='#111827'/>
  <rect x='20' y='20' width='280' height='140' rx='16' fill='#1f2937'/>
  <circle cx='160' cy='90' r='42' fill='#ef4444'/>
  <polygon points='150,70 150,110 182,90' fill='white'/>
  <text x='160' y='152' text-anchor='middle' font-family='Arial, sans-serif' font-size='18' fill='white'>{escape(video_path.name)}</text>
</svg>"""
    fallback_path.write_text(svg, encoding="utf-8")
    return fallback_path


def iiii():
    global video_paths
    inpr = input("folder path pls? ").strip()
    folder = Path(inpr)
    video_paths[:] = scan_videos(folder)
    if video_paths:
        print("ok it should work")
    else:
        print("aw no work")
    return folder


@app.route("/")
def main():
    cards = []
    for index, video_path in enumerate(video_paths):
        title = makedavidtitle(video_path)
        thumb_path = yessythumb(video_path, index)
        thumb_url = f"/thumb/{index}"
        cards.append(
            f"""
            <a class="card" href="/watch/{index}">
              <img src="{thumb_url}" alt="{escape(title)}">
              <div class="card-body">
                <h3>{escape(title)}</h3>
              </div>
            </a>
            """
        )
    if not cards:
        cards.append("<p class='empty'>nothing (why)</p>")
    page = f"""
<body>
  <div class='page'>
    <div class='grid'>
      {''.join(cards)}
    </div>
  </div>
</body>
</html>"""
    return page


@app.route("/watch/<int:index>")
def watch_video(index):
    if 0 <= index < len(video_paths):
        video_path = video_paths[index]
        title = makedavidtitle(video_path)
        mime_type = getthetypeig(video_path)
        return f"""

<head>
  <title>{escape(title)}</title>
      <style>.player{{
  display: inline-block;
  width: min(100%, 900px);
  max-width: 100%;
  overflow: hidden;
  border-radius: 16px;
  background: #000;
}}
.player video{{
  display: block;
  width: 100%;
  max-width: 100%;
  max-height: 70vh;
  height: auto;
  object-fit: contain;
  border-radius: 16px;
}}</style>
</head>
<body>
  <div class='player'>
    <a href='/'>go back</a>
    <h1>{escape(title)}</h1>
    <br></br>
    <video controls autoplay preload='metadata' poster='/thumb/{index}'>
      <source src='/video/{index}' type='{mime_type}'>
      your browser does not support the video tag lol imagine
    </video>
  </div>
</body>
</html>"""
    abort(404)
@app.route("/thumb/<int:index>")
def thumb(index):
    if 0 <= index < len(video_paths):
        video_path = video_paths[index]
        thumbnail = yessythumb(video_path, index)
        if thumbnail.suffix.lower() == ".svg":
            return Response(thumbnail.read_text(encoding="utf-8"), mimetype="image/svg+xml")
        return send_file(thumbnail, mimetype="image/jpeg")
    abort(404)
@app.route("/video/<int:index>")
def stream_video(index):
    if 0 <= index < len(video_paths):
        video_path = video_paths[index]
        if video_path.exists():
            return send_file(video_path, as_attachment=False)
    abort(404)
if __name__ == "__main__":
    iiii()
    app.run(host="127.0.0.1", port=1234, debug=False, use_reloader=False)