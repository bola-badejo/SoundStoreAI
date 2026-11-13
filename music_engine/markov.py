"""
markov.py — a tiny Markov chain melody generator.

Markov chain? Fancy name, simple idea:
    "Given the LAST note I played, what's a likely NEXT note?"
    "And after that, what's likely to come after THAT?"
    ... and so on.

We don't train on real songs (that would need data + more RAM).
Instead we build a transition table by hand that sounds "musical":
    - The next note is usually CLOSE to the previous one (small step).
    - Big leaps are rare.
    - Returning to the scale's root is always allowed (gives melody a "home").

That's enough to generate pleasant melodies for free, forever, on a potato.
"""

import random


def generate_melody(scale_notes: list[int],
                    length: int,
                    seed: int | None = None,
                    rest_chance: float = 0.1) -> list[tuple[int | None, float]]:
    """
    Produce a melody as a list of (midi_note_or_None, duration_in_beats).

    scale_notes: the MIDI numbers we're allowed to pick from (our scale).
    length: how many notes to produce.
    seed: pass a number to get the SAME melody again (reproducible).
    rest_chance: probability of a silent beat (makes rhythm feel natural).
    """

    # random.Random lets us have an isolated RNG — handy when the UI runs
    # several generations in a row without polluting Python's global RNG.
    rng = random.Random(seed)

    melody = []

    # Start on the root (first scale note). Classic "begin at home".
    current_index = 0

    for _ in range(length):
        # Should this slot be a rest instead of a note?
        if rng.random() < rest_chance:
            melody.append((None, _random_duration(rng)))
            continue

        # ---- Pick the NEXT scale index by weighted random walk ----
        # Options: stay, step up, step up 2, step down, step down 2,
        # jump to root (home), jump up an octave (surprise).
        choices = [
            (current_index,                       3),  # Repeat note.
            (current_index + 1,                   5),  # Step up (common).
            (current_index - 1,                   5),  # Step down (common).
            (current_index + 2,                   2),  # Skip a note up.
            (current_index - 2,                   2),  # Skip a note down.
            (0,                                   2),  # Home base.
            (current_index + len(scale_notes),    1),  # Octave jump (rare).
        ]

        # Build a weighted pool, then pick.
        pool = []
        for value, weight in choices:
            pool.extend([value] * weight)
        next_index = rng.choice(pool)

        # Keep the index within the available notes (wrap around via modulo).
        next_index = next_index % len(scale_notes)

        melody.append((scale_notes[next_index], _random_duration(rng)))
        current_index = next_index

    return melody


def _random_duration(rng: random.Random) -> float:
    """
    Pick a note length in BEATS. 1.0 = one beat (a quarter note).
    Shorter notes are more common than long ones → feels livelier.
    """
    return rng.choices(
        [0.25, 0.5, 0.5, 1.0, 1.0, 2.0],   # eighth, two 1/8ths... mostly 1/2 and 1-beat.
        k=1
    )[0]
