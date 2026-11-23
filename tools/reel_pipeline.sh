#!/usr/bin/env bash
# Download an Instagram reel and produce transcript + frames in a scratch dir.
# Prints only short summaries: the transcript and frames stay on disk.
# Usage: tools/reel_pipeline.sh <reel_url> <name> [cookies.txt]
set -euo pipefail

URL="${1:?reel url}"
NAME="${2:?short name, e.g. fx_booy}"
COOKIES="${3:-}"
V="$HOME/.venvs/media/bin"
W="${REEL_SCRATCH:-/tmp/reels_scratch}/$NAME"
mkdir -p "$W"

FF="$("$V/python" -c 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())')"
ARGS=(--ffmpeg-location "$(dirname "$FF")" --no-playlist -o "$W/src.%(ext)s")
[ -n "$COOKIES" ] && ARGS+=(--cookies "$COOKIES")

# yt-dlp fails at its own merge step (no ffprobe on this machine) but keeps the
# separate streams; accept that failure only when both streams are on disk.
"$V/yt-dlp" -k "${ARGS[@]}" "$URL" > "$W/download.log" 2>&1 || true

VID="$(ls "$W"/src.fdash-*v.mp4 2>/dev/null | head -1 || true)"
AUD="$(ls "$W"/src.fdash-*a.m4a 2>/dev/null | head -1 || true)"
if [ -z "$VID" ] || [ -z "$AUD" ]; then
  if ! ls "$W"/src.* >/dev/null 2>&1; then
    echo "DOWNLOAD_FAILED: see $W/download.log (last line: $(tail -1 "$W/download.log"))"; exit 1
  fi
fi
if [ -n "$VID" ] && [ -n "$AUD" ]; then
  "$FF" -y -loglevel error -i "$VID" -i "$AUD" -c copy "$W/reel.mp4"
else
  cp "$(ls "$W"/src.* | grep -v '\.log$' | head -1)" "$W/reel.mp4"
fi

"$FF" -y -loglevel error -i "$W/reel.mp4" -vn -ac 1 -ar 16000 "$W/audio.wav"
mkdir -p "$W/frames"
"$FF" -y -loglevel error -i "$W/reel.mp4" -vf "fps=1/3,scale=960:-1" "$W/frames/f_%03d.png"

"$V/python" - "$W" <<'PY' 2>/dev/null
import sys
from faster_whisper import WhisperModel
w = sys.argv[1]
m = WhisperModel("base", device="cpu", compute_type="int8")
segs, info = m.transcribe(f"{w}/audio.wav", language="es", vad_filter=True)
with open(f"{w}/transcript.txt", "w", encoding="utf-8") as f:
    for s in segs:
        f.write(f"[{s.start:6.1f}-{s.end:6.1f}] {s.text.strip()}\n")
print(f"DURATION_S={info.duration:.1f}")
PY

echo "DIR=$W"
echo "FRAMES=$(ls "$W/frames" | wc -l | tr -d ' ')"
echo "TRANSCRIPT_LINES=$(wc -l < "$W/transcript.txt" | tr -d ' ')"
