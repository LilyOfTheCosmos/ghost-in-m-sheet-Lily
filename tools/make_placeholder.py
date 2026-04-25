#!/usr/bin/env python3
"""
Dev helper: generate a placeholder image or video with a label drawn on it.

Usage:
    python3 make_placeholder.py TEXT PATH WIDTH HEIGHT
    python3 make_placeholder.py --rebuild-manifest

PATH is resolved relative to ./asset-placeholders (when not absolute) so the
defaults line up with how build.sh swaps in real assets. The file extension
decides the output format:
    .png / .jpg / .jpeg  -> still image (ffmpeg color source + drawtext)
    .mp4                 -> 3-second looping video (H.264 + AAC)
    .webm                -> 3-second looping video (VP8 + Opus, with audio track)

Examples:
    python3 make_placeholder.py "Alice 1" characters/alice/1.png 640 360
    python3 make_placeholder.py "Trans Alex 3" characters/trans/alex/3.jpg 640 360
    python3 make_placeholder.py "Blake intro" characters/blake/home/1.mp4 640 360

Each successful generation also adds/updates an entry in
asset-placeholders/index.json. Run with --rebuild-manifest to regenerate the
manifest from scratch by scanning every placeholder under asset-placeholders/
(uses ffprobe for dimensions; labels stay empty unless you regenerate via the
normal mode).

Requires ffmpeg on PATH.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE = REPO_ROOT / "asset-placeholders"
MANIFEST_PATH = DEFAULT_BASE / "index.json"
IMAGE_EXTS = {".png", ".jpg", ".jpeg"}
VIDEO_EXTS = {".mp4", ".webm"}
VIDEO_DURATION = "3"
BG_COLOR = "gray"
FG_COLOR = "white"


def find_font() -> str:
    try:
        out = subprocess.check_output(
            ["fc-match", "sans", "--format=%{file}"], text=True
        ).strip()
        if out and Path(out).is_file():
            return out
    except (OSError, subprocess.CalledProcessError):
        pass
    for candidate in (
        "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ):
        if Path(candidate).is_file():
            return candidate
    sys.exit("error: no sans font found; install a TTF or pass --font")


def escape_drawtext(text: str) -> str:
    # drawtext is finicky: escape \ : ' % first, then wrap in single quotes.
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("%", "\\%")
    )


def build_drawtext_filter(text: str, width: int, font: str) -> str:
    font_size = max(16, width // 14)
    escaped = escape_drawtext(text)
    return (
        f"drawtext=fontfile='{font}'"
        f":text='{escaped}'"
        f":fontcolor={FG_COLOR}"
        f":fontsize={font_size}"
        f":x=(w-text_w)/2"
        f":y=(h-text_h)/2"
        f":box=1:boxcolor=black@0.5:boxborderw=10"
    )


def run_ffmpeg(cmd: list[str]) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        sys.exit(f"ffmpeg failed (exit {result.returncode})")


def generate(text: str, out_path: Path, width: int, height: int) -> None:
    ext = out_path.suffix.lower()
    if ext not in IMAGE_EXTS and ext not in VIDEO_EXTS:
        sys.exit(f"error: unsupported extension {ext!r} (use .png/.jpg/.mp4/.webm)")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    font = find_font()
    vf = build_drawtext_filter(text, width, font)

    base = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel", "error",
        "-f", "lavfi",
    ]
    if ext in IMAGE_EXTS:
        cmd = base + [
            "-i", f"color=c={BG_COLOR}:s={width}x{height}:d=0.1",
            "-vf", vf,
            "-frames:v", "1",
            str(out_path),
        ]
    elif ext == ".webm":
        cmd = base + [
            "-i", f"color=c={BG_COLOR}:s={width}x{height}:r=24:d={VIDEO_DURATION}",
            "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
            "-vf", vf,
            "-c:v", "libvpx",
            "-b:v", "200k",
            "-pix_fmt", "yuv420p",
            "-c:a", "libopus",
            "-t", VIDEO_DURATION,
            "-shortest",
            str(out_path),
        ]
    else:
        cmd = base + [
            "-i", f"color=c={BG_COLOR}:s={width}x{height}:r=24:d={VIDEO_DURATION}",
            "-vf", vf,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-t", VIDEO_DURATION,
            str(out_path),
        ]
    run_ffmpeg(cmd)
    print(f"wrote {out_path}")


def resolve_out(name: str) -> Path:
    p = Path(name)
    if p.is_absolute():
        return p
    return DEFAULT_BASE / p


def kind_for(ext: str) -> str:
    return "image" if ext in IMAGE_EXTS else "video"


def load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        return {"entries": {}}
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"entries": {}}
    if "entries" not in data or not isinstance(data["entries"], dict):
        data["entries"] = {}
    return data


def save_manifest(data: dict) -> None:
    data["entries"] = dict(sorted(data["entries"].items()))
    MANIFEST_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def update_manifest_entry(out_path: Path, label: str, width: int, height: int) -> None:
    """Record this placeholder in asset-placeholders/index.json.
    Skips silently if `out_path` lives outside DEFAULT_BASE."""
    try:
        rel = out_path.resolve().relative_to(DEFAULT_BASE)
    except ValueError:
        return
    data = load_manifest()
    data["entries"][str(rel)] = {
        "label": label,
        "width": width,
        "height": height,
        "kind": kind_for(out_path.suffix.lower()),
    }
    save_manifest(data)


def probe_dimensions(path: Path) -> tuple[int, int] | None:
    """Read width/height of an image or video using ffprobe."""
    if not shutil.which("ffprobe"):
        return None
    try:
        out = subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height",
                "-of", "csv=p=0:s=x",
                str(path),
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    parts = out.split("x")
    if len(parts) != 2:
        return None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None


def rebuild_manifest() -> None:
    """Scan asset-placeholders/ from scratch. Dimensions come from ffprobe;
    label is left empty for files we didn't generate this run."""
    print(f"scanning {DEFAULT_BASE}/ ...")
    entries: dict[str, dict] = {}
    valid_exts = IMAGE_EXTS | VIDEO_EXTS
    for path in sorted(DEFAULT_BASE.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in valid_exts:
            continue
        rel = str(path.relative_to(DEFAULT_BASE))
        dims = probe_dimensions(path)
        entries[rel] = {
            "label": "",
            "width": dims[0] if dims else None,
            "height": dims[1] if dims else None,
            "kind": kind_for(path.suffix.lower()),
        }
    save_manifest({"entries": entries})
    print(f"wrote {MANIFEST_PATH} ({len(entries)} entries)")


def main(argv: list[str]) -> None:
    if len(argv) == 2 and argv[1] == "--rebuild-manifest":
        rebuild_manifest()
        return
    if len(argv) != 5:
        sys.exit(
            "usage: make_placeholder.py TEXT PATH WIDTH HEIGHT\n"
            "       make_placeholder.py --rebuild-manifest\n"
            "       (PATH is relative to ./asset-placeholders unless absolute)"
        )
    text, name, width_s, height_s = argv[1:]
    try:
        width = int(width_s)
        height = int(height_s)
    except ValueError:
        sys.exit("error: WIDTH and HEIGHT must be integers")
    if width <= 0 or height <= 0:
        sys.exit("error: WIDTH and HEIGHT must be positive")
    if not shutil.which("ffmpeg"):
        sys.exit("error: ffmpeg not found on PATH")
    out_path = resolve_out(name)
    generate(text, out_path, width, height)
    update_manifest_entry(out_path, text, width, height)


if __name__ == "__main__":
    main(sys.argv)
