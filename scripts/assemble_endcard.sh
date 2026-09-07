#!/usr/bin/env bash
# Append a 3-second end card with a 1-second cross-dissolve at 29s → 33s total, audio faded under the dissolve.
#   scripts/assemble_endcard.sh out/render/v1/spot_30s.mp4 endcard.png out/final/spot_33s.mp4 [bg_hex]
# The end card is fitted to the video height and padded left/right with bg_hex (default black) —
# so a 19.5:9 App Store screenshot sits cleanly inside a 9:16 frame.
set -euo pipefail
IN="$1"; CARD="$2"; OUT="$3"; BG="${4:-0x000000}"
mkdir -p "$(dirname "$OUT")"
ffmpeg -v error -y -i "$IN" -loop 1 -framerate 24 -t 4 -i "$CARD" -filter_complex \
"[0:v]trim=0:30,setpts=PTS-STARTPTS,fps=24,format=yuv420p[v0];\
[1:v]scale=-2:1280,pad=720:1280:(ow-iw)/2:0:color=${BG},fps=24,format=yuv420p,setsar=1[v1];\
[v0][v1]xfade=transition=fade:duration=1:offset=29[v];\
[0:a]atrim=0:30,asetpts=PTS-STARTPTS,afade=t=out:st=29:d=1,apad=whole_dur=33[a]" \
-map "[v]" -map "[a]" -c:v libx264 -crf 20 -preset medium -pix_fmt yuv420p -c:a aac -b:a 160k -t 33 -movflags +faststart "$OUT"
echo "wrote $OUT ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")s)"
