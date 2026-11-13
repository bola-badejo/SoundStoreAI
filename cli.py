"""
cli.py — command-line way to generate a song.

Why a CLI when we already have a Streamlit app?
  1. Dead simple to test the engine without any UI.
  2. Great for teaching — you see every knob as a flag.
  3. Works even if Streamlit's install chain gives trouble.

Usage:
    python cli.py                                # defaults
    python cli.py --scale=blues --bars=8 --seed=42
    python cli.py --help                         # full list of options
"""

import argparse
from pathlib import Path
import time

from music_engine.generator import generate_song
from music_engine.renderer import render_midi_to_wav

PROJECT = Path(__file__).parent
OUTPUT_DIR = PROJECT / "output"
SOUNDFONT = PROJECT / "assets" / "FluidR3_GM.sf2"


def main() -> None:
    # argparse builds a --help page for free — great teaching tool.
    p = argparse.ArgumentParser(description="SoundStoreAI — tiny local music generator.")
    p.add_argument("--root",        default="C",     help="Key: C D E F G A B")
    p.add_argument("--scale",       default="major",
                   choices=["major", "minor", "blues",
                            "pentatonic_major", "pentatonic_minor", "dorian"])
    p.add_argument("--progression", default="pop",
                   choices=["pop", "blues", "sad", "jazz"])
    p.add_argument("--drums",       default="rock",
                   choices=["rock", "hip_hop", "ballad", "none"])
    p.add_argument("--tempo",       type=int, default=110, help="BPM 60-180")
    p.add_argument("--bars",        type=int, default=8,   help="1 bar = 4 beats")
    p.add_argument("--seed",        type=int, default=None, help="Same seed = same song")
    p.add_argument("--instrument",  type=int, default=0,
                   help="GM program number: 0=Piano, 24=Guitar, 56=Trumpet, 73=Flute, 80=Synth")
    p.add_argument("--no-wav",      action="store_true",
                   help="Only write MIDI (skip the WAV render, useful if fluidsynth is missing)")
    args = p.parse_args()

    OUTPUT_DIR.mkdir(exist_ok=True)
    stamp = int(time.time())
    midi_file = OUTPUT_DIR / f"song_{stamp}.mid"
    wav_file  = OUTPUT_DIR / f"song_{stamp}.wav"

    print(f"▶ Composing… (scale={args.scale}, bars={args.bars}, seed={args.seed})")
    generate_song(
        out_path=midi_file,
        root=args.root, scale=args.scale, progression=args.progression,
        drum_style=args.drums, tempo=args.tempo, bars=args.bars,
        seed=args.seed, melody_instrument=args.instrument,
    )
    print(f"   ✓ MIDI written: {midi_file}")

    if args.no_wav:
        print("   (skipped WAV render — pass without --no-wav to produce audio)")
        return

    if not SOUNDFONT.exists():
        print(f"   ⚠ SoundFont missing at {SOUNDFONT}. Run ./setup.sh to download it.")
        return

    print("▶ Rendering audio via FluidSynth…")
    render_midi_to_wav(midi_file, SOUNDFONT, wav_file)
    print(f"   ✓ WAV written: {wav_file}")


if __name__ == "__main__":
    main()
