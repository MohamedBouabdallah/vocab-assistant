from pathlib import Path

import sounddevice as sd
import soundfile as sf

def record_audio(
        output_path: str = "data/test.wav",
        duration: int = 3,
        samplerate: int = 16000
) -> None:
    print("Recording... Speak now")

    audio = sd.rec(
        int(duration * samplerate),
        samplerate = samplerate,
        channels = 1,
        dtype = "float32",
    )

    sd.wait()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_path, audio, samplerate)

    print(f"Audio saved to {output_path}")

if __name__ == "__main__":
    record_audio()