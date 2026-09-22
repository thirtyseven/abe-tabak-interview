import json
from pathlib import Path

import numpy as np
import torch
from huggingface_hub import get_token
from pyannote.audio import Pipeline
from scipy.io import wavfile


ROOT = Path(__file__).resolve().parents[2]
PILOT = ROOT / "work" / "tapes" / "pilot-tape1"
AUDIO = PILOT / "tape1-16k-mono.wav"
OUTPUT = PILOT / "diarization-auto.json"

sample_rate, samples = wavfile.read(AUDIO)
if samples.dtype == np.int16:
    samples = samples.astype(np.float32) / 32768.0
else:
    samples = samples.astype(np.float32)
waveform = torch.from_numpy(samples).unsqueeze(0)

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-community-1", token=get_token()
)
if torch.backends.mps.is_available():
    pipeline.to(torch.device("mps"))

result = pipeline(
    {"waveform": waveform, "sample_rate": sample_rate},
    min_speakers=2,
    max_speakers=6,
)
annotation = result.exclusive_speaker_diarization
turns = [
    {
        "start": round(turn.start, 3),
        "end": round(turn.end, 3),
        "speaker": speaker,
    }
    for turn, _, speaker in annotation.itertracks(yield_label=True)
]
speakers = sorted({turn["speaker"] for turn in turns})
OUTPUT.write_text(json.dumps({"num_speakers": len(speakers), "speakers": speakers, "turns": turns}, indent=2) + "\n")
print(f"Wrote {len(turns)} speaker turns to {OUTPUT}")
