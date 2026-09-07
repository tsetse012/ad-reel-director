# Example 3 — Nunchi (눈치): the A/B that shaped the two recommended routes

**Watch (route B):** https://youtube.com/shorts/23wfNnE-F6E · App: https://apps.apple.com/app/id6762175275

Nunchi pastes a KakaoTalk chat and returns a 0–100 "does this person like me" score.
The spot: late night, a woman rereads a message, pastes it into the app, watches a purple-to-pink ring
fill up to 72, laughs with relief, finally types her reply. "거봐. 나만 신경 쓴 거 아니잖아."

On the previous two spots the reference-to-video route with **five scene keyframes** smeared the background at
every cut (each keyframe is its own still; the room differs slightly; the model reconciles them at the cut).
So here we rendered both alternatives from the same moveboard and keyframes:

| route | inputs | prompt | result |
|---|---|---|---|
| **A — i2v, two anchors** | first frame (kf1) + last frame (kf5), nothing else | `prompt_i2v.txt` | ending pixel-exact and bright; small UI text crept onto the phone; last second slightly frozen |
| **B — r2v, start + sheets** | kf1 as @Image1 + 3 character panels + 3 room panels, **no mid keyframes** | `prompt_r2v_sheets.txt` + `refs_r2v.json` | cleanest phone screen (ring + number only); ending darker; 5 s shows the back of her head |

Both kept the room consistent across the cuts. `ab_compare_i2v_vs_r2v.jpg` shows the same 17 timestamps side by side (top A, bottom B).
Each render: 30 s, 720p, audio on, ≈ $4, 7–11 min.

| file | what it is |
|---|---|
| `concepts_contact_sheet.jpg` | 6 variations (bed / cafe / bus / rooftop / convenience store / desk); #01 chosen |
| `moveboard.md` | shot plan — note the "what is different from a pet spot" table (emotional arc is the product) |
| `keyframes_strip.jpg` | 5 keyframes; kf3 got the real app screenshot as a style reference, hence the accurate ring |
| `caption.md` | Reels caption |
