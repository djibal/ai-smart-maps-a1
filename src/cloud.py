"""Cloud reference runner using llama3.2:3b via Ollama."""
import ollama
from src.graph import Scenario

MODEL = "llama3.2:3b"


def build_prompt(scenario: Scenario) -> str:
    lines = ["Graph edges (src -> dst, weight, hazard):"]
    for e in scenario.edges:
        lines.append(f"  {e.src} -> {e.dst}  w={e.weight:.2f} h={e.hazard:.2f}")
    lines.append("")
    lines.append(f"Route A: {scenario.routes[0]}")
    lines.append(f"Route B: {scenario.routes[1]}")
    lines.append("")
    lines.append(
        "Cost of a route = sum of weights + 3x hazards along each edge. "
        "Missing edges cost 50. "
        "Which route is cheaper, A or B? Reply with ONLY the letter A or B."
    )
    return "\n".join(lines)


def pick(scenario: Scenario) -> int:
    r = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": build_prompt(scenario)}],
    )
    text = r["message"]["content"].strip().upper()
    if "A" in text:
        return 0
    if "B" in text:
        return 1
    return -1
