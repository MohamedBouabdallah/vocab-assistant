import json
from pathlib import Path

from app.models.vocabulary_entry import VocabularyEntry

def load_entries(storage_path: str = "data/vocabulary.json") -> list[dict]:
    path = Path(storage_path)

    if not path.exists():
        return []
    
    with path.open("r", encoding = "utf-8") as file:
        return json.load(file)
    
def save_entry(
        entry: VocabularyEntry,
        storage_path: str = "data/vocabulary.json",
) -> None:
    entries = load_entries(storage_path)

    entries.append(entry.model_dump(mode="json"))

    path = Path(storage_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(entries, file, ensure_ascii=False, indent=2)