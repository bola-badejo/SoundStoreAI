"""
generator.py — glue layer.

This is the ONE function most of the app cares about:
    generate_song(...) -> writes a .mid file and returns its path.

Everything else (theory, markov, drums, midi_writer) is machinery it uses.
Keeping the glue in its own file means the UI stays short and readable.
"""

from pathlib import Path

from . import theory, markov, drums
from .midi_writer import write_midi


def generate_song(out_path: str | Path,
                  root: str = "C",
                  scale: str = "major",
                  progression: str = "pop",
                  drum_style: str = "rock",
                  tempo: int = 110,
                  bars: int = 8,
                  seed: int | None = None,
                  melody_instrument: int = 0,
                  chord_instrument: int = 48) -> str:
    """
    Compose a short piece and save it to disk as a .mid file.
    Returns the path (as a string) so the caller can hand it to the renderer.
    """

    # Step 1 — build the scale we'll draw melody notes from.
    scale_notes = theory.build_scale(root, scale, octave=5)   # A bit high = bright.

    # Step 2 — generate a melody using our tiny Markov walker.
    # 4 notes per bar is a reasonable density. Multiply by bars → total notes.
    melody_length = bars * 4
    melody = markov.generate_melody(scale_notes, length=melody_length, seed=seed)

    # Step 3 — expand the Roman-numeral progression into actual chord notes.
    chords = theory.progression_to_chords(progression, root, scale, octave=3)

    # Step 4 — pick a drum pattern (can be empty = "none").
    drum_pattern = drums.DRUM_PATTERNS.get(drum_style, [])

    # Step 5 — write the multi-track MIDI file.
    out_path = str(out_path)
    write_midi(
        path=out_path,
        melody=melody,
        chords=chords,
        drum_pattern=drum_pattern,
        tempo_bpm=tempo,
        bars=bars,
        melody_instrument=melody_instrument,
        chord_instrument=chord_instrument,
    )
    return out_path
