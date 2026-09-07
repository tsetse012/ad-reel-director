#!/usr/bin/env python3
"""Render the 30-second spot with Seedance 2.5 on Atlas Cloud — two interchangeable routes.

  i2v  (image-to-video)      first frame + last frame are pixel-locked, everything between is prompt-guided
  r2v  (reference-to-video)  first frame as @Image1 + character panels + location panels; NO mid keyframes

    python scripts/render_seedance.py --mode i2v --prompt prompt.txt --start kf1.png --end kf5.png --out out/render/v1
    python scripts/render_seedance.py --mode r2v --prompt prompt.txt --refs refs.json --out out/render/v2
    python scripts/render_seedance.py --resume-id <prediction id> --out out/render/v2   # re-poll after a timeout

refs.json = ["kf1.png", "panels/woman_portrait.png", "panels/woman_laugh.png", "panels/room_wide.png", ...]
(order matters: the prompt cites them as @Image1, @Image2, ... in submission order)

Why no mid keyframes in r2v: each keyframe is an independently generated still whose background differs
slightly; at every cut the model reconciles them and the background smears. One start frame + sheet
panels keeps a single definition of the room. Both routes rendered cleanly in our A/B.

The script keeps state.json (prediction id) so a dropped connection never loses a paid render,
saves prediction.json (raw API response), and refuses to double-submit.
"""
import argparse, base64, io, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path
from PIL import Image

API = "https://api.atlascloud.ai/api/v1"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
MIN_SIDE = 320  # Atlas rejects reference images with any side < 300 px


def key():
    k = os.environ.get("ATLASCLOUD_VIDEO_API_KEY")
    if not k:
        sys.exit("set ATLASCLOUD_VIDEO_API_KEY (a key allowed to call video models)")
    return k


def headers(json_body=True):
    h = {"Authorization": f"Bearer {key()}", "User-Agent": UA}
    if json_body:
        h["Content-Type"] = "application/json"
    return h


def to_b64(path, max_side=2048, q=92):
    im = Image.open(path).convert("RGB")
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side))
    if min(im.size) < MIN_SIDE:
        f = MIN_SIDE / min(im.size)
        im = im.resize((round(im.width * f), round(im.height * f)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=q)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), im.size, len(buf.getvalue())


def post(path, body):
    for i in range(3):
        try:
            req = urllib.request.Request(API + path, data=json.dumps(body).encode(), headers=headers(), method="POST")
            return json.load(urllib.request.urlopen(req, timeout=180))
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:800]
            if e.code in (502, 504) and i < 2:
                print(f"[retry] HTTP {e.code}", flush=True); time.sleep(45); continue
            sys.exit(f"[HTTP {e.code}] {detail}")


def get(path):
    req = urllib.request.Request(API + path, headers=headers(False))
    return json.load(urllib.request.urlopen(req, timeout=60))


def dig(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k):
            return d[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["i2v", "r2v"], default="i2v")
    ap.add_argument("--prompt", help="text file with the full 30s prompt")
    ap.add_argument("--start"); ap.add_argument("--end"); ap.add_argument("--refs", help="JSON list of image paths (r2v)")
    ap.add_argument("--out", required=True); ap.add_argument("--duration", type=int, default=30)
    ap.add_argument("--resolution", default="720p"); ap.add_argument("--ratio", default="9:16", help="r2v only; i2v is always adaptive")
    ap.add_argument("--no-audio", action="store_true"); ap.add_argument("--format", choices=["mp4", "mov"], default="mp4")
    ap.add_argument("--resume-id"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    state = out / "state.json"; st = json.load(open(state)) if state.exists() else {}
    pid = a.resume_id or st.get("prediction_id")

    if not pid:
        prompt = Path(a.prompt).read_text(encoding="utf-8")
        (out / "prompt.txt").write_text(prompt, encoding="utf-8")
        body = {"prompt": prompt, "duration": a.duration, "resolution": a.resolution, "generate_audio": not a.no_audio,
                "watermark": False, "return_last_frame": True, "output_format": a.format}
        meta = {"mode": a.mode}
        if a.mode == "i2v":
            body["model"] = "bytedance/seedance-2.5/image-to-video"; body["ratio"] = "adaptive"
            body["image"], s_size, s_n = to_b64(a.start); meta["start"] = {"file": a.start, "size": s_size, "jpeg_bytes": s_n}
            if a.end:
                body["last_image"], e_size, e_n = to_b64(a.end); meta["end"] = {"file": a.end, "size": e_size, "jpeg_bytes": e_n}
        else:
            body["model"] = "bytedance/seedance-2.5/reference-to-video"; body["ratio"] = a.ratio
            refs = json.loads(Path(a.refs).read_text()); body["reference_images"] = []; meta["refs"] = []
            for i, p in enumerate(refs, 1):
                b, size, n = to_b64(p); body["reference_images"].append(b)
                meta["refs"].append({"index": f"@Image{i}", "file": p, "size": size, "jpeg_bytes": n})
        meta["params"] = {k: v for k, v in body.items() if k not in ("prompt", "image", "last_image", "reference_images")}
        (out / "request_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
        print(json.dumps(meta, ensure_ascii=False), flush=True)
        if a.dry_run:
            print("dry-run: not submitted"); return
        r = post("/model/generateVideo", body); d = r.get("data", r)
        pid = dig(d, "id", "prediction_id", "predictionId") or dig(r, "id")
        if not pid:
            sys.exit("unexpected response: " + json.dumps(r, ensure_ascii=False)[:800])
        json.dump({"prediction_id": pid, "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%S")}, open(state, "w"), indent=1)
        print(f"[submit] prediction_id={pid}", flush=True)

    t0 = time.time(); errs = 0
    while time.time() - t0 < 40 * 60:
        try:
            pr = get(f"/model/prediction/{pid}"); errs = 0
        except Exception as e:
            errs += 1; print(f"[poll err {errs}] {str(e)[:120]}", flush=True)
            if errs >= 20:
                sys.exit(f"polling failed 20x — resume later with --resume-id {pid}")
            time.sleep(10); continue
        pd = pr.get("data", pr); status = pd.get("status")
        print(f"[wait {int(time.time() - t0)}s] {status}", flush=True)
        if status in ("completed", "succeeded"):
            (out / "prediction.json").write_text(json.dumps(pd, ensure_ascii=False, indent=1))
            o = dig(pd, "outputs", "output", "video_url", "url"); url = o[0] if isinstance(o, list) else o
            data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=600).read()
            (out / f"spot_{a.duration}s.{a.format}").write_bytes(data)
            print(f"saved {out / f'spot_{a.duration}s.{a.format}'} {len(data) // 1024}KB | total_tokens={pd.get('total_tokens')}")
            return
        if status in ("failed", "error", "canceled"):
            (out / "prediction.json").write_text(json.dumps(pd, ensure_ascii=False, indent=1))
            sys.exit("failed: " + json.dumps(pd, ensure_ascii=False)[:1000])
        time.sleep(15)
    sys.exit(f"timeout — resume with --resume-id {pid}")


if __name__ == "__main__":
    main()
