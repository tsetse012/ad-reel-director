---
name: ad-reel-director
description: Direct a 30-second live-action-style app commercial with AI in one render — concept stills → moveboard → identity sheets → keyframes → one Seedance 2.5 pass with voice and SFX → end card. Use when someone wants an ad, promo, reel, or short spot for an app or product that looks like a handheld film, not a screenshot slideshow. Triggers — "make an ad video", "promo reel", "30 second spot", "광고 영상 만들어줘", "릴스 광고", "앱 홍보 영상".
---

# ad-reel-director

You are directing a 30-second commercial that must look like it was shot handheld by a small crew,
not assembled from app screenshots. The whole method is: **lock identity in stills, lock the story in a
one-page moveboard, then let the video model render the 30 seconds in ONE pass** with its own voice and
sound effects. Music and the logo card are added in post.

Read `templates/` before writing any prompt. Every template line exists because a render failed without it.

## The seven steps (and where the human approves)

| # | step | tool | output | human gate |
|---|---|---|---|---|
| 1 | **Concepts** — 6 stills varying background × lead | `scripts/gen_stills.py` + `templates/concept_style.txt` | contact sheet | **pick one** |
| 2 | **Moveboard** — one page: 3 takes / 2 cuts, 3 lines, sounds, end card | `templates/moveboard.md` | `moveboard.md` | approve |
| 3 | **Sheets** — character / pet / location multi-panel references from the chosen still | `gen_stills.py` (refs) + `templates/sheet_rules.md` → `crop_panels.py` | sheets + single panels | optional |
| 4 | **Keyframes** — one still per shot beat, built from the panels | `gen_stills.py` (refs) + `templates/keyframe_ident.txt` | 5 keyframes | **final approval before paying for a render** |
| 5 | **Render** — Seedance 2.5, 30 s, audio on, one pass | `scripts/render_seedance.py` (`--mode i2v` or `r2v`) + `templates/prompt_30s.txt` | `spot_30s.mp4` | — |
| 6 | **QA** — frame strip + per-second motion | `scripts/qa_frames.py` | strip, `motion.txt` | judge; retake or accept |
| 7 | **Post** — dissolve to end card, (optional) BGM under the dialogue | `scripts/assemble_endcard.sh`, `scripts/mix_bgm.sh` | `spot_33s.mp4` | publish |

Do not skip step 1 for a moveboard: people choose tone from pictures, not from text.
Do not render before step 4 is approved: a render costs money and 7–15 minutes; a keyframe costs cents.

## Two render routes — both work, pick by what must be exact

- **i2v (two anchors)** `--mode i2v --start kf1 --end kf5`: first and last frame are pixel-locked; the three
  middle beats are prompt-only. Choose when the ending frame matters (logo space, brightness) — it will be exact.
  Side effects seen: small UI text creeps onto phone screens; the last second can stall.
- **r2v (start + sheets)** `--mode r2v --refs refs.json` with `[kf1, face panel, expression panel, pose panel,
  room wide, room reverse, room low]`: identity and room come from sheets, mid beats are prompt-only. Choose when
  the phone screen must stay clean or when the lead's face is the product. Ending is approximate.
- **Never** put five scene keyframes into r2v as references. Each keyframe is an independent still whose
  background differs slightly; at every cut the model reconciles them and the background smears. That is the
  defect that produced this rule. Sheets, not scenes.

Both routes are exclusive per API call (there is no "pixel-locked start frame + reference sheets" in one call).

## Prompt rules that are not optional

1. **Integer-second timestamps, 3 takes / 2 cuts (12 s, 18 s).** 30 s holds 4–6 shots at most; every hard cut re-synthesises the background, so use two.
2. **LIVING MOTION RULE paragraph** near the top: no frozen frames, no digital zoom on a still; subjects keep moving during every camera move. Without it the model freezes the picture and Ken-Burns it at 15 s and 27 s.
3. **Dialogue in quotes + "Only the lines inside quotes are spoken."** One line per take, mid-take, only where the face is large. Never say the app name in dialogue; the end card does that.
4. **State expressions positively.** "Relaxed soft smile, eyes open and bright" — never "concentrating, tongue out, eyes narrowed" (it rendered a grimace for 6 seconds).
5. **"No background music, no BGM, no singing"** — with audio on, the model sometimes lays its own music, which can trip the provider's copyright filter and fail the render.
6. **Phone screen**: name exactly what is on it and end with "no other words, buttons or labels". Expect a tiny camera-app UI anyway; if zero text matters, comp the real screen for those 3 s in post.
7. Reference images in r2v are cited as `@Image1…@ImageN` in **submission order**; say what each one is for.

## Sheet rules (see `templates/sheet_rules.md`)

Portrait panel 25–30% of the sheet, three-quarter angle, iris readable, catchlight in both eyes. Background is
the opposite luminance of the costume (`#3a3a3c` for bright clothes / white fur, `#d2d2d2` for dark). One face
per sheet. Cut sheets into single panels before giving them to the video model; each panel ≥ 300 px per side.

## QA — what to look at

- `frames_strip.jpg`: cut positions, identity across cuts, the phone screen, the end frame.
- `motion.txt`: any second under ~3 is a freeze. A 1–2 s low at a deliberate hold is fine; 3+ s is a retake.
- You cannot hear the render from a strip. Tell the human which three lines to listen for and that there must be no music.

## Costs and timings (Atlas Cloud, Sept 2026; verify with a live price call)

Stills at quality=high ≈ $0.17 each (6 concepts + 3 sheets + 4 keyframes ≈ $2–3). One 30 s / 720p / audio-on
render ≈ $4 and 7–15 minutes. A full spot with one retake ≈ $10–15. Reference images must be ≥ 300 px per side;
the video key must be allowed to call video models (an Atlas "coding plan" key returns 403).

## Reporting back

Show the contact sheet, then the moveboard, then the keyframe strip, then the render strip + motion numbers.
Say what you could not verify (audio). Keep the moveboard's decision log append-only: what was tried, what
failed, why the prompt changed.
