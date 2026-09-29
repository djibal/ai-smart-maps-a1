"""Synthetic OSM road network and change generators."""
from dataclasses import dataclass

import numpy as np

KINDS = ("added", "removed", "modified")


@dataclass
class RoadSegment:
    id: int
    length_km: float


@dataclass
class Change:
    segment_id: int
    month: int
    kind: str


def make_network(n_km, seed):
    """Build ~n_km of road as unit-ish segments with rng-drawn lengths."""
    rng = np.random.default_rng(seed)
    n = max(1, int(round(float(n_km))))
    lengths = rng.uniform(0.5, 1.5, size=n)
    lengths *= float(n_km) / lengths.sum()
    return [RoadSegment(id=i, length_km=float(lengths[i])) for i in range(n)]


def make_changes(segments, rate_per_km_month, horizon_months, seed):
    """Sample OSM edits over segments at ~rate_per_km_month per km per month.

    Months are 1..horizon_months. Per segment-month, event count is
    Poisson(rate_per_km_month * length_km); each event gets a random kind.
    """
    rng = np.random.default_rng(seed)
    changes = []
    for seg in segments:
        for month in range(1, int(horizon_months) + 1):
            lam = float(rate_per_km_month) * seg.length_km
            n_events = int(rng.poisson(lam))
            for _ in range(n_events):
                kind = KINDS[int(rng.integers(0, len(KINDS)))]
                changes.append(Change(segment_id=seg.id, month=month, kind=kind))
    return changes
