#!/usr/bin/env python3
"""Cut a multi-panel reference sheet into single-panel PNGs.

Seedance 2.5 treats a whole multi-panel sheet as a loose "storyboard" and drops detail;
it reads single views much more faithfully. So we generate the 9-panel sheet for humans
(and for gpt-image-2 keyframes) and cut it into panels for the video model.

    python scripts/crop_panels.py out/sheets/woman_sheet.png out/sheets/panels panels.json

panels.json maps panel name -> [x0, y0, x1, y1] in *fractions* of the sheet (0..1), e.g.
{ "woman_portrait": [0, 0, 0.34, 0.5], "woman_crouch": [0, 0.52, 0.25, 1.0] }

Panels are upscaled so the short side is >= 320 px: Atlas rejects reference images under 300 px
(InvalidParameter.HeightTooSmall).
"""
import json, sys
from pathlib import Path
from PIL import Image

MIN_SIDE = 320


def main():
    src, out_dir, spec = Path(sys.argv[1]), Path(sys.argv[2]), json.loads(Path(sys.argv[3]).read_text())
    out_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    W, H = im.size
    for name, (x0, y0, x1, y1) in spec.items():
        panel = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
        if min(panel.size) < MIN_SIDE:
            f = MIN_SIDE / min(panel.size)
            panel = panel.resize((round(panel.width * f), round(panel.height * f)), Image.LANCZOS)
        panel.save(out_dir / f"{name}.png")
        print(name, panel.size)


if __name__ == "__main__":
    main()
