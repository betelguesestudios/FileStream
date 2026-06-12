from flask import Flask, abort, send_file
from pathlib import Path
from html import escape
app = Flask(__name__)
losvideos = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".mpg", ".mpeg"}
video_paths = []
def scan_videos(folder: Path):
    if not folder.exists() or not folder.is_dir():
        return []
    return sorted(
        [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in losvideos],
        key=lambda p: p.name.lower(),
    )
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
    items = []
    items.append("""<style>
.video-container {
  display: flex;
  justify-content: center;
  margin: 20px 0;
}
.video-container video {
  width: auto;
  max-width: 100%;
  display: block;
  border-radius: 16px;
}
</style>""")
    for index, video_path in enumerate(video_paths):
        ext = video_path.suffix.lower()
        if ext == ".mp4":
            mime_type = "video/mp4"
        elif ext == ".mkv":
            mime_type = "video/x-matroska"
        elif ext == ".mov":
            mime_type = "video/quicktime"
        elif ext == ".webm":
            mime_type = "video/webm"
        else:
            mime_type = "video/mp4"
        items.append(
            "<br></br>"
            f"""<div class="video-container"><video controls width='640' height='360'><source src='/video/{index}' type='{mime_type}'></video></div>"""
        )
    if not items:
        items.append("<p>no videos found lol</p>")
    return "<!doctype html><html><body>" + "".join(items) + "</body></html>"
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