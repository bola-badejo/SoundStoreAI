#!/usr/bin/env bash
# ----------------------------------------------------------------------------
#  setup.sh — one-shot environment setup for SoundStoreAI.
#  Run from the project root:   ./setup.sh
# ----------------------------------------------------------------------------
set -e   # Stop on first error. (-e = "exit on error")

echo "▶ 1/4  Installing system packages via Homebrew..."
brew install fluid-synth ffmpeg || true   # 'true' so re-running doesn't fail.

echo "▶ 2/4  Creating Python virtual environment at .venv ..."
python3 -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "▶ 3/4  Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "▶ 4/4  Downloading free FluidR3_GM SoundFont (~140 MB)..."
mkdir -p assets
if [ ! -f assets/FluidR3_GM.sf2 ]; then
    # Hosted on the MuseScore mirror of the public-domain FluidR3 SoundFont.
    curl -L -o assets/FluidR3_GM.sf2 \
        "https://github.com/musescore/MuseScore/raw/2.1/share/sound/FluidR3Mono_GM.sf3"
    echo "   (Downloaded a compressed .sf3 variant — FluidSynth handles both.)"
else
    echo "   SoundFont already present — skipped."
fi

echo
echo "✅ Done!"
echo "   Activate the venv:   source .venv/bin/activate"
echo "   Then run the app:    streamlit run app.py"
