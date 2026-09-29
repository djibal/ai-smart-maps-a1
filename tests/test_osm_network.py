from src.osm.network import make_network, make_changes, KINDS


def test_make_network_shape():
    n_km = 50
    segments = make_network(n_km, seed=0)
    assert len(segments) == n_km
    assert {s.id for s in segments} == set(range(n_km))
    total = sum(s.length_km for s in segments)
    assert abs(total - n_km) < 1e-9
    assert all(s.length_km > 0 for s in segments)


def test_make_changes_rate_is_reasonable():
    n_km = 1000
    rate = 0.1
    horizon = 12
    segments = make_network(n_km, seed=1)
    total_km = sum(s.length_km for s in segments)
    expected = total_km * rate * horizon
    changes = make_changes(segments, rate, horizon, seed=2)
    assert 0.5 * expected <= len(changes) <= 1.5 * expected
    ids = {s.id for s in segments}
    assert all(c.segment_id in ids for c in changes)
    assert all(1 <= c.month <= horizon for c in changes)
    assert all(c.kind in KINDS for c in changes)


def test_make_changes_deterministic():
    segments_a = make_network(100, seed=7)
    segments_b = make_network(100, seed=7)
    assert segments_a == segments_b
    changes_a = make_changes(segments_a, 0.05, 6, seed=11)
    changes_b = make_changes(segments_b, 0.05, 6, seed=11)
    assert changes_a == changes_b
