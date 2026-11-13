# SoundStoreAI 🎵

A **100% local, 100% free, dinosaur-friendly** music generator.
No GPU, no cloud API, no model weights. Works on a 2014 MacBook Air.

## How it works (the whole secret in 4 lines)

1. Pick a scale and a chord progression (music theory).
2. Walk the scale with a tiny **Markov chain** to build a melody.
3. Write everything out as a **MIDI** file.
4. Feed the MIDI to **FluidSynth** + a free **SoundFont** → real `.wav` audio.

That's it. No neural network. No GPU required. Instant on any machine.

## Quick start

```bash
cd SoundStoreAI
./setup.sh                      # installs fluidsynth + ffmpeg + python deps + soundfont
source .venv/bin/activate
streamlit run app.py
```

Browser opens at http://localhost:8501.

## Project layout

```
SoundStoreAI/
├── app.py                      # Streamlit UI (what you see in the browser)
├── requirements.txt            # Python deps (just streamlit + mido)
├── setup.sh                    # One-shot install for mac
├── assets/
│   └── FluidR3_GM.sf2          # Free General-MIDI SoundFont (downloaded by setup.sh)
├── output/                     # Generated .mid + .wav files land here
└── music_engine/               # The brains
    ├── theory.py               #   scales, chords, progressions (music theory)
    ├── markov.py               #   Markov-chain melody walker
    ├── drums.py                #   canned drum patterns per vibe
    ├── midi_writer.py          #   turn notes → .mid file
    ├── renderer.py             #   call fluidsynth → .wav file
    └── generator.py            #   glue layer: everything above in one function
```

## Teaching plan (suggested order)

1. **theory.py** — what's a scale, what's a chord? Numbers on a keyboard.
2. **markov.py** — "what's the next note?" explained in 30 lines.
3. **drums.py** — rhythm as a list of (drum, beat) pairs.
4. **midi_writer.py** — MIDI = a recipe for a player piano.
5. **renderer.py** — subprocess + fluidsynth = free synthesizer.
6. **app.py** — Streamlit: Python → UI in 150 lines.

## Troubleshooting

- **"fluidsynth not found"** → `brew install fluid-synth`.
- **"SoundFont missing"** → re-run `./setup.sh` or drop any `*.sf2` into `assets/`.
- **No sound in the browser?** → every browser plays `.wav`; try the Download button.

## Roadmap

Once you have a GPU, swap `renderer.py` for a MusicGen call — the rest of the app stays the same.
