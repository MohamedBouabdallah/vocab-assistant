from app.speech.record_audio import record_audio
from app.speech.transcribe_audio import transcribe_audio
from app.llm.define_word import define_word
from app.models.vocabulary_entry import VocabularyEntry
from app.storage.json_storage import save_entry

def main() -> None:
    audio_path = "data/test.wav"

    record_audio(output_path = audio_path, duration=3)
    word = transcribe_audio(audio_path).strip()
    print(f"Recognized: {word}")

    definition = define_word(word)
    print(definition)

    entry = VocabularyEntry(
        word=word,
        definition=definition,
        source="voice",
    )

    save_entry(entry)

    print("Saved to vocabulary.json")

if __name__ == "__main__":
    main()
