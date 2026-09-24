#!/bin/bash

DIR="$(dirname "$0")"

# Apps launched from Finder get a minimal PATH, so add the usual Homebrew
# locations where ffmpeg / deno / node live.
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# The packaged app (PyInstaller + Qt) passes its own library/Python settings
# down to child processes, which can confuse python3, deno and ffmpeg.
unset PYTHONHOME PYTHONPATH DYLD_LIBRARY_PATH DYLD_FALLBACK_LIBRARY_PATH \
      QT_PLUGIN_PATH QML2_IMPORT_PATH

# The GUI leaves stdin open as a pipe; make sure nothing waits on it.
exec </dev/null

# Full debug log of every run (paste this when something goes wrong).
LOG="$HOME/Library/Logs/SetLAB.log"
mkdir -p "$(dirname "$LOG")"
{
  echo "===== $(date) ====="
  echo "URL=$1  OUT=${2:-.}"
  echo "python3=$(command -v python3) ($(python3 --version 2>&1))"
  echo "ffmpeg=$(command -v ffmpeg)  deno=$(command -v deno)  node=$(command -v node)"
  env | sort
} >> "$LOG" 2>&1

# Check if a URL is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <YouTube or SoundCloud URL> [output folder]"
  exit 1
fi

# URL of the song
URL=$1

# Output folder (optional, defaults to current directory)
OUTPUT_FOLDER=${2:-.}

# ffmpeg is required to convert to mp3
if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg not found. Install it with: brew install ffmpeg"
  exit 1
fi

# yt-dlp now needs a JavaScript runtime to download from YouTube.
# Deno is used by default; fall back to Node or Bun if that's what's installed.
JS_ARGS=()
if command -v deno >/dev/null 2>&1; then
  :  # deno is enabled by default
elif command -v node >/dev/null 2>&1; then
  JS_ARGS=(--js-runtimes node)
elif command -v bun >/dev/null 2>&1; then
  JS_ARGS=(--js-runtimes bun)
else
  echo "WARNING: No JavaScript runtime found; YouTube downloads will likely fail."
  echo "         Install one with: brew install deno"
fi

# Download the song using yt-dlp (best-quality mp3).
# --force-ipv4: YouTube requests can hang at "Downloading webpage" over IPv6.
# Run with python3 explicitly (rather than relying on the #! line), write the
# verbose log to $LOG, and still show normal progress in the app.
set -o pipefail
python3 "$DIR/yt-dlp" "${JS_ARGS[@]}" --force-ipv4 --newline -v \
  --extract-audio --audio-format mp3 --audio-quality 0 \
  -o "$OUTPUT_FOLDER/%(title)s.%(ext)s" "$URL" 2>&1 \
  | tee -a "$LOG" | grep --line-buffered -v '^\[debug\]'
