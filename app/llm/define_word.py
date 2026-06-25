import ollama

def define_word(word: str) -> str:
    prompt = f"""
You are a strict vocabulary assistant.

Term or expression:
"{word}"

Rules:
- Detect the language of the term or expression.
- Your answer MUST be entirely in that same language.
- Do NOT mention the detected language.
- Do NOT translate the example.
- Do NOT use English unless the term itself is English.
- If the term is technical, explain it simply.
- Return exactly two lines.

Output format:
Definition: <definition in the same language as the term>
Example: <example sentence in the same language as the term>
"""
    response = ollama.chat(
        model = "qwen2:7b",
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return response["message"]["content"]

if __name__ == "__main__":
    word = input("Word to define: ")
    definition = define_word(word)
    print(definition)