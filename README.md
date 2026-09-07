# ad-reel-director

Direct a 30-second, live-action-looking app commercial with AI — in **one video render**, with the model's own
voice and sound effects. Stills lock the identity, a one-page moveboard locks the story, Seedance 2.5 renders
the 30 seconds in a single pass, ffmpeg adds the end card.

[한국어 README](README.ko.md) · `SKILL.md` is the manual for Claude Code (or any coding agent); humans only need this page.

## Before / after

| a screenshot slideshow (what we had) | this method |
|---|---|
| static app screens, crossfades, stock music | handheld 35 mm look, one continuous take per beat, spoken lines, diegetic sound |

Three spots made with this repo, each from concept to YouTube in an afternoon and about $10–15:

| spot | watch | route |
|---|---|---|
| Jupnyangi (줍냥이) — cat in a morning alley | https://youtube.com/shorts/XyNFGF2DogI | r2v |
| Jupnyangi — Maltese in a living room | https://youtube.com/shorts/4ufNKuxzklo | r2v |
| Nunchi (눈치) — late-night reply anxiety | https://youtube.com/shorts/23wfNnE-F6E | r2v, start + sheets (A/B vs i2v in `examples/nunchi`) |

Everything about those three — moveboards, the exact prompts, keyframes, QA strips, captions — is in [`examples/`](examples/). The cat spot also has a full cut-by-cut teardown of the finished render (lighting plots, staging, palette, the dialogue the analyser heard) in [`examples/jupnyangi-cat/cutaway/`](examples/jupnyangi-cat/cutaway/) — the plan and the render match to the second.

## The method in one picture

```
6 concept stills ──pick one──▶ moveboard (3 takes / 2 cuts, 3 lines) ──▶ identity sheets ──cut──▶ panels
                                                                              │
                                                     keyframes (one per beat) ◀┘
                                                              │  approve
                              ┌──── i2v: first + last frame ──┤
   Seedance 2.5, 30 s, audio ◀┤                               │
                              └──── r2v: first frame + sheet panels (NO scene keyframes)
                                                              │
                                    QA strip + motion numbers ─▶ dissolve to end card ─▶ (BGM) ─▶ publish
```

## Quick start

```bash
git clone https://github.com/tsetse012/ad-reel-director && cd ad-reel-director
pip install -r requirements.txt            # openai, pillow; ffmpeg must be on PATH
cp .env.example .env                       # OPENAI_API_KEY (stills), ATLASCLOUD_VIDEO_API_KEY (video)

# 1. six concept stills from a job file (see examples/*/ and templates/concept_style.txt)
python scripts/gen_stills.py jobs/concepts.json
# 2. write moveboard.md from templates/moveboard.md — pick the concept, three lines, two cuts
# 3. sheets from the chosen still, then cut them into panels
python scripts/gen_stills.py jobs/sheets.json
python scripts/crop_panels.py out/sheets/lead_sheet.png out/sheets/panels panels.json
# 4. keyframes from the panels
python scripts/gen_stills.py jobs/keyframes.json
# 5. render (pick a route)
python scripts/render_seedance.py --mode i2v --prompt prompt.txt --start out/kf/kf1.png --end out/kf/kf5.png --out out/render/v1
python scripts/render_seedance.py --mode r2v --prompt prompt.txt --refs refs.json --out out/render/v1
# 6. QA
python scripts/qa_frames.py out/render/v1/spot_30s.mp4
# 7. end card (+ optional BGM with ducking)
scripts/assemble_endcard.sh out/render/v1/spot_30s.mp4 endcard.png out/final/spot_33s.mp4 0x0a0614
scripts/mix_bgm.sh out/final/spot_33s.mp4 bgm.mp3 out/final/spot_33s_bgm.mp4
```

With Claude Code: drop this folder into `.claude/skills/ad-reel-director/` (or symlink it) and say
"make a 30-second ad for my app". The agent follows `SKILL.md`, stops at the two approval gates, and hands you
a contact sheet, a moveboard, a keyframe strip and a render strip in that order.

## What actually moved the quality

These are the things that changed the result, in the order we discovered them (details in `templates/`):

1. **One render, not a slideshow.** Seedance 2.5 keeps physics, light and identity across a 30 s single pass; stitching 5 s clips never matched this.
2. **Three takes, two cuts.** Every hard cut re-synthesises the background. Camera moves inside a take replace cuts.
3. **The "living motion" paragraph.** Without it the model freezes a frame and zooms it whenever the prompt says push-in or pull-back.
4. **Identity from sheets, cut into single panels.** A whole 9-panel sheet is read as a storyboard and loses detail; single views are read faithfully.
5. **Sheets, not scene keyframes, as r2v references.** Five scene stills = five slightly different rooms = smeared background at every cut. First frame + sheet panels keeps one room.
6. **Expressions written positively.** "Soft closed-lip smile" — never what to avoid.
7. **No BGM in the render.** Add it in post; the model's own music can trip the copyright filter.
8. **Per-second motion numbers** as the QA gate instead of watching every render three times.

## Costs (Atlas Cloud, Sept 2026 — re-check with a live price call)

| item | cost |
|---|---|
| still, gpt-image-2 quality=high, 1152×2048 | ≈ $0.17 |
| 6 concepts + 3 sheets + 4 keyframes | ≈ $2–3 |
| 30 s render, 720p, audio on | ≈ $4, 7–15 min |
| a finished spot with one retake | ≈ $10–15 |

## Limits we hit

- Phone screens grow a tiny camera-app UI no matter what the prompt says. Plan to comp the real screen for those 3 s if zero text matters.
- i2v pixel-locks the last frame, so the final second may stall; r2v's ending is approximate.
- Reference images must be ≥ 300 px per side (`crop_panels.py` upscales small panels).
- You cannot hear the render from a QA strip; listen for the three lines and for any music before publishing.
- Model availability and prices on gateways change week to week; the scripts take the model id as a plain string for that reason.

## People

All people and pets in the examples are generated; no real person was used as a reference. Do not upload real
faces as references — the provider's terms forbid it and so does common decency.

## License

MIT. Built by a solo developer to promote two of his own apps; issues are welcome, response time is not promised.
