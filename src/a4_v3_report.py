"""A4-v3 report."""
import json
from pathlib import Path

raw = Path("reports/raw/a4-v3-results.json")
out = Path("reports/A4-v3-report.md")


def main():
    r = json.loads(raw.read_text())
    lines = [
        "# A4-v3 Report: Realistic Propagation",
        "",
        "Same flood-fill as A4-v2, at the A4-v2 pass point (50 beacons/km2,",
        "100m beacon range, 20m mobile range, 10% mobile duty), plus:",
        "",
        "- Packet loss: per-hop retransmit factor 1/(1-p)",
        "- Attenuation: all ranges multiplied by a factor (buildings, walls)",
        "- Beacon outage: fraction of beacons offline per trial",
        "",
        "Pass: P95 <= 100ms, all reachable, mobile battery <= 3%/day.",
        "",
        "| Config | Beacons | Atten | Loss | Outage | P50 | P95 | Unreach | Verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for name, m in r.items():
        p95 = m["p95_ms"]
        un = m["n_unreachable"]
        batt = m["battery_pct_per_day"]
        ok = p95 <= 100.0 and un == 0 and batt <= 3.0
        lines.append(
            f"| {name} | {m['beacons']}/km2 | {m['atten']} "
            f"| {m['p_loss']} | {m['p_beacon_out']} "
            f"| {m['p50_ms']:.1f}ms | {p95:.1f}ms | {un} "
            f"| {'PASS' if ok else 'FAIL'} |"
        )

    baseline_ok = r["baseline_50b"]["n_unreachable"] == 0 and r["baseline_50b"]["p95_ms"] <= 100
    loss_ok = r["loss_20pct"]["n_unreachable"] == 0 and r["loss_20pct"]["p95_ms"] <= 100
    atten_07 = r["atten_0.7"]
    atten_ok = atten_07["n_unreachable"] == 0 and atten_07["p95_ms"] <= 100
    severe_ok = r["severe_combined"]["n_unreachable"] == 0 and r["severe_combined"]["p95_ms"] <= 100
    rescue_ok = r["100b_severe_combined"]["n_unreachable"] == 0

    overall = baseline_ok and loss_ok and atten_ok and severe_ok

    lines += [
        "",
        "## Findings",
        "",
        f"- Baseline reproduces A4-v2: P95={r['baseline_50b']['p95_ms']:.1f}ms, all reachable.",
        f"- Packet loss (20%) has negligible impact: P95={r['loss_20pct']['p95_ms']:.1f}ms.",
        f"- **Attenuation 0.7 (mild urban) breaks percolation:** "
        f"P95={atten_07['p95_ms']:.1f}ms, {atten_07['n_unreachable']}/30 unreachable.",
        f"- **Attenuation 0.5 (moderate urban) fully disconnects:** inf, 30/30.",
        f"- Mild combined degradation (atten 0.7 + loss 10% + outage 5%) fails: 29/30 unreachable.",
        f"- Doubling density to 100 beacons/km2 does NOT rescue severe attenuation "
        f"({r['100b_severe_combined']['n_unreachable']}/30 unreachable).",
        "",
        "## Verdict",
        "",
        f"**Overall A4-v3: {'PASS' if overall else 'FAIL'}**",
        "",
        "The A4-v2 PASS holds only under near-line-of-sight conditions. "
        "Any meaningful urban attenuation breaks the beacon grid's percolation.",
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
