from faster_whisper import WhisperModel

def transcribe_audio(audio_path: str = "data/test.wav") -> str:
    model = WhisperModel(
        "base",
        device = "cpu",
        compute_type = "int8",
    )

    segments, info = model.transcribe(
        audio_path,
        language = None,
    )

    text = " ".join(segment.text.strip() for segment in segments)

    return text

if __name__ == "__main__":
    transcription = transcribe_audio()
    print("Transcription:", transcription)