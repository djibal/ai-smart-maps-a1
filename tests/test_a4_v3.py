import numpy as np
from src.mesh.sim_v3 import run_trials_v3


def test_run_trials_returns_expected_keys():
    r = run_trials_v3(
        n_mobile=100, mobile_radius=20, mobile_duty=0.1,
        n_beacons=20, beacon_radius=100,
        n_trials=3, seed=0,
    )
    for k in ["n_trials", "n_unreachable", "p50_ms", "p95_ms", "max_ms"]:
        assert k in r


def test_attenuation_does_not_help():
    """Higher attenuation should not improve latency or reachability."""
    r_full = run_trials_v3(
        n_mobile=200, mobile_radius=20, mobile_duty=0.1,
        n_beacons=20, beacon_radius=100, n_trials=5,
        seed=1, atten=1.0,
    )
    r_low = run_trials_v3(
        n_mobile=200, mobile_radius=20, mobile_duty=0.1,
        n_beacons=20, beacon_radius=100, n_trials=5,
        seed=1, atten=0.5,
    )
    assert r_low["n_unreachable"] >= r_full["n_unreachable"]
