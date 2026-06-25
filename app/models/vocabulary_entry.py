from datetime import datetime
from pydantic import BaseModel, Field

class VocabularyEntry(BaseModel):
    word: str
    definition: str
    example: str | None = None
    language: str | None = None
    source: str = "voice"
    reviewed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)