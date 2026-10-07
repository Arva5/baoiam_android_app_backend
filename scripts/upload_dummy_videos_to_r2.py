"""
Dummy sample MP4s download karke Cloudflare R2 pe upload karta hai.

Need:
  - wrangler login (Cloudflare account)
  - env: R2_BUCKET_NAME (default baoiam-course-videos)
  - optional: R2_PUBLIC_BASE_URL after enabling public access on the bucket

Usage (from baoiam_android_app_backend):
  python scripts/upload_dummy_videos_to_r2.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

BUCKET = os.environ.get("R2_BUCKET_NAME", "baoiam-course-videos")
SAMPLE = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample"

# R2 key -> source sample file
FILES = [
    ("videos/python/welcome.mp4", f"{SAMPLE}/BigBuckBunny.mp4"),
    ("videos/python/install.mp4", f"{SAMPLE}/ElephantsDream.mp4"),
    ("videos/python/variables.mp4", f"{SAMPLE}/Sintel.mp4"),
    ("videos/android/setup.mp4", f"{SAMPLE}/TearsOfSteel.mp4"),
    ("videos/android/compose.mp4", f"{SAMPLE}/ForBiggerBlazes.mp4"),
    ("videos/uiux/intro.mp4", f"{SAMPLE}/ForBiggerEscapes.mp4"),
    ("videos/uiux/colors.mp4", f"{SAMPLE}/ForBiggerJoyrides.mp4"),
    (
        "pdfs/python/cheatsheet.pdf",
        "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
    ),
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.check_call(cmd)


def main() -> int:
    try:
        run(["npx", "--yes", "wrangler", "--version"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("wrangler nahi mila. Pehle: npm install -g wrangler  then  wrangler login")
        return 1

    try:
        run(["npx", "--yes", "wrangler", "r2", "bucket", "create", BUCKET])
    except subprocess.CalledProcessError:
        print(f"Bucket create skip (already exists?): {BUCKET}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for key, src in FILES:
            dest = tmp_path / Path(key).name
            print(f"Downloading {src}")
            urllib.request.urlretrieve(src, dest)
            run(
                [
                    "npx",
                    "--yes",
                    "wrangler",
                    "r2",
                    "object",
                    "put",
                    f"{BUCKET}/{key}",
                    "--file",
                    str(dest),
                    "--remote",
                    "--content-type",
                    "application/pdf" if key.endswith(".pdf") else "video/mp4",
                ]
            )

    print(
        "\nDone. Cloudflare dashboard me is bucket pe Public Development URL enable karo,\n"
        "phir .env me set karo:\n"
        "  R2_BUCKET_NAME=" + BUCKET + "\n"
        "  R2_PUBLIC_BASE_URL=https://pub-xxxxxxxx.r2.dev\n"
        "Phir seed:\n"
        "  python manage.py seed_dummy_courses --reset --r2-base-url %R2_PUBLIC_BASE_URL%\n"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
