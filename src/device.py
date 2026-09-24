"""On-device proxy runner using qwen2.5:0.5b via Ollama."""
import ollama
from src.graph import Scenario
from src.cloud import build_prompt

MODEL = "qwen2.5:0.5b"


def pick(scenario: Scenario) -> int:
    r = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": build_prompt(scenario)}],
    )
    text = r["message"]["content"].strip()
    for tok in text.replace(",", " ").split():
        if tok.isdigit():
            idx = int(tok)
            if 0 <= idx < len(scenario.routes):
                return idx
    return -1
