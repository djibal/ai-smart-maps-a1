import numpy as np

from src.osm.detectors import (
    combine_detections,
    observe_osm,
    observe_satellite,
    observe_user,
)
from src.osm.network import Change


def _changes(n, segment_ids=None):
    if segment_ids is None:
        segment_ids = list(range(n))
    return [
        Change(segment_id=int(sid), month=1, kind="modified")
        for sid in segment_ids
    ]


def test_observe_osm_lag_positive():
    changes = _changes(100)
    lags = observe_osm(changes, seed=0)
    assert len(lags) == len(changes)
    assert np.all(lags > 0)


def test_observe_satellite_detection_rate_in_range():
    changes = _changes(2000)
    lags = observe_satellite(changes, seed=42)
    rate = np.isfinite(lags).mean()
    assert 0.35 <= rate <= 0.65
    finite = lags[np.isfinite(lags)]
    assert np.all(finite >= 0)
    assert np.all(finite <= 30)


def test_observe_user_respects_coverage():
    coverage_frac = 0.60
    n = 500
    changes = _changes(n)  # one change per unique segment
    lags = observe_user(changes, p_detect=1.0, coverage_frac=coverage_frac, seed=3)
    finite_frac = np.isfinite(lags).mean()
    expected = round(coverage_frac * n) / n
    assert abs(finite_frac - expected) < 1e-12
    assert abs(finite_frac - coverage_frac) < 0.05
    assert np.all(lags[np.isfinite(lags)] == 7.0)


def test_combine_takes_minimum():
    a = np.array([1.0, np.inf, 5.0, 10.0])
    b = np.array([3.0, 2.0, np.inf, 4.0])
    c = np.array([np.inf, np.inf, 1.0, 8.0])
    # Already in days; no OSM month conversion needed in this unit test.
    result = combine_detections(a, b, c)
    expected = np.array([1.0, 2.0, 1.0, 4.0])
    np.testing.assert_array_equal(result, expected)
