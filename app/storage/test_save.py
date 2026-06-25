from app.models.vocabulary_entry import VocabularyEntry
from app.storage.json_storage import save_entry


entry = VocabularyEntry(
    word="libellule",
    definition="Insecte au corps long et fin, avec quatre ailes transparentes.",
    example="Une libellule vole au-dessus de l’étang.",
    language="fr",
)

save_entry(entry)

print("Entry saved.")