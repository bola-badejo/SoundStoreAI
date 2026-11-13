"""
drums.py — canned drum patterns, each labelled by vibe.

GM (General MIDI) drum map on channel 9 — the usual suspects:
    35 = Acoustic Bass Drum (kick)
    38 = Acoustic Snare
    42 = Closed Hi-hat
    46 = Open Hi-hat
    49 = Crash Cymbal
    51 = Ride Cymbal

A "pattern" here = list of (drum_note, beat_in_bar).
beat_in_bar = 0.0, 0.5, 1.0, 1.5, ... (0 is downbeat, 2.0 is beat 3, etc.)
"""

KICK, SNARE, HAT, OPEN_HAT = 35, 38, 42, 46

DRUM_PATTERNS = {
    # Classic 4-on-the-floor + snare backbeat.
    "rock": [
        (KICK, 0.0), (HAT, 0.0),
        (HAT, 0.5),
        (SNARE, 1.0), (HAT, 1.0),
        (HAT, 1.5),
        (KICK, 2.0), (HAT, 2.0),
        (HAT, 2.5),
        (SNARE, 3.0), (HAT, 3.0),
        (HAT, 3.5),
    ],

    # Hip-hop groove: kicks on 1 + off-beat, snare on 2 & 4.
    "hip_hop": [
        (KICK, 0.0), (HAT, 0.0),
        (HAT, 0.5),
        (SNARE, 1.0), (HAT, 1.0),
        (KICK, 1.5), (HAT, 1.5),
        (KICK, 2.0), (HAT, 2.0),
        (HAT, 2.5),
        (SNARE, 3.0), (HAT, 3.0),
        (HAT, 3.5),
    ],

    # Half-time ballad feel: snare only on 3.
    "ballad": [
        (KICK, 0.0),
        (HAT, 0.5),
        (HAT, 1.0),
        (HAT, 1.5),
        (SNARE, 2.0),
        (HAT, 2.5),
        (HAT, 3.0),
        (HAT, 3.5),
    ],

    # No drums.
    "none": [],
}
