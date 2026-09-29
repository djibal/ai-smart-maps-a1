"""Detection lag models for OSM, satellite, and user-report channels."""
import numpy as np


def observe_osm(changes, mean_months=12.0, sigma=0.6, seed=0):
    """Sample OSM detection lag in months from a lognormal.

    ``mean_months`` is the arithmetic mean E[X]; ``sigma`` is the std of the
    underlying normal. Converted to numpy's lognormal ``mean`` (mu of log X)
    via mu = log(mean_months) - 0.5 * sigma**2.
    """
    n = len(changes)
    if n == 0:
        return np.array([], dtype=float)
    if mean_months <= 0:
        raise ValueError("mean_months must be positive")
    rng = np.random.default_rng(seed)
    mu = np.log(mean_months) - 0.5 * sigma**2
    return rng.lognormal(mean=mu, sigma=sigma, size=n)


def observe_satellite(changes, revisit_days=30, p_detect=0.50, seed=0):
    """Sample satellite detection lag in days; undetected changes get inf."""
    n = len(changes)
    if n == 0:
        return np.array([], dtype=float)
    rng = np.random.default_rng(seed)
    detected = rng.random(n) < p_detect
    lags = rng.uniform(0, revisit_days, size=n)
    return np.where(detected, lags, np.inf)


def observe_user(changes, p_detect=0.70, latency_days=7, coverage_frac=0.60, seed=0):
    """Sample user-report lag in days; uncovered or undetected get inf.

    Coverage is assigned by segment: unique segment ids are sorted, shuffled,
    and the first round(coverage_frac * n) are covered.
    """
    n = len(changes)
    if n == 0:
        return np.array([], dtype=float)
    rng = np.random.default_rng(seed)
    unique_ids = sorted({c.segment_id for c in changes})
    n_seg = len(unique_ids)
    n_covered = int(round(coverage_frac * n_seg))
    shuffled = list(unique_ids)
    rng.shuffle(shuffled)
    covered = set(shuffled[:n_covered])

    lags = np.full(n, np.inf, dtype=float)
    for i, change in enumerate(changes):
        if change.segment_id not in covered:
            continue
        if rng.random() < p_detect:
            lags[i] = float(latency_days)
    return lags


def combine_detections(*lag_arrays):
    """Element-wise minimum across lag arrays (all in the same units).

    Callers must convert OSM months to days (× 30.44) before combining.
    """
    if not lag_arrays:
        raise ValueError("at least one lag array is required")
    lengths = {len(a) for a in lag_arrays}
    if len(lengths) != 1:
        raise ValueError("all lag arrays must have the same length")
    return np.minimum.reduce(lag_arrays)
