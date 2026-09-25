"""Aggregate A1-v3 results into a report."""
import json
from pathlib import Path

raw = Path("reports/raw/eval-summary.json")
out = Path("reports/A1-v3-report.md")


def main():
    results = json.loads(raw.read_text())
    lines = [
        "# A1-v3 Report",
        "",
        "Task: binary route choice. Oracle = deterministic cost.",
        "Cloud model: MLP 4->128->128->128->1. Device model: MLP 4->16->1.",
        "Test set: 1000 scenarios per cost variant.",
        "",
        "| Variant | Cloud | Device | Delta | Verdict |",
        "|---|---|---|---|---|",
    ]

    all_pass = True
    for variant, r in results.items():
        c = r["cloud_agreement"]
        d = r["device_agreement"]
        delta = r["delta_pp"]
        v = "PASS" if (d >= c - 3.0) else "FAIL"
        if v == "FAIL":
            all_pass = False
        lines.append(f"| {variant} | {c:.1f}% | {d:.1f}% | {delta:.1f}pp | {v} |")

    lines.append("")
    lines.append(f"## Overall: {'PASS' if all_pass else 'FAIL'}")
    lines.append("")
    lines.append("Criterion: device agreement within 3pp of cloud on every variant.")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
