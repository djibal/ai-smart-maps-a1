"""Cloud reference runner using llama3.2:3b via Ollama."""
import json
import ollama
from src.graph import Scenario, route_cost

MODEL = "llama3.2:3b"


def build_prompt(scenario: Scenario) -> str:
    lines = ["Graph edges (src, dst, weight, hazard):"]
    for e in scenario.edges:
        lines.append(f"  {e.src} -> {e.dst}  w={e.weight:.2f} h={e.hazard:.2f}")
    lines.append("")
    lines.append("Candidate routes (node sequences):")
    for i, r in enumerate(scenario.routes):
        lines.append(f"  [{i}] {r}")
    lines.append("")
    lines.append(
        "Pick the route index with lowest total cost. "
        "Cost = sum of weights + 3x hazards along the route. "
        "Missing edges cost 50. Reply with ONLY the index number."
    )
    return "\n".join(lines)


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
    return -1  # malformed
