"""Tiered storage ages and compression for map updates."""
from dataclasses import dataclass
from enum import Enum


class Tier(Enum):
    HOT = "hot"  # 0-7 days
    WARM = "warm"  # 7-90 days
    COLD = "cold"  # 90-730 days
    ARCHIVE = "archive"  # >730 days


@dataclass
class UpdateRecord:
    id: int
    day: int  # day the update was created (simulation time)
    size_kb: float  # raw size in KB
    segment_km: float  # length of segment affected
    kind: str  # "added", "removed", "modified"


@dataclass
class TierStats:
    tier: Tier
    count: int
    total_size_kb: float
    stored_size_kb: float  # after tier-specific compression/aggregation


TIER_AGE_BOUNDS: dict[Tier, tuple[int, int]] = {
    Tier.HOT: (0, 7),
    Tier.WARM: (7, 90),
    Tier.COLD: (90, 730),
    Tier.ARCHIVE: (730, 10**9),
}

TIER_COMPRESSION: dict[Tier, float] = {
    Tier.HOT: 1.0,  # raw
    Tier.WARM: 0.4,  # reduced resolution
    Tier.COLD: 0.05,  # aggregated statistics
    Tier.ARCHIVE: 0.01,  # compressed
}

TIER_LATENCY_P95_MS: dict[Tier, float] = {
    Tier.HOT: 10.0,
    Tier.WARM: 100.0,
    Tier.COLD: 5000.0,
    Tier.ARCHIVE: 30000.0,
}


def tier_for_age_days(age_days: int) -> Tier:
    """Return tier based on age in days."""
    if age_days < 0:
        raise ValueError(f"age_days must be non-negative, got {age_days}")

    tiers = (Tier.HOT, Tier.WARM, Tier.COLD, Tier.ARCHIVE)
    for index, tier in enumerate(tiers):
        lower, upper = TIER_AGE_BOUNDS[tier]
        if index == 0:
            if lower <= age_days <= upper:
                return tier
        elif lower < age_days <= upper:
            return tier

    raise ValueError(f"age_days {age_days} exceeds archive upper bound")


def stored_size_kb(record: UpdateRecord, tier: Tier) -> float:
    """Apply tier compression to record size."""
    return record.size_kb * TIER_COMPRESSION[tier]
