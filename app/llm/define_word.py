import ollama
from pydantic import BaseModel


class WordDefinition(BaseModel):
    definition: str
    example: str
    language: str


def define_word(word: str) -> WordDefinition:
    prompt = f"""
You are a strict vocabulary assistant.

Term or expression:
"{word}"

Task:
- Detect the language of the term or expression.
- Answer in French by default.
- If the term is foreign, give the meaning in French.
- If the term is foreign, the example must be in the original language and include a French translation.
- If the term is French, the example must be in French.
- Keep everything concise.

Return ONLY valid JSON with exactly these keys:
{{
  "definition": "...",
  "example": "...",
  "language": "..."
}}
"""

    response = ollama.chat(
        model="qwen2:7b",
        messages=[{"role": "user", "content": prompt}],
    )

    content = response["message"]["content"]

    return WordDefinition.model_validate_json(content)


if __name__ == "__main__":
    word = input("Word to define: ")
    result = define_word(word)
    print(result)