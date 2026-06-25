from app.speech.record_audio import record_audio
from app.speech.transcribe_audio import transcribe_audio
from app.llm.define_word import define_word
from app.models.vocabulary_entry import VocabularyEntry
from app.storage.json_storage import save_entry

def main() -> None:
    audio_path = "data/test.wav"

    record_audio(output_path = audio_path, duration=3)
    word = transcribe_audio(audio_path).strip()

    if not word:
        print("No word recognized. Please try again.")
        return
    
    print(f"Recognized: {word}")

    try:
        word_definition = define_word(word)
    except Exception as error:
        print("Could not generate a valid definition.")
        print(f"Error : {error}")
        return

    print("Definition:", word_definition.definition)
    print("Example:", word_definition.example)
    print("Language:", word_definition.language)

    entry = VocabularyEntry(
        word=word,
        definition=word_definition.definition,
        example=word_definition.example,
        language=word_definition.language,
        source="voice",
    )

    save_entry(entry)

    print("Saved to vocabulary.json")

if __name__ == "__main__":
    main()
