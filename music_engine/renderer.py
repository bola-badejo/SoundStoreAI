"""
renderer.py — turn a .mid file into a playable .wav using FluidSynth.

FluidSynth is a command-line program (not a Python library here). We call it
via subprocess — the same way you'd run it from Terminal yourself. That's
teaching-friendly: students can copy the command and run it by hand too.
"""

import shutil
import subprocess
from pathlib import Path


def render_midi_to_wav(midi_path: str | Path,
                       soundfont_path: str | Path,
                       wav_path: str | Path) -> str:
    """
    Run FluidSynth to render midi_path using soundfont_path, saving wav_path.
    Raises RuntimeError if anything goes wrong — we want loud failures.
    """

    # shutil.which finds 'fluidsynth' on $PATH (same as `which fluidsynth`).
    fluidsynth = shutil.which("fluidsynth")
    if not fluidsynth:
        raise RuntimeError(
            "fluidsynth command not found. Install it first:\n"
            "    brew install fluid-synth"
        )

    midi_path = Path(midi_path)
    wav_path = Path(wav_path)
    soundfont_path = Path(soundfont_path)

    if not midi_path.exists():
        raise RuntimeError(f"MIDI file missing: {midi_path}")
    if not soundfont_path.exists():
        raise RuntimeError(
            f"SoundFont missing: {soundfont_path}\n"
            f"Download one and place it there (see assets/README.md)."
        )

    # fluidsynth flags explained:
    #   -ni      : no interactive shell, no audio out, just render.
    #   -g 1.0   : gain (volume).
    #   -r 44100 : sample rate — CD quality.
    #   -F path  : output file (triggers file render mode).
    #   -F needs to come before the input .mid.
    cmd = [
        fluidsynth,
        "-ni",
        "-g", "1.0",
        "-r", "44100",
        "-F", str(wav_path),
        str(soundfont_path),
        str(midi_path),
    ]

    # Run it. capture_output so we can show errors nicely.
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            "FluidSynth render failed:\n"
            f"STDOUT: {result.stdout}\n"
            f"STDERR: {result.stderr}"
        )

    return str(wav_path)
