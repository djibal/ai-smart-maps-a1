"""TDLA report: temporal data lifecycle claim verification."""
import json
from pathlib import Path

from src.tdla.tiers import TIER_COMPRESSION, Tier

DEFAULT_INPUT = Path("reports/raw/tdla-results.json")
DEFAULT_OUTPUT = Path("reports/TDLA-report.md")

_TIERS = (Tier.HOT, Tier.WARM, Tier.COLD, Tier.ARCHIVE)


def _format_compression(factor: float) -> str:
    """Show compression factors as 1.0, 0.4, 0.05, 0.01."""
    value = float(factor)
    if value == int(value):
        return f"{value:.1f}"
    return f"{value:.2f}".rstrip("0")


def _format_ms(value: float) -> str:
    return f"{float(value):.1f}"


def _snapshot_on_day(snapshots: dict, day: int) -> dict:
    """Day keys may be int (hand-built dicts) or str (JSON)."""
    if day in snapshots:
        return snapshots[day]
    return snapshots[str(day)]


def _stored_total_kb(snapshot: dict) -> float:
    total = 0.0
    for tier in _TIERS:
        total += float(snapshot[tier.value]["total_stored_size_kb"])
    return total


def _storage_converges(snapshots: dict, final_day: int) -> bool:
    """PASS when final/day-730 stored KB is inside [0.9, 1.2]."""
    final_total = _stored_total_kb(_snapshot_on_day(snapshots, int(final_day)))
    day_730_total = _stored_total_kb(_snapshot_on_day(snapshots, 730))
    if day_730_total == 0:
        return final_total == 0
    ratio = final_total / day_730_total
    return 0.9 <= ratio <= 1.2


def _latency_slos_met(latency: dict) -> bool:
    return all(bool(latency[tier.value]["pass"]) for tier in _TIERS)


def _result(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def _verdict(storage_ok: bool, latency_ok: bool) -> tuple[str, str]:
    if not storage_ok:
        return (
            "**Overall TDLA: FAIL**",
            "Stored volume grew outside the convergence band between day 730 "
            "and the final day.",
        )
    if not latency_ok:
        return (
            "**Overall TDLA: PARTIAL PASS**",
            "Storage stayed inside the convergence band, and at least one "
            "tier missed its latency SLO.",
        )
    return (
        "**Overall TDLA: STRONG PASS**",
        "Storage stayed inside the convergence band and every tier met its "
        "latency SLO.",
    )


def build_report(input_data: dict, output_path: Path) -> str:
    """input_data schema:
    {
      "config": {n_cities, sim_days, segment_km_per_city},
      "aggregate": {"snapshots": {day: {tier: {count, total_stored_size_kb}}},
                    "final_day": int, "n_cities": int},
      "latency": {tier_name: {"p95_ms": float, "slo_ms": float, "pass": bool}},
    }
    Writes Markdown to output_path. Returns the Markdown string.
    """
    output_path = Path(output_path)
    config = input_data["config"]
    aggregate = input_data["aggregate"]
    latency = input_data["latency"]
    snapshots = aggregate["snapshots"]
    final_day = int(aggregate["final_day"])
    final_snapshot = _snapshot_on_day(snapshots, final_day)

    storage_ok = _storage_converges(snapshots, final_day)
    latency_ok = _latency_slos_met(latency)
    verdict_line, summary = _verdict(storage_ok, latency_ok)

    lines = [
        "# TDLA Report: Temporal Data Lifecycle Architecture",
        "",
        "TDLA (ADR-0006) proposes a four-tier temporal data lifecycle",
        "(HOT/WARM/COLD/ARCHIVE) to bound storage and meet per-tier",
        "latency SLOs.",
        "This report tests both claims.",
        "",
        "## Configuration",
        "",
        f"- Cities (n_cities): {config['n_cities']}",
        f"- sim_days: {config['sim_days']}",
        f"- segment_km_per_city: {config['segment_km_per_city']}",
        "",
        "## Storage",
        "",
        "| Tier | Final count | Stored (PB) | Compression |",
        "|---|---|---|---|",
    ]

    for tier in _TIERS:
        stats = final_snapshot[tier.value]
        stored_pb = float(stats["total_stored_size_kb"]) / (1024 ** 4)
        factor = _format_compression(TIER_COMPRESSION[tier])
        lines.append(
            f"| {tier.name} | {int(stats['count'])} | {stored_pb:.8f} | {factor} |"
        )

    lines += [
        "",
        "## Latency",
        "",
        "| Tier | SLO (ms) | p95 (ms) | Verdict |",
        "|---|---|---|---|",
    ]

    for tier in _TIERS:
        entry = latency[tier.value]
        verdict = _result(bool(entry["pass"]))
        lines.append(
            f"| {tier.name} | {_format_ms(entry['slo_ms'])} | "
            f"{_format_ms(entry['p95_ms'])} | {verdict} |"
        )

    lines += [
        "",
        "## Claim verification",
        "",
        f"- Storage converges?: {_result(storage_ok)}",
        f"- All latency SLOs met?: {_result(latency_ok)}",
        "",
        "## Verdict",
        "",
        verdict_line,
        "",
        summary,
        "",
    ]

    text = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text)
    return text


def main() -> None:
    """Read reports/raw/tdla-results.json, write reports/TDLA-report.md."""
    input_data = json.loads(DEFAULT_INPUT.read_text())
    text = build_report(input_data, DEFAULT_OUTPUT)
    print(text)
    print(f"wrote {DEFAULT_OUTPUT}")


if __name__ == "__main__":
    main()
