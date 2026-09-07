# Example 1 — Jupnyangi (줍냥이), cat edition

**Watch:** https://youtube.com/shorts/XyNFGF2DogI · App: https://apps.apple.com/app/id6784272434

Jupnyangi turns a photo of a stray cat or a dog into a storybook card in a personal collection.
The spot: a young woman on a morning walk meets a calico in a 2010s Korean alley, photographs it,
the photo becomes a card, the cat head-bumps her knee. "오늘도 한 마리 주웠다." (Picked up one more today.)

| file | what it is |
|---|---|
| `concepts_contact_sheet.jpg` | 6 concept variations (background × lead); #06 was chosen |
| `moveboard.md` | the approved shot plan (Korean), with the decision log of what v1 got wrong |
| `keyframes_strip.jpg` | 5 keyframes generated from the sheets |
| `prompt_r2v_keyframes.txt` | the exact 30 s prompt used (r2v route, 5 keyframes + 3 identity panels) |
| `render_frames_strip.jpg` | QA strip of the final render |
| `caption.md` | the Reels caption (Korean) |

Route used: **reference-to-video with all 5 keyframes**. It rendered clean here, but on the third production
this route smeared the background at every cut — see `../nunchi/` for the two routes we recommend instead.
Costs: 6 concepts + 3 sheets + 4 keyframes ≈ $3 in stills, 2 × 30 s renders ≈ $8.

**Post-render check:** the finished spot was torn down cut by cut with Cutaway — all four boards and the shot table are in [`cutaway/`](cutaway/). The machine cuts land exactly on the moveboard's 12 s / 18 s cuts.
