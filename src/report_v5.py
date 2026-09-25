"""Report v5 as distribution across seeds."""
import json
from pathlib import Path

raw = Path("reports/raw/train-v5-summary.json")
out = Path("reports/A1-v5-report.md")


def main():
    s = json.loads(raw.read_text())
    lines = [
        "# A1-v5 Report",
        "",
        "5 seeds per variant. Device model grown to 32x2 (was 16x1).",
        "Criterion: device mean >= cloud mean - 3pp on every variant.",
        "",
        "| Variant | Cloud mean+/-std | Device mean+/-std | Delta | Verdict |",
        "|---|---|---|---|---|",
    ]
    all_pass = True
    for variant, r in s.items():
        c = r["cloud_mean"]
        d = r["device_mean"]
        delta = r["delta_mean_pp"]
        v = "PASS" if delta <= 3.0 else "FAIL"
        if v == "FAIL":
            all_pass = False
        lines.append(
            f"| {variant} | {c:.1f}+/-{r['cloud_std']:.1f} "
            f"| {d:.1f}+/-{r['device_std']:.1f} | {delta:.1f}pp | {v} |"
        )
    lines += ["", f"## Overall: {'PASS' if all_pass else 'FAIL'}"]

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
