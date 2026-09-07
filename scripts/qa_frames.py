#!/usr/bin/env python3
"""QA a rendered spot without watching it frame by frame.

    python scripts/qa_frames.py out/render/v1/spot_30s.mp4

Writes next to the video:
  frames_strip.jpg   one frame per timestamp (1,3,5,...,29.8s) with labels — check cuts, identity, phone screen
  motion.txt         mean frame-to-frame luma difference per second — low numbers (< ~3) mean the model froze
                     the picture and only zoomed/panned it, the single most common defect in 30s single-pass renders

Needs ffmpeg/ffprobe on PATH.
"""
import subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TS = ["1", "3", "5", "7", "9", "11", "12.5", "14", "15.5", "17", "19", "21", "23", "25", "27", "28.5", "29.8"]


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def main():
    video = Path(sys.argv[1]); d = video.parent; frames = d / "frames"; frames.mkdir(exist_ok=True)
    for t in TS:
        sh(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", str(video), "-frames:v", "1", "-vf", "scale=200:-1", str(frames / f"f_{t}.jpg")])
    ims = [Image.open(frames / f"f_{t}.jpg") for t in TS if (frames / f"f_{t}.jpg").exists()]
    w, h = ims[0].size; pad, lh = 5, 20
    strip = Image.new("RGB", (len(ims) * (w + pad) + pad, h + lh + 2 * pad), "white"); dr = ImageDraw.Draw(strip)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except Exception:
        font = ImageFont.load_default()
    for i, (im, t) in enumerate(zip(ims, TS)):
        x = pad + i * (w + pad); strip.paste(im, (x, pad)); dr.text((x + 2, pad + h + 2), f"{t}s", fill="black", font=font)
    strip.save(d / "frames_strip.jpg", quality=88)

    # per-second motion: sample every 6th frame, blend consecutive frames by difference, average luma
    r = sh(["ffmpeg", "-v", "error", "-i", str(video), "-vf",
            "scale=180:-1,select='not(mod(n,6))',tblend=all_mode=difference,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-",
            "-f", "null", "-"])
    vals = [float(l.split("=")[1]) for l in r.stdout.splitlines() if "YAVG" in l]
    per_sec = [sum(vals[i:i + 4]) / max(1, len(vals[i:i + 4])) for i in range(0, len(vals), 4)]
    lines = [f"{s}: {v:.1f}" + ("   <-- near-frozen" if v < 3 else "") for s, v in enumerate(per_sec)]
    (d / "motion.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nstrip: {d / 'frames_strip.jpg'}")


if __name__ == "__main__":
    main()
