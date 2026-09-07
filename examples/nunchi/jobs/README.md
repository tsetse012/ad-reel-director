# Job files — the exact inputs behind the Nunchi spot

Run from the repo root in this order (paths inside the files are relative to the repo root):

```bash
python scripts/gen_stills.py examples/nunchi/jobs/concepts.json                 # 6 concepts → out/concepts/
#   pick one; crop a face/torso region of it to out/sheets/ref_lead_crop.png (any image tool)
python scripts/gen_stills.py examples/nunchi/jobs/sheets.json                   # woman_sheet.png, room_sheet.png → out/sheets/
python scripts/crop_panels.py out/sheets/woman_sheet.png out/sheets/panels examples/nunchi/jobs/panels_lead.json
python scripts/crop_panels.py out/sheets/room_sheet.png  out/sheets/panels examples/nunchi/jobs/panels_room.json
#   keyframes.json also expects out/sheets/panels/app_score_ring.png — a crop of the real app's result screen,
#   used as the style reference for the phone screen in kf3 (use your own product screenshot)
cp out/concepts/01_bed_night_woman.png out/keyframes/kf1_read.png
python scripts/gen_stills.py examples/nunchi/jobs/keyframes.json                # kf2..kf5 → out/keyframes/
```

Panel boxes are fractions of the sheet; the grid layout gpt-image-2 produces varies a little per run,
so open the sheet once and adjust the numbers before cropping.
