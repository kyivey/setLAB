#!/bin/bash
# One-time setup for SetLAB on macOS.
#   ./setup.sh          install everything
#   ./setup.sh --build  install everything and build SetLAB.app
set -e
cd "$(dirname "$0")"

if [[ "$(uname)" != "Darwin" ]]; then
  echo "This setup script is for macOS." >&2
  exit 1
fi

# 1. Homebrew
if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required. Install it from https://brew.sh and re-run ./setup.sh" >&2
  exit 1
fi

echo "==> Installing system dependencies (python, ffmpeg, deno)..."
echo "    (Homebrew can sit quietly for a few minutes here; that's normal)"
# --no-upgrade: don't upgrade tools that are already installed (much faster)
brew bundle --file=Brewfile --no-upgrade

# 2. Python virtual environment
PYTHON="$(brew --prefix python@3.13)/bin/python3.13"
if [[ ! -x .venv/bin/python ]]; then
  echo "==> Creating Python virtual environment..."
  rm -rf .venv
  "$PYTHON" -m venv .venv
fi

echo "==> Installing Python packages..."
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt --progress-bar on

# 3. Make sure the bundled yt-dlp is current (YouTube breaks old versions)
chmod +x getSong.sh yt-dlp
echo "==> Updating yt-dlp..."
.venv/bin/python yt-dlp -U || echo "   (could not update yt-dlp; continuing with the bundled version)"

# 4. Optionally build the .app
if [[ "$1" == "--build" ]]; then
  echo "==> Building SetLAB.app..."
  .venv/bin/pyinstaller SetLAB.spec --noconfirm
  echo
  echo "============================================================"
  echo " Done! SetLAB.app is built."
  echo
  echo " To install it:"
  echo "   1. A Finder window with SetLAB.app is opening now"
  echo "      (or run:  open dist)"
  echo "   2. Drag SetLAB.app into your Applications folder"
  echo "      (it's in the Finder sidebar)"
  echo "   3. Open SetLAB from Applications or Launchpad"
  echo
  echo " The first time, if macOS says it can't be opened:"
  echo "   right-click SetLAB, choose Open, then Open again."
  echo "============================================================"
  open -R dist/SetLAB.app || true
else
  echo "Done! Start SetLAB with:  .venv/bin/python SetLAB.py"
  echo "Or build the app with:    ./setup.sh --build"
fi
