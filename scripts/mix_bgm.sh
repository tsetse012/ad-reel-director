#!/usr/bin/env bash
# Mix a BGM track under the spot's own dialogue/SFX with sidechain ducking, then normalize for YouTube.
#   scripts/mix_bgm.sh out/final/spot_33s.mp4 bgm.mp3 out/final/spot_33s_bgm.mp4
# Bring your own BGM (we used ElevenLabs Music, which carries a commercial license on paid plans).
# Ducking: BGM drops ~5:1 whenever the dialogue track is above -28 dBFS, recovers in 450 ms.
# loudnorm to -16 LUFS: YouTube only turns loud uploads down, never quiet ones up.
set -euo pipefail
IN="$1"; BGM="$2"; OUT="$3"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
ffmpeg -v error -y -i "$IN" -i "$BGM" -filter_complex \
"[1:a]atrim=0:${DUR},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.5,afade=t=out:st=$(python3 -c "print(max(0,float('$DUR')-1.7))"):d=1.7,volume=0.32[bgm];\
[0:a]aformat=sample_rates=44100:channel_layouts=stereo,asplit=2[dlg][sc];\
[bgm][sc]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=450:makeup=1[duck];\
[dlg][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95,loudnorm=I=-16:TP=-1.5:LRA=11[a]" \
-map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "wrote $OUT"
