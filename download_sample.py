"""
Download a short traffic video for testing.
Uses yt-dlp to grab a public traffic footage clip from YouTube.

Install yt-dlp if needed:
    pip install yt-dlp

Then run:
    python download_sample.py
"""

import subprocess
import sys
from pathlib import Path

OUT_VIDEO = Path("sample_traffic.mp4")

# 1-minute intersection traffic clip, public domain / CC
# https://www.youtube.com/watch?v=MNn9qKG2UFI  "Traffic Intersection"
YOUTUBE_URL = "https://www.youtube.com/watch?v=MNn9qKG2UFI"


def check_ytdlp():
    try:
        subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def download():
    if OUT_VIDEO.exists():
        print(f"[INFO] {OUT_VIDEO} already exists, skipping download.")
        return

    if not check_ytdlp():
        print("[ERROR] yt-dlp not found. Install it with:  pip install yt-dlp")
        sys.exit(1)

    print(f"[INFO] Downloading traffic video → {OUT_VIDEO} ...")
    cmd = [
        "yt-dlp",
        "--format", "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best",
        "--merge-output-format", "mp4",
        "--output", str(OUT_VIDEO),
        # Download only first 60 seconds to keep it small
        "--download-sections", "*0:00-1:00",
        "--force-keyframes-at-cuts",
        YOUTUBE_URL,
    ]
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit("[ERROR] Download failed.")
    print(f"[INFO] Saved to {OUT_VIDEO}")


if __name__ == "__main__":
    download()

    import cv2
    cap = cv2.VideoCapture(str(OUT_VIDEO))
    w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    print(f"[INFO] Video: {w}x{h}  {fps:.1f} fps")
    print(f"\nRun tracker:\n"
          f"  python main.py --source {OUT_VIDEO} --line 0,{h//2},{w},{h//2}\n")
