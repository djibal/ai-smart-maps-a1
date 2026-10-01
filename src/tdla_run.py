"""TDLA: multi-city tiered storage and latency experiment."""
import json
from pathlib import Path

import numpy as np

from src.tdla.simulator import simulate_tiers
from src.tdla.tiers import TIER_LATENCY_P95_MS, Tier

CITY_CONFIG = {
    "n_cities": 100,
    "segment_km_per_city": 5000,
    "changes_per_segment_km_per_month": 1.0 / 100,
    "sim_days": 1095,
}

_TIER_NAMES = tuple(tier.value for tier in Tier)


def run_one_city(seed, sim_days, changes_per_day) -> dict:
    """Run simulate_tiers for one city, return its snapshots dict."""
    return simulate_tiers(
        n_days=sim_days,
        changes_per_day=changes_per_day,
        seed=seed,
    )


def aggregate_cities(city_results: list[dict]) -> dict:
    """Sum per-tier stored_size_kb and count across all cities at each
    snapshot day. Return:
    {
      "snapshots": {day: {tier: {count, total_stored_size_kb}}},
      "final_day": ...,
      "n_cities": len(city_results),
    }
    """
    days: set[int] = set()
    for city in city_results:
        days.update(int(day) for day in city["snapshots"])

    snapshots: dict[int, dict[str, dict[str, int | float]]] = {}
    for day in sorted(days):
        tiers: dict[str, dict[str, int | float]] = {}
        for tier_name in _TIER_NAMES:
            count = 0
            stored = 0.0
            for city in city_results:
                tier = city["snapshots"].get(day, {}).get(tier_name)
                if tier is None:
                    continue
                count += int(tier["count"])
                stored += float(tier["stored_size_kb"])
            tiers[tier_name] = {
                "count": int(count),
                "total_stored_size_kb": float(stored),
            }
        snapshots[int(day)] = tiers

    final_day = None
    if city_results:
        final_day = int(city_results[0]["final_day"])

    return {
        "snapshots": snapshots,
        "final_day": final_day,
        "n_cities": len(city_results),
    }


def check_latency_slos(seed) -> dict:
    """For each tier, sample 10 latencies uniform in [0.5, 1.1]*SLO
    (SLO values from src/tdla/tiers.py). Return
    {tier_name: {"p95_ms": ..., "slo_ms": ..., "pass": bool}}.
    """
    rng = np.random.default_rng(seed)
    latency: dict[str, dict[str, float | bool]] = {}
    for tier in Tier:
        slo = TIER_LATENCY_P95_MS[tier]
        samples = rng.uniform(0.5 * slo, 1.1 * slo, size=10)
        p95_ms = float(np.percentile(samples, 95))
        slo_ms = float(slo)
        latency[tier.value] = {
            "p95_ms": p95_ms,
            "slo_ms": slo_ms,
            "pass": bool(p95_ms <= slo_ms),
        }
    return latency


def _snapshots_with_string_days(snapshots: dict) -> dict:
    """JSON object keys are strings; match the in-memory payload to json.loads."""
    return {str(day): tiers for day, tiers in snapshots.items()}


def run_experiment(
    output_path: Path,
    n_cities: int = 100,
    sim_days: int = 1095,
    segment_km_per_city: int = 5000,
    seed: int = 0,
) -> dict:
    """Run the full experiment and write JSON to output_path.
    Returns the same dict that was written.
    """
    output_path = Path(output_path)
    changes_per_month = CITY_CONFIG["changes_per_segment_km_per_month"]
    changes_per_day = segment_km_per_city * changes_per_month / 30

    city_results = [
        run_one_city(
            seed=seed + city_index,
            sim_days=sim_days,
            changes_per_day=changes_per_day,
        )
        for city_index in range(n_cities)
    ]
    aggregate = aggregate_cities(city_results)
    latency = check_latency_slos(seed)

    payload = {
        "aggregate": {
            "snapshots": _snapshots_with_string_days(aggregate["snapshots"]),
            "final_day": aggregate["final_day"],
            "n_cities": int(aggregate["n_cities"]),
        },
        "latency": latency,
        "config": {
            "n_cities": int(n_cities),
            "sim_days": int(sim_days),
            "segment_km_per_city": int(segment_km_per_city),
            "changes_per_segment_km_per_month": float(changes_per_month),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(payload, f, indent=2)
    return payload


def main() -> None:
    """Call run_experiment with defaults, write
    reports/raw/tdla-results.json, print per-tier final-day storage in
    PB and latency pass/fail.
    """
    output_path = Path("reports/raw/tdla-results.json")
    results = run_experiment(output_path)
    final_day = str(results["aggregate"]["final_day"])
    day_snapshot = results["aggregate"]["snapshots"][final_day]
    for tier in Tier:
        name = tier.value
        stored_kb = day_snapshot[name]["total_stored_size_kb"]
        pb = stored_kb / (1024 ** 3)
        status = "PASS" if results["latency"][name]["pass"] else "FAIL"
        print(f"{name}: {pb:.8f} PB  latency {status}")
    print(f"\nwrote {output_path}")


if __name__ == "__main__":
    main()
