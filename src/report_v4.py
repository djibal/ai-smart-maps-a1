"""Aggregate A1-v4 results into a report."""
import json
from pathlib import Path

raw = Path("reports/raw/eval-v4-summary.json")
out = Path("reports/A1-v4-report.md")


def main():
    results = json.loads(raw.read_text())
    lines = [
        "# A1-v4 Report",
        "",
        "Same architecture as v3. Only change: pairwise margin ranking loss",
        "instead of MSE. Objective matches the binary-choice metric.",
        "",
        "| Variant | Cloud | Device | Delta | Verdict |",
        "|---|---|---|---|---|",
    ]
    all_pass = True
    for variant, r in results.items():
        c, d, delta = r["cloud_agreement"], r["device_agreement"], r["delta_pp"]
        v = "PASS" if d >= c - 3.0 else "FAIL"
        if v == "FAIL":
            all_pass = False
        lines.append(f"| {variant} | {c:.1f}% | {d:.1f}% | {delta:.1f}pp | {v} |")

    lines += ["", f"## Overall: {'PASS' if all_pass else 'FAIL'}",
              "", "Criterion: device within 3pp of cloud on every variant."]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
