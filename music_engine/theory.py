"""
theory.py — the music-theory cheatsheet, in code.

We store every note as a MIDI number. MIDI is a standard where every note on
a piano is one integer:
    C4 (middle C) = 60
    C#4 = 61    D4 = 62   ...
    Every octave up adds 12.

Understand that one line and the rest of this file is easy.
"""

#  Note names ↔ pitch classes (the "note letter" without the octave).
#  A pitch class is 0..11 where C=0, C#=1, D=2 ... B=11.

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

#  Scales = recipes for which notes "sound right" together.
#  Each entry is the list of semitone steps FROM THE ROOT.
#  Example: major scale is Whole-Whole-Half-Whole-Whole-Whole-Half, which in
#  semitones is 0, 2, 4, 5, 7, 9, 11.  (That's C-D-E-F-G-A-B when root = C.)

SCALES = {
    # Happy / bright
    "major":           [0, 2, 4, 5, 7, 9, 11],
    # Sad / emotional
    "minor":           [0, 2, 3, 5, 7, 8, 10],
    # Bluesy / gritty
    "blues":           [0, 3, 5, 6, 7, 10],
    # Floaty / eastern
    "pentatonic_major":[0, 2, 4, 7, 9],
    # Melancholy / Japanese
    "pentatonic_minor":[0, 3, 5, 7, 10],
    # Jazzy / mysterious
    "dorian":          [0, 2, 3, 5, 7, 9, 10],
}

#  Chord progressions written using Roman numerals (I, ii, iii, IV, V, vi, vii°).
#  A number represents "which note of the scale to build the chord on" (1-based).
#  We'll keep it simple: each chord is (scale_degree, chord_type).

#  Chord recipes — each is a list of semitone offsets from the chord's ROOT note.
CHORD_TYPES = {
    "maj": [0, 4, 7],      # Root + major third + fifth  (happy chord)
    "min": [0, 3, 7],      # Root + minor third + fifth  (sad chord)
    "dim": [0, 3, 6],      # Diminished (tense)
    "7":   [0, 4, 7, 10],  # Dominant 7th (bluesy)
}

#  Famous progressions. Each entry = (scale_degree_1_based, chord_type).
PROGRESSIONS = {
    # Pop staple: C - G - Am - F  in C major.
    "pop":   [(1, "maj"), (5, "maj"), (6, "min"), (4, "maj")],
    # Blues 12-bar skeleton.
    "blues": [(1, "7"), (1, "7"), (1, "7"), (1, "7"),
              (4, "7"), (4, "7"), (1, "7"), (1, "7"),
              (5, "7"), (4, "7"), (1, "7"), (5, "7")],
    # Sad / cinematic: vi - IV - I - V  in major.
    "sad":   [(6, "min"), (4, "maj"), (1, "maj"), (5, "maj")],
    # 12-bar jazz-ish ii - V - I loop.
    "jazz":  [(2, "min"), (5, "7"), (1, "maj"), (1, "maj")],
}

#  Helper functions. These are the ONLY things the rest of the app needs.

def note_name_to_midi(name: str, octave: int = 4) -> int:
    """
    'C' + octave 4 -> 60 (middle C).
    We find the pitch class (0..11), then add 12 for each octave above -1.
    (MIDI note 0 is C at octave -1, which is why the +1 is there.)
    """
    pitch_class = NOTE_NAMES.index(name)
    return pitch_class + (octave + 1) * 12


def build_scale(root_name: str, scale_type: str, octave: int = 4) -> list[int]:
    """
    Return the MIDI note numbers of a scale.
    Example: build_scale('C', 'major', 4) -> [60, 62, 64, 65, 67, 69, 71]
    """
    root = note_name_to_midi(root_name, octave)      # Where the scale starts.
    steps = SCALES[scale_type]                        # Recipe for this scale.
    # Add every step to the root to get the actual notes.
    return [root + s for s in steps]


def build_chord(root_midi: int, chord_type: str) -> list[int]:
    """
    Build a chord given a root MIDI note.
    Example: build_chord(60, 'maj') -> [60, 64, 67]  (C major = C+E+G)
    """
    offsets = CHORD_TYPES[chord_type]
    return [root_midi + o for o in offsets]


def progression_to_chords(progression_name: str,
                          root_name: str,
                          scale_type: str,
                          octave: int = 3) -> list[list[int]]:
    """
    Turn a Roman-numeral progression into actual chord notes.
    Lower octave (3) because chords usually sit BELOW the melody.
    """
    scale_notes = build_scale(root_name, scale_type, octave)
    out = []
    for degree, chord_type in PROGRESSIONS[progression_name]:
        # Convert 1-based degree to 0-based index.
        # % len(scale_notes) handles progressions that go past the 7th note.
        root_midi = scale_notes[(degree - 1) % len(scale_notes)]
        out.append(build_chord(root_midi, chord_type))
    return out
