import json

import pytest

from src.tdla.tiers import TIER_LATENCY_P95_MS, Tier
from src.tdla_run import (
    aggregate_cities,
    check_latency_slos,
    run_experiment,
    run_one_city,
)


def _tier_stats(count: int, stored_size_kb: float) -> dict:
    return {
        "count": count,
        "total_size_kb": stored_size_kb * 2.0,
        "stored_size_kb": stored_size_kb,
    }


def _city_result(
    day: int,
    hot: tuple[int, float],
    warm: tuple[int, float],
    cold: tuple[int, float],
    archive: tuple[int, float],
) -> dict:
    return {
        "snapshots": {
            day: {
                "hot": _tier_stats(*hot),
                "warm": _tier_stats(*warm),
                "cold": _tier_stats(*cold),
                "archive": _tier_stats(*archive),
            }
        },
        "final_day": day,
        "total_updates": hot[0] + warm[0] + cold[0] + archive[0],
    }


def test_run_one_city_returns_snapshots():
    result = run_one_city(seed=0, sim_days=100, changes_per_day=10)
    assert isinstance(result, dict)
    assert "snapshots" in result
    assert result["snapshots"]


def test_aggregate_cities_sums_correctly():
    first = _city_result(
        7,
        hot=(4, 10.5),
        warm=(2, 20.0),
        cold=(1, 3.0),
        archive=(0, 0.0),
    )
    second = _city_result(
        7,
        hot=(3, 1.25),
        warm=(1, 5.5),
        cold=(2, 4.5),
        archive=(1, 0.25),
    )
    aggregate = aggregate_cities([first, second])
    assert aggregate["n_cities"] == 2
    hot = aggregate["snapshots"][7]["hot"]
    assert hot["total_stored_size_kb"] == pytest.approx(10.5 + 1.25)
    assert hot["count"] == 4 + 3
    warm = aggregate["snapshots"][7]["warm"]
    assert warm["total_stored_size_kb"] == pytest.approx(20.0 + 5.5)
    assert warm["count"] == 2 + 1


def test_check_latency_slos_all_tiers_present():
    result = check_latency_slos(seed=0)
    assert set(result) == {tier.value for tier in Tier}
    for tier in Tier:
        entry = result[tier.value]
        assert set(entry) >= {"p95_ms", "slo_ms", "pass"}
        assert entry["slo_ms"] == TIER_LATENCY_P95_MS[tier]
        assert type(entry["pass"]) is bool


def test_run_experiment_writes_json(tmp_path):
    output_path = tmp_path / "tdla-results.json"
    result = run_experiment(output_path, n_cities=2, sim_days=30)
    assert output_path.exists()
    data = json.loads(output_path.read_text())
    assert set(data) >= {"aggregate", "latency", "config"}
    assert data["config"]["n_cities"] == 2
    assert data["config"]["sim_days"] == 30
    assert data["aggregate"]["n_cities"] == 2
    assert result["config"]["n_cities"] == 2
    assert result["aggregate"]["n_cities"] == 2
