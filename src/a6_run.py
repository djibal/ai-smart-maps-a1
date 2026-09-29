"""A6: OSM vs satellite vs user detection-lag experiment."""
import json
from pathlib import Path

import numpy as np

from src.osm.network import make_network, make_changes
from src.osm.detectors import (
    observe_osm,
    observe_satellite,
    observe_user,
    combine_detections,
)

N_KM = 500
HORIZON_MONTHS = 36
RATE_PER_KM_MONTH = 1 / 100
N_TRIALS = 20

OSM_MEAN_MONTHS = 12.0
OSM_SIGMA = 0.6
SAT_REVISIT_DAYS = 30
SAT_P_DETECT = 0.50
USER_P_DETECT = 0.70
USER_LATENCY_DAYS = 7
USER_COVERAGE_FRAC = 0.60

MONTHS_TO_DAYS = 30.44
DETECT_HORIZON_DAYS = 90.0

CHANNELS = ("osm", "satellite", "user", "combined")


def _channel_stats(lags):
    """Per-channel mean lag (finite only) and 90-day detection rate."""
    n = len(lags)
    if n == 0:
        return np.nan, np.nan
    finite = lags[np.isfinite(lags)]
    mean_lag = float(np.mean(finite)) if len(finite) > 0 else np.nan
    detect_90d = float(np.mean(lags <= DETECT_HORIZON_DAYS))
    return mean_lag, detect_90d


def one_trial(
    n_km,
    horizon_months,
    rate_per_km_month,
    seed,
    osm_mean_months=OSM_MEAN_MONTHS,
    osm_sigma=OSM_SIGMA,
    sat_revisit_days=SAT_REVISIT_DAYS,
    sat_p_detect=SAT_P_DETECT,
    user_p_detect=USER_P_DETECT,
    user_latency_days=USER_LATENCY_DAYS,
    user_coverage_frac=USER_COVERAGE_FRAC,
):
    segments = make_network(n_km, seed=seed)
    changes = make_changes(segments, rate_per_km_month, horizon_months, seed=seed)

    osm_days = observe_osm(
        changes, mean_months=osm_mean_months, sigma=osm_sigma, seed=seed
    ) * MONTHS_TO_DAYS
    sat_days = observe_satellite(
        changes, revisit_days=sat_revisit_days, p_detect=sat_p_detect, seed=seed
    )
    user_days = observe_user(
        changes,
        p_detect=user_p_detect,
        latency_days=user_latency_days,
        coverage_frac=user_coverage_frac,
        seed=seed,
    )
    combined_days = combine_detections(osm_days, sat_days, user_days)

    lag_by_channel = {
        "osm": osm_days,
        "satellite": sat_days,
        "user": user_days,
        "combined": combined_days,
    }
    stats = {}
    for name, lags in lag_by_channel.items():
        mean_lag, detect_90d = _channel_stats(lags)
        stats[name] = {"mean_lag_days": mean_lag, "detect_90d": detect_90d}
    return stats, len(changes), lag_by_channel


def run_experiment(
    out_path,
    n_km=N_KM,
    horizon_months=HORIZON_MONTHS,
    rate_per_km_month=RATE_PER_KM_MONTH,
    n_trials=N_TRIALS,
    osm_mean_months=OSM_MEAN_MONTHS,
    osm_sigma=OSM_SIGMA,
    sat_revisit_days=SAT_REVISIT_DAYS,
    sat_p_detect=SAT_P_DETECT,
    user_p_detect=USER_P_DETECT,
    user_latency_days=USER_LATENCY_DAYS,
    user_coverage_frac=USER_COVERAGE_FRAC,
):
    """Run A6 trials and write aggregated results JSON to out_path."""
    out_path = Path(out_path)
    trial_means = {ch: [] for ch in CHANNELS}
    trial_detect = {ch: [] for ch in CHANNELS}
    n_changes_total = 0

    for trial in range(n_trials):
        stats, n_changes, _ = one_trial(
            n_km=n_km,
            horizon_months=horizon_months,
            rate_per_km_month=rate_per_km_month,
            seed=trial,
            osm_mean_months=osm_mean_months,
            osm_sigma=osm_sigma,
            sat_revisit_days=sat_revisit_days,
            sat_p_detect=sat_p_detect,
            user_p_detect=user_p_detect,
            user_latency_days=user_latency_days,
            user_coverage_frac=user_coverage_frac,
        )
        n_changes_total += n_changes
        for ch in CHANNELS:
            trial_means[ch].append(stats[ch]["mean_lag_days"])
            trial_detect[ch].append(stats[ch]["detect_90d"])

    results = {
        ch: {
            "mean_lag_days": float(np.nanmean(trial_means[ch])),
            "detect_90d": float(np.nanmean(trial_detect[ch])),
            "detect_90d_std": float(np.nanstd(trial_detect[ch])),
        }
        for ch in CHANNELS
    }
    results["n_trials"] = int(n_trials)
    results["n_changes_total"] = int(n_changes_total)

    labels = {
        "osm": "OSM:",
        "satellite": "Satellite:",
        "user": "User:",
        "combined": "Combined:",
    }
    for ch in CHANNELS:
        mean_lag = results[ch]["mean_lag_days"]
        detect_pct = results[ch]["detect_90d"] * 100.0
        print(
            f"{labels[ch]:12s} mean_lag={mean_lag:.1f} days  "
            f"detect_90d={detect_pct:.1f}%"
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        json.dump(results, f, indent=2)
    print(f"\nwrote {out_path}")
    return results


def main(argv=None):
    run_experiment(out_path=Path("reports/raw/a6-results.json"))


if __name__ == "__main__":
    main()
