"""Synthetic daily update records and tier snapshots for TDLA."""
import numpy as np

from src.tdla.tiers import (
    Tier,
    TierStats,
    UpdateRecord,
    stored_size_kb,
    tier_for_age_days,
)

KINDS = ("added", "removed", "modified")
SIZE_SIGMA = 0.5
SEGMENT_SIGMA = 0.4


def _lognormal_mu(arithmetic_mean: float, sigma: float) -> float:
    """Convert an arithmetic mean to numpy's lognormal ``mean`` (mu of log X).

    ``Generator.lognormal(mean, sigma)`` treats ``mean`` as the mean of the
    underlying normal, not E[X]. With ``mu = log(M) - 0.5 * sigma**2``,
    E[X] = M.
    """
    return float(np.log(arithmetic_mean) - 0.5 * sigma**2)


def generate_updates(
    n_days: int,
    changes_per_day: float,
    mean_segment_km: float = 5.0,
    mean_size_kb: float = 20.0,
    seed: int = 0,
) -> list[UpdateRecord]:
    """Generate synthetic daily update records for n_days.

    Uses a Poisson process per day with rate changes_per_day.
    Each record: size drawn from LogNormal with mean mean_size_kb,
    sigma=0.5; segment_km from LogNormal with mean mean_segment_km,
    sigma=0.4; kind chosen uniformly from {added, removed, modified}.
    """
    rng = np.random.default_rng(seed)
    size_mu = _lognormal_mu(mean_size_kb, SIZE_SIGMA)
    segment_mu = _lognormal_mu(mean_segment_km, SEGMENT_SIGMA)

    records: list[UpdateRecord] = []
    next_id = 0
    for day in range(n_days):
        n = int(rng.poisson(changes_per_day))
        for _ in range(n):
            size_kb = float(rng.lognormal(mean=size_mu, sigma=SIZE_SIGMA))
            segment_km = float(
                rng.lognormal(mean=segment_mu, sigma=SEGMENT_SIGMA)
            )
            kind = str(rng.choice(KINDS))
            records.append(
                UpdateRecord(
                    id=next_id,
                    day=day,
                    size_kb=size_kb,
                    segment_km=segment_km,
                    kind=kind,
                )
            )
            next_id += 1
    return records


def tier_snapshot(
    records: list[UpdateRecord], current_day: int
) -> dict[Tier, TierStats]:
    """For a given current_day, compute age = current_day - record.day
    for each record, assign tier via tier_for_age_days, and return
    per-tier TierStats (count, total_size_kb raw, stored_size_kb after
    compression).
    """
    counts = {tier: 0 for tier in Tier}
    total_size = {tier: 0.0 for tier in Tier}
    stored_size = {tier: 0.0 for tier in Tier}

    for record in records:
        if record.day > current_day:
            continue
        age = current_day - record.day
        tier = tier_for_age_days(age)
        counts[tier] += 1
        total_size[tier] += float(record.size_kb)
        stored_size[tier] += float(stored_size_kb(record, tier))

    return {
        tier: TierStats(
            tier=tier,
            count=counts[tier],
            total_size_kb=float(total_size[tier]),
            stored_size_kb=float(stored_size[tier]),
        )
        for tier in Tier
    }


def _snapshot_days(n_days: int, snapshot_days: list[int] | None) -> list[int]:
    """Requested snapshot days, or the default schedule without duplicates."""
    if snapshot_days is not None:
        return list(snapshot_days)
    final_day = n_days - 1
    days = [7, 30, 90, 365, 730]
    if final_day not in days:
        days.append(final_day)
    return days


def _tier_stats_json(stats: TierStats) -> dict[str, int | float]:
    return {
        "count": int(stats.count),
        "total_size_kb": float(stats.total_size_kb),
        "stored_size_kb": float(stats.stored_size_kb),
    }


def simulate_tiers(
    n_days: int,
    changes_per_day: float,
    snapshot_days: list[int] | None = None,
    seed: int = 0,
) -> dict:
    """Run generate_updates once for n_days, then take tier snapshots
    at the requested days (or defaults [7, 30, 90, 365, 730, n_days-1]).
    Return dict:
    {
      "snapshots": {day: {tier_name: {count, total_size_kb, stored_size_kb}}},
      "final_day": n_days - 1,
      "total_updates": len(records),
    }
    """
    records = generate_updates(n_days, changes_per_day, seed=seed)
    days = _snapshot_days(n_days, snapshot_days)
    snapshots: dict[int, dict[str, dict[str, int | float]]] = {}
    for day in days:
        stats_by_tier = tier_snapshot(records, int(day))
        snapshots[int(day)] = {
            tier.value: _tier_stats_json(stats)
            for tier, stats in stats_by_tier.items()
        }
    return {
        "snapshots": snapshots,
        "final_day": int(n_days - 1),
        "total_updates": int(len(records)),
    }
