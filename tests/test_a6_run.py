import json

import numpy as np

from src.a6_run import one_trial, run_experiment
from src.osm.detectors import (
    combine_detections,
    observe_osm,
    observe_satellite,
    observe_user,
)
from src.osm.network import make_changes, make_network


def test_main_runs_end_to_end(tmp_path):
    out_path = tmp_path / "a6-results.json"
    results = run_experiment(
        out_path=out_path,
        n_km=50,
        horizon_months=6,
        rate_per_km_month=1 / 100,
        n_trials=1,
    )
    assert out_path.exists()
    data = json.loads(out_path.read_text())
    assert set(data) >= {"osm", "satellite", "user", "combined", "n_trials", "n_changes_total"}
    assert data["n_trials"] == 1
    assert isinstance(data["n_changes_total"], int)
    assert data["n_changes_total"] >= 0
    assert results["n_trials"] == 1
    for ch in ("osm", "satellite", "user", "combined"):
        assert ch in data
        for key in ("mean_lag_days", "detect_90d", "detect_90d_std"):
            assert key in data[ch]


def test_combined_never_worse_than_single(tmp_path):
    # Aggregated mean_lag averages different detection sets per channel, so
    # combined mean_lag is not guaranteed <= min(single-channel means). The
    # true "never worse" invariant is element-wise: combined lag <= each
    # channel's lag for every change.
    seed = 0
    n_km = 200
    horizon_months = 12
    rate = 1 / 100

    segments = make_network(n_km, seed=seed)
    changes = make_changes(segments, rate, horizon_months, seed=seed)
    osm_days = observe_osm(changes, seed=seed) * 30.44
    sat_days = observe_satellite(changes, seed=seed)
    user_days = observe_user(changes, seed=seed)
    combined = combine_detections(osm_days, sat_days, user_days)

    assert np.all(combined <= osm_days)
    assert np.all(combined <= sat_days)
    assert np.all(combined <= user_days)

    # Also: on each single channel's detected subset, combined mean <= channel mean.
    for lags in (osm_days, sat_days, user_days):
        mask = np.isfinite(lags)
        if not np.any(mask):
            continue
        assert np.mean(combined[mask]) <= np.mean(lags[mask]) + 1e-6

    # Sanity: aggregated detect_90d of combined >= each single channel.
    out_path = tmp_path / "a6-results.json"
    results = run_experiment(
        out_path=out_path,
        n_km=200,
        horizon_months=12,
        rate_per_km_month=rate,
        n_trials=3,
    )
    c90 = results["combined"]["detect_90d"]
    for ch in ("osm", "satellite", "user"):
        assert c90 >= results[ch]["detect_90d"] - 1e-12

    # one_trial is available for callers that need raw lag arrays.
    stats, n_changes, lag_by_channel = one_trial(
        n_km=200, horizon_months=12, rate_per_km_month=rate, seed=1
    )
    assert n_changes >= 0
    assert "combined" in stats
    assert set(lag_by_channel) == {"osm", "satellite", "user", "combined"}
