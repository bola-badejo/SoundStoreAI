"""
midi_writer.py — turn our generated notes into a real .mid file.

MIDI timing uses "ticks". A common standard:
    1 beat (quarter note) = 480 ticks.
That's what mido defaults to — we just stick with it.

A MIDI file has TRACKS. Each track is a series of MESSAGES like:
    note_on  (press key)
    note_off (release key)
    program_change (switch instrument)

Think of it like a recipe for a player-piano.
"""

import mido

TICKS_PER_BEAT = 480   # Standard MIDI resolution.


def write_midi(path: str,
               melody: list[tuple[int | None, float]],
               chords: list[list[int]],
               drum_pattern: list[tuple[int, float]] | None,
               tempo_bpm: int = 120,
               melody_instrument: int = 0,     # 0 = Acoustic Grand Piano (GM).
               chord_instrument: int = 48,     # 48 = String Ensemble 1.
               bars: int = 8,
               beats_per_bar: int = 4) -> None:
    """
    Save a multi-track MIDI file combining melody + chords + drums.
    Drums live on MIDI channel 9 by convention — the standard GM drum map.
    """

    mid = mido.MidiFile(ticks_per_beat=TICKS_PER_BEAT)

    # --- Tempo track (meta messages don't play — they CONFIGURE playback) ----
    meta = mido.MidiTrack()
    mid.tracks.append(meta)
    # mido has a helper that turns BPM into microseconds per beat (what MIDI stores).
    meta.append(mido.MetaMessage("set_tempo",
                                 tempo=mido.bpm2tempo(tempo_bpm)))
    meta.append(mido.MetaMessage("time_signature",
                                 numerator=beats_per_bar, denominator=4))

    # --- Melody track ----
    _add_melody_track(mid, melody, melody_instrument, channel=0)

    # --- Chord track ----
    total_beats = bars * beats_per_bar
    _add_chord_track(mid, chords, total_beats, chord_instrument, channel=1)

    # --- Drum track (channel 9 is drums in General MIDI) ----
    if drum_pattern:
        _add_drum_track(mid, drum_pattern, total_beats, channel=9)

    mid.save(path)

#  Internal helpers. Prefixing with _ = "don't use me from outside this file".

def _add_melody_track(mid, melody, program, channel):
    track = mido.MidiTrack()
    mid.tracks.append(track)
    # program_change picks the instrument.
    track.append(mido.Message("program_change", program=program, channel=channel, time=0))

    # "time" on each message is TICKS SINCE THE PREVIOUS MESSAGE in the track.
    # So a "rest" is just: next note_on has a bigger 'time'.
    carry = 0    # ticks to delay the next event by.
    velocity = 90   # how hard the note is struck (0-127).

    for note, beats in melody:
        duration = int(beats * TICKS_PER_BEAT)
        if note is None:
            # Rest: no messages emitted, we just defer the next event.
            carry += duration
        else:
            track.append(mido.Message("note_on",  note=note, velocity=velocity,
                                      channel=channel, time=carry))
            track.append(mido.Message("note_off", note=note, velocity=0,
                                      channel=channel, time=duration))
            carry = 0


def _add_chord_track(mid, chords, total_beats, program, channel):
    track = mido.MidiTrack()
    mid.tracks.append(track)
    track.append(mido.Message("program_change", program=program, channel=channel, time=0))

    # Spread the chord list evenly across the song.
    beats_per_chord = max(1, total_beats // max(1, len(chords)))
    duration_ticks = beats_per_chord * TICKS_PER_BEAT

    for chord in chords:
        # Press every chord note at the SAME TIME (hence time=0 on all but first).
        for i, note in enumerate(chord):
            track.append(mido.Message("note_on", note=note, velocity=70,
                                      channel=channel, time=0 if i > 0 else 0))
        # Release them all at the same time. First note_off carries the duration;
        # subsequent ones fire instantly (time=0).
        for i, note in enumerate(chord):
            track.append(mido.Message("note_off", note=note, velocity=0,
                                      channel=channel,
                                      time=duration_ticks if i == 0 else 0))


def _add_drum_track(mid, drum_pattern, total_beats, channel):
    """
    drum_pattern is a list of (drum_midi_note, beat_position) within one bar.
    We loop the pattern for the full song length.

    Trick: several drums can fire on the SAME beat (kick + hi-hat together).
    So we first build a list of absolute-tick events, SORT it, and only then
    compute deltas. Delta time in MIDI must be non-negative.
    """
    track = mido.MidiTrack()
    mid.tracks.append(track)
    # No program_change needed on channel 9 — it's always the GM drum kit.

    total_ticks = total_beats * TICKS_PER_BEAT
    bar_ticks = 4 * TICKS_PER_BEAT         # 1 bar = 4 beats in this simple model.
    bars = total_ticks // bar_ticks
    hit_len = 10                           # Drum hit = very short note.

    # Build a flat list of absolute-tick events: (tick, kind, note).
    events: list[tuple[int, str, int]] = []
    for bar in range(bars):
        for note, beat in drum_pattern:
            tick = bar * bar_ticks + int(beat * TICKS_PER_BEAT)
            events.append((tick, "on", note))
            events.append((tick + hit_len, "off", note))

    # Sort by (tick, kind) — note_off before note_on at the same tick avoids
    # overlapping identical notes confusing the synth.
    events.sort(key=lambda e: (e[0], 0 if e[1] == "off" else 1))

    last_tick = 0
    for tick, kind, note in events:
        delta = max(0, tick - last_tick)
        msg_type = "note_on" if kind == "on" else "note_off"
        velocity = 100 if kind == "on" else 0
        track.append(mido.Message(msg_type, note=note, velocity=velocity,
                                  channel=channel, time=delta))
        last_tick = tick
