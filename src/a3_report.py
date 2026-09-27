"""A3 report."""
import json
from pathlib import Path

raw = Path("reports/raw/a3-results.json")
out = Path("reports/A3-report.md")


def main():
    s = json.loads(raw.read_text())
    lines = [
        "# A3 Report: Byzantine-Fault-Tolerant Community Reports",
        "",
        "Config: 500 locations, 20 reporters, honest accuracy 85%,",
        "20 trials. Byzantine strategies: random, invert, coordinated.",
        "",
        "Pass criterion: at least one aggregator reaches >= 95% accuracy",
        "under 30% Byzantine.",
        "",
        "| Byzantine | Strategy | Majority | Supermajority | Reputation | Bayesian |",
        "|---|---|---|---|---|---|",
    ]
    for key, m in s.items():
        byz = m["byzantine_frac"]
        strat = m["strategy"]
        a = m["accuracy"]
        lines.append(
            f"| {byz*100:.0f}% | {strat} "
            f"| {a['majority']*100:.1f}% "
            f"| {a['supermajority']*100:.1f}% "
            f"| {a['reputation_weighted']*100:.1f}% "
            f"| {a['bayesian']*100:.1f}% |"
        )
    thirty_pct = [k for k in s if s[k]["byzantine_frac"] == 0.30]
    pass_any = False
    best_agg = None
    best_acc = 0.0
    for k in thirty_pct:
        for agg in s[k]["accuracy"]:
            if s[k]["accuracy"][agg] > best_acc:
                best_acc = s[k]["accuracy"][agg]
                best_agg = f"{s[k]['strategy']}/{agg}"
            if s[k]["accuracy"][agg] >= 0.95:
                pass_any = True
    lines += [
        "",
        "## Findings",
        "",
        f"- Best aggregator at 30% Byzantine: {best_agg} at {best_acc*100:.1f}%.",
        f"- Pass criterion met: {'YES' if pass_any else 'NO'}",
        "",
        "## Verdict",
        "",
        f"**Overall A3: {'PASS' if pass_any else 'FAIL'}**",
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
