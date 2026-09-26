import json
from pathlib import Path

raw = Path("reports/raw/a4-results.json")
out = Path("reports/A4-report.md")


def main():
    r = json.loads(raw.read_text())
    lines = [
        "# A4 Report: Mesh Density Simulation",
        "",
        "Flood-fill broadcast over duty-cycled BLE mesh.",
        "Metric: P95 time for 90% of nodes within 200m of source.",
        "Pass: P95 <= 100ms AND battery <= 3%/day AND unreachable == 0.",
        "",
        "| Config | Density | Radius | Duty | Battery | P50 | P95 | Unreach | Verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    any_pass = False
    for name, m in r.items():
        p95 = m["p95_ms"]
        batt = m["battery_pct_per_day"]
        un = m["n_unreachable"]
        ok = p95 <= 100.0 and batt <= 3.0 and un == 0
        if ok:
            any_pass = True
        lines.append(
            f"| {name} | {m['density']}/km2 | {m['radius_m']}m | {m['duty']} "
            f"| {batt:.2f}% | {m['p50_ms']:.1f}ms | {p95:.1f}ms | {un} "
            f"| {'PASS' if ok else 'FAIL'} |"
        )
    lines += ["", f"**Overall A4: {'PASS' if any_pass else 'FAIL'}**"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
