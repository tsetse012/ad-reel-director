# Reference sheets — rules that survived three productions

A sheet is a 16:9 multi-panel grid of ONE subject (character / pet / location) on a plain cyclorama.
Generate it with the images/edits endpoint, passing the chosen concept still (and a face crop of it)
as `refs`, so the sheet inherits that exact identity. Then cut it into single panels (`crop_panels.py`).

## Prompt skeleton (character)

```
Reference handling: the attached photos are a PHOTOGRAPHIC IDENTITY reference of {{who}} — keep that exact
person's face, age, bone structure, hairstyle and costume ({{costume in plain words}}). Ignore the scene
lighting; render on a neutral cyclorama.

Character: {{2–3 sentences: nationality/age, face shape, eye colour, skin, mood. "Ordinary and believable, not a model."}}

PHOTOREALISTIC reference sheet arranged as a clean MULTI-PANEL grid, 16:9 horizontal, shot on a real camera
with film grain — NOT illustration, NOT 3D render, no beauty filter, no glossy AI skin. NO text, NO labels,
NO arrows, NO watermark, NO extra characters.
Panels for the SAME character: bust portrait (large, three-quarter, {{expression}}), front full-body standing,
three-quarter full-body, side profile, back, {{2–3 poses the spot actually needs, e.g. crouching with phone}},
{{2–3 expression close-ups the spot needs: worried / eyes-closed relief / open laugh}}, hand-with-phone close-up.
Keep face, hair, costume, palette IDENTICAL in every panel.
The bust portrait panel must occupy 25–30% of the whole sheet and be slightly OFF-FRONTAL. Eyes: iris colour
clearly readable, never crushed to black, with a visible catchlight in both eyes. Naturally asymmetric.
PLAIN seamless {{BG}} studio cyclorama, soft even studio light, no rim light, no colored light.
```

## Hard rules

| Rule | Why |
|---|---|
| Portrait panel = 25–30% of the sheet, three-quarter angle | It is the only place the video model reads the face; frontal-only loses head volume |
| Iris colour readable + catchlight in both eyes | Crushed eyes carry no light information → skin tone drifts shot to shot |
| **Background = the opposite luminance of the main costume** — bright clothes / white fur → `deep neutral gray (#3a3a3c)`, dark clothes → `light gray (#d2d2d2)` | Measured subject/background separation: 145 vs 1.6 for white-on-light. Separation, not the absolute colour, is what the model needs |
| One face per sheet | Two faces = two identities supplied; the model picks a different one per shot |
| No rim light, no coloured light on the sheet | Whatever is baked into the sheet leaks into every downstream shot |
| Cut the sheet into panels before giving it to the video model; each panel ≥ 300 px on both sides | Seedance reads a whole grid as a loose storyboard and drops detail; Atlas rejects images < 300 px |
| Never regenerate a whole sheet to fix one panel | Repeated regenerations accumulate a dirty plate and split the identity; fix one panel with a mask |

## Location sheet

Same grid idea, no people, no animals. Because the light IS the subject here, keep the real scene light
(sun direction, flare) instead of studio light. Panels: wide establishing (large), reverse angle, low angle,
two detail shots, a four-panel turnaround strip. Give the video model the wide + reverse + low panels.
