"""
app.py — the Streamlit UI.

Run it with:        streamlit run app.py
That opens http://localhost:8501 in your browser.

Streamlit tip for dummies: this file re-runs top-to-bottom EVERY time the user
touches a widget. Variables are not kept between runs unless you stash them in
st.session_state. That's weird at first but it's the whole trick.
"""

from pathlib import Path
import time

import streamlit as st

from music_engine.generator import generate_song
from music_engine.renderer import render_midi_to_wav

# ---------------------------------------------------------------------------
#  Paths. Having them at the top means we never hardcode strings deeper down.
# ---------------------------------------------------------------------------

PROJECT = Path(__file__).parent
OUTPUT_DIR = PROJECT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Our bundled free SoundFont. Install script puts it here.
SOUNDFONT = PROJECT / "assets" / "FluidR3_GM.sf2"

# ---------------------------------------------------------------------------
#  Page config — title + icon that show in the browser tab.
# ---------------------------------------------------------------------------

st.set_page_config(page_title="SoundStoreAI", page_icon="🎵", layout="centered")
st.title("🎵 SoundStoreAI")
st.caption("Local, offline, free. Generates music from music-theory rules + a Markov chain.")

# ---------------------------------------------------------------------------
#  Guard: we can't do anything without a SoundFont. Show instructions early.
# ---------------------------------------------------------------------------

if not SOUNDFONT.exists():
    st.error(
        "**SoundFont missing.** Download a free General-MIDI soundfont and "
        f"save it as `{SOUNDFONT.relative_to(PROJECT)}`.\n\n"
        "Easiest: run the install script `./setup.sh` from the project root."
    )
    st.stop()

# ---------------------------------------------------------------------------
#  Sidebar controls.
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Compose")

    # Key = which note the piece is centred on. The Markov engine builds a
    # scale starting from here.
    root = st.selectbox("Key", ["C", "D", "E", "F", "G", "A", "B"], index=0)

    # Mood = scale choice. See music_engine/theory.py for the recipes.
    scale = st.selectbox(
        "Mood (scale)",
        ["major", "minor", "blues", "pentatonic_major", "pentatonic_minor", "dorian"],
        index=0,
        help="Major = bright · Minor = sad · Blues = gritty · Pentatonic = can't go wrong"
    )

    # Chord backbone.
    progression = st.selectbox(
        "Chord progression",
        ["pop", "blues", "sad", "jazz"],
        index=0,
    )

    # Drum vibe.
    drum_style = st.selectbox(
        "Drums",
        ["rock", "hip_hop", "ballad", "none"],
        index=0,
    )

    tempo = st.slider("Tempo (BPM)", 60, 180, value=110)
    bars  = st.slider("Length (bars)", 4, 32, value=8,
                       help="1 bar = 4 beats. 8 bars at 110 BPM ≈ 17 seconds.")

    # Melody instrument (General MIDI numbers).
    #   0 = Grand Piano, 24 = Nylon Guitar, 56 = Trumpet, 73 = Flute, 80 = Synth lead.
    mel_inst = st.selectbox(
        "Melody instrument",
        options=[0, 24, 56, 73, 80],
        format_func=lambda n: {0: "Piano", 24: "Guitar", 56: "Trumpet",
                                73: "Flute", 80: "Synth lead"}[n],
    )

    # Seed = reproducibility. Same seed + same settings = same song.
    seed_input = st.text_input("Seed (optional)", placeholder="leave blank for random")
    seed = int(seed_input) if seed_input.strip().isdigit() else None

    generate_clicked = st.button("🎼  Generate", type="primary", use_container_width=True)

# ---------------------------------------------------------------------------
#  Main area — results.
# ---------------------------------------------------------------------------

if generate_clicked:
    # Unique filename per run so previous clips don't get overwritten.
    stamp = int(time.time())
    midi_file = OUTPUT_DIR / f"song_{stamp}.mid"
    wav_file  = OUTPUT_DIR / f"song_{stamp}.wav"

    try:
        # 1. Compose + write MIDI.
        with st.spinner("Composing..."):
            generate_song(
                out_path=midi_file,
                root=root,
                scale=scale,
                progression=progression,
                drum_style=drum_style,
                tempo=tempo,
                bars=bars,
                seed=seed,
                melody_instrument=mel_inst,
            )

        # 2. Render to audio.
        with st.spinner("Rendering audio..."):
            render_midi_to_wav(midi_file, SOUNDFONT, wav_file)

    except Exception as exc:                   # noqa: BLE001 — teaching clarity.
        st.error(f"Something went wrong: {exc}")
        st.stop()

    st.success("Done! Play it below.")

    # Audio player + download buttons.
    audio_bytes = wav_file.read_bytes()
    st.audio(audio_bytes, format="audio/wav")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "⬇️  Download WAV",
            data=audio_bytes,
            file_name=wav_file.name,
            mime="audio/wav",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            "⬇️  Download MIDI",
            data=midi_file.read_bytes(),
            file_name=midi_file.name,
            mime="audio/midi",
            use_container_width=True,
        )

    # Little recap for teaching: show the settings that produced this clip.
    with st.expander("What just happened?"):
        st.write(
            f"- Built a **{scale}** scale starting from **{root}**.\n"
            f"- Generated **{bars * 4}** notes with a Markov chain walking that scale.\n"
            f"- Played the **{progression}** chord progression underneath.\n"
            f"- Added a **{drum_style}** drum pattern looped for {bars} bars.\n"
            f"- Tempo: **{tempo} BPM**.\n"
            f"- Wrote `{midi_file.name}` and rendered it with FluidSynth → `{wav_file.name}`."
        )

else:
    st.info("Pick settings in the sidebar, then hit **Generate**.")
