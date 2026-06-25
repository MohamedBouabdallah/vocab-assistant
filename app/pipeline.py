from app.speech.record_audio import record_audio
from app.speech.transcribe_audio import transcribe_audio
from app.llm.define_word import define_word
from app.models.vocabulary_entry import VocabularyEntry
from app.storage.json_storage import save_entry, load_entries


def listen_and_transcribe() -> str:
    """
    Enregistre l'audio puis retourne le mot transcrit.

    Cette fonction ne définit pas le mot.
    Elle sert uniquement à remplir le champ texte dans l'interface.
    """
    audio_path = record_audio()
    word = transcribe_audio(audio_path) if audio_path else transcribe_audio()
    return word.strip()


def define_and_save_word(word: str) -> VocabularyEntry:
    """
    Prend un mot validé par l'utilisateur,
    demande une définition au LLM,
    crée un VocabularyEntry,
    sauvegarde l'entrée dans le JSON,
    puis retourne l'entrée créée.
    """
    word = word.strip()

    if not word:
        raise ValueError("Le mot ne peut pas être vide.")

    word_definition = define_word(word)

    entry = VocabularyEntry(
        word=word,
        definition=word_definition.definition,
        example=word_definition.example,
        language=word_definition.language,
        source="voice",
        reviewed=False,
    )

    save_entry(entry)

    return entry


def get_vocabulary_entries():
    """
    Charge les entrées sauvegardées.
    """
    return load_entries()
