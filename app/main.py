from app.speech.record_audio import record_audio
from app.speech.transcribe_audio import transcribe_audio

def main() -> None:
    audio_path = "data/test.wav"

    record_audio(output_path = audio_path, duration=3)
    transcription = transcribe_audio(audio_path)

    print(f"Recognized text: {transcription}")

if __name__ == "__main__":
    main()
