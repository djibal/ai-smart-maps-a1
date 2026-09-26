"""A4-v2 report."""
import json
from pathlib import Path

raw = Path("reports/raw/a4-v2-results.json")
out = Path("reports/A4-v2-report.md")


def main():
    r = json.loads(raw.read_text())
    lines = [
        "# A4-v2 Report: Civic Beacons in the Mesh",
        "",
        "Same flood-fill model as A4, plus mains-powered civic beacons",
        "(100m range, always on, on a grid). Metric: P95 latency for 90%",
        "coverage of a 200m circle. Pass: P95 <= 100ms, all reachable,",
        "mobile battery <= 3%/day.",
        "",
        "| Config | Beacons | Beacon R | Mobile R | Mobile Duty | P50 | P95 | Unreach | Verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    any_pass = False
    for name, m in r.items():
        p95 = m["p95_ms"]
        un = m["n_unreachable"]
        batt = m["battery_pct_per_day"]
        ok = p95 <= 100.0 and un == 0 and batt <= 3.0
        if ok:
            any_pass = True
        lines.append(
            f"| {name} | {m['beacons']}/km2 | {m['beacon_radius']}m "
            f"| {m['mobile_radius']}m | {m['mobile_duty']} "
            f"| {m['p50_ms']:.1f}ms | {p95:.1f}ms | {un} "
            f"| {'PASS' if ok else 'FAIL'} |"
        )

    lines += [
        "",
        "## Verdict",
        "",
        f"**Overall A4-v2: {'PASS' if any_pass else 'FAIL'}**",
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
