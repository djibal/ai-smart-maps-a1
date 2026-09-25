"""A2 report."""
import json
from pathlib import Path

raw = Path("reports/raw/a2-results.json")
out = Path("reports/A2-report.md")


def main():
    r = json.loads(raw.read_text())
    c = r["centralized"]["final_acc"]
    honest = r["fedavg_honest"]["final_acc"]
    f1 = r["fedavg_1byz"]["final_acc"]
    f2 = r["fedavg_2byz"]["final_acc"]
    f3 = r["fedavg_3byz"]["final_acc"]
    kr = r["krum_3byz"]["final_acc"]
    tm = r["trimmed_3byz"]["final_acc"]

    fl_gap = c - honest
    damage = honest - f3
    krum_rec = kr - f3
    trim_rec = tm - f3

    fl_ok = fl_gap <= 5
    krum_ok = krum_rec >= 3
    trim_ok = trim_rec >= 3
    overall = fl_ok and (krum_ok or trim_ok)

    lines = [
        "# A2 Report: Federated Learning Convergence",
        "",
        f"Config: {10} devices, 500 samples/device, 20 FL rounds,",
        "non-IID partition (80% primary variant, remainder split).",
        "Attack: sign-flip of weight deltas.",
        "",
        "## Results",
        "",
        "| Config | Final accuracy |",
        "|---|---|",
        f"| Centralized (upper bound) | {c:.1f}% |",
        f"| FedAvg, no attackers | {honest:.1f}% |",
        f"| FedAvg, 1 Byzantine | {f1:.1f}% |",
        f"| FedAvg, 2 Byzantine | {f2:.1f}% |",
        f"| FedAvg, 3 Byzantine | {f3:.1f}% |",
        f"| Krum(f=3,m=3), 3 Byzantine | {kr:.1f}% |",
        f"| TrimmedMean(0.2), 3 Byzantine | {tm:.1f}% |",
        "",
        "## Findings",
        "",
        f"- FL viability: FedAvg honest is {fl_gap:.1f}pp below centralized. "
        f"{'PASS' if fl_ok else 'FAIL'} (<= 5pp).",
        f"- FedAvg attack damage (3 Byzantine): {damage:.1f}pp.",
        f"- Krum recovery over undefended FedAvg+3byz: +{krum_rec:.1f}pp.",
        f"- TrimmedMean recovery over undefended FedAvg+3byz: +{trim_rec:.1f}pp.",
        "",
        "## Verdict",
        "",
        f"- FL convergence: {'PASS' if fl_ok else 'FAIL'}",
        f"- Krum defense effective: {'PASS' if krum_ok else 'FAIL'}",
        f"- TrimmedMean defense effective: {'PASS' if trim_ok else 'FAIL'}",
        "",
        f"**Overall A2: {'PASS' if overall else 'FAIL'}**",
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
