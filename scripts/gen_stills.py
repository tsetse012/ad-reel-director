#!/usr/bin/env python3
"""Generate stills (concepts / sheets / keyframes) with OpenAI gpt-image-2 from a JSON job file.

    python scripts/gen_stills.py jobs/concepts.json          # all jobs in the file
    python scripts/gen_stills.py jobs/keyframes.json kf2 kf4  # only these job names

Job file format (see examples/*/jobs/):
{
  "out_dir": "out/concepts",            # where PNGs go (created)
  "size": "1152x2048",                  # 9:16 for social; every side must be a multiple of 16
  "quality": "high",                    # low / medium / high
  "prefix": "STYLE text shared by every job in this file ...",
  "jobs": {
    "01_alley_student": { "prompt": "variant-specific text ..." },
    "kf2_shoot":        { "prompt": "...", "refs": ["out/sheets/panels/woman_portrait.png", "..."] }
  }
}
Jobs with "refs" use the images/edits endpoint (identity lock via multiple reference images);
jobs without "refs" use images/generations. Every job writes <name>.png + <name>.prompt.txt,
and the file's run.json records success/failure per job (double bookkeeping: keep the raw prompt).
"""
import base64, json, sys, time, concurrent.futures as cf
from pathlib import Path
from openai import OpenAI


def run_job(client, cfg, name, job):
    out = Path(cfg["out_dir"]); out.mkdir(parents=True, exist_ok=True)
    prompt = (cfg.get("prefix", "") + "\n\n" + job["prompt"]).strip()
    size, quality = job.get("size", cfg.get("size", "1152x2048")), job.get("quality", cfg.get("quality", "high"))
    t0 = time.time()
    try:
        if job.get("refs"):
            files = [open(p, "rb") for p in job["refs"]]
            r = client.images.edit(model="gpt-image-2", image=files, prompt=prompt, size=size, quality=quality, n=1)
        else:
            r = client.images.generate(model="gpt-image-2", prompt=prompt, size=size, quality=quality, n=1)
    except Exception as e:  # record failures too
        return {"name": name, "ok": False, "error": repr(e), "sec": round(time.time() - t0, 1)}
    data = base64.b64decode(r.data[0].b64_json)
    (out / f"{name}.png").write_bytes(data)
    (out / f"{name}.prompt.txt").write_text(prompt, encoding="utf-8")
    return {"name": name, "ok": True, "bytes": len(data), "sec": round(time.time() - t0, 1)}


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    cfg = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    only = sys.argv[2:]
    names = [n for n in cfg["jobs"] if not only or n in only]
    client = OpenAI()
    with cf.ThreadPoolExecutor(max_workers=min(6, len(names))) as ex:
        results = list(ex.map(lambda n: run_job(client, cfg, n, cfg["jobs"][n]), names))
    Path(cfg["out_dir"], "run.json").write_text(json.dumps(results, ensure_ascii=False, indent=1))
    print(json.dumps(results, ensure_ascii=False, indent=1))
    if any(not r["ok"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
