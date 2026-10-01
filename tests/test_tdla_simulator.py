from src.tdla.simulator import generate_updates, simulate_tiers, tier_snapshot
from src.tdla.tiers import Tier


def test_generate_updates_count_within_range():
    records = generate_updates(30, 10.0, seed=0)
    assert 240 <= len(records) <= 360


def test_generate_updates_deterministic():
    kwargs = dict(n_days=15, changes_per_day=4.0, seed=7)
    first = generate_updates(**kwargs)
    second = generate_updates(**kwargs)
    assert first == second
    assert len(first) > 0


def test_generate_updates_fields_valid():
    n_days = 20
    records = generate_updates(n_days, changes_per_day=5.0, seed=1)
    assert len(records) > 0
    kinds = {"added", "removed", "modified"}
    for record in records:
        assert record.size_kb > 0
        assert record.segment_km > 0
        assert record.kind in kinds
        assert record.day in range(n_days)


def test_tier_snapshot_empty():
    stats = tier_snapshot([], current_day=0)
    assert set(stats) == set(Tier)
    for tier in Tier:
        assert stats[tier].tier == tier
        assert stats[tier].count == 0
        assert stats[tier].total_size_kb == 0.0
        assert stats[tier].stored_size_kb == 0.0


def test_tier_snapshot_populates_all_tiers():
    records = generate_updates(800, 10.0, seed=0)
    stats = tier_snapshot(records, 799)
    assert stats[Tier.HOT].count > 0
    assert stats[Tier.WARM].count > 0
    assert stats[Tier.COLD].count > 0
    assert stats[Tier.ARCHIVE].count > 0


def test_tier_snapshot_stored_less_than_raw():
    records = generate_updates(800, 10.0, seed=0)
    stats = tier_snapshot(records, 799)
    for tier in Tier:
        assert stats[tier].stored_size_kb <= stats[tier].total_size_kb


def test_simulate_tiers_deterministic():
    kwargs = dict(
        n_days=40,
        changes_per_day=5.0,
        snapshot_days=[7, 39],
        seed=0,
    )
    first = simulate_tiers(**kwargs)
    second = simulate_tiers(**kwargs)
    assert first == second
    assert first["final_day"] == 39
    assert set(first["snapshots"]) == {7, 39}
    for day in (7, 39):
        snap = first["snapshots"][day]
        assert set(snap) == {"hot", "warm", "cold", "archive"}
        for stats in snap.values():
            assert set(stats) == {"count", "total_size_kb", "stored_size_kb"}
            assert isinstance(stats["count"], int)
            assert isinstance(stats["total_size_kb"], float)
            assert isinstance(stats["stored_size_kb"], float)
