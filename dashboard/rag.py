from pathlib import Path
import anthropic


def retrieve_context(question: str, raw_dir: str, top_k: int = 3) -> str:
    """Search knowledge/raw/ markdown files and return top_k most relevant."""
    files = list(Path(raw_dir).glob("*.md"))
    question_words = set(question.lower().split())
    scores = []
    for f in files:
        content = f.read_text(encoding="utf-8")
        score = sum(1 for w in question_words if w in content.lower())
        scores.append((score, f.name, content))
    scores.sort(reverse=True)
    top = scores[:top_k]
    return "\n\n---\n\n".join(
        f"Source: {name}\n{content[:1500]}" for _, name, content in top
    )


def ask_claude(question: str, context: str, api_key: str) -> str:
    """Send question + retrieved context to Claude and return the answer."""
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": (
                f"Based on these industry sources:\n\n{context}\n\n"
                f"Answer this question concisely: {question}"
            ),
        }],
    )
    return message.content[0].text
