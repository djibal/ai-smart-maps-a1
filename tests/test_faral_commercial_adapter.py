import math

from src.faral.adapters.commercial import CommercialAdapter


def test_commercial_returns_nodes_and_edges():
    n_nodes = 50
    adapter = CommercialAdapter(n_nodes=n_nodes, seed=0)
    nodes = adapter.nodes()
    edges = adapter.edges()
    assert len(nodes) == n_nodes
    assert len(edges) > 0
    ids = {n.id for n in nodes}
    for e in edges:
        assert e.src in ids
        assert e.dst in ids
        assert e.weight > 0
        assert e.hazard == 0.0
        assert e.closed is False


def test_commercial_uses_travel_time_as_weight():
    adapter = CommercialAdapter(n_nodes=50, seed=0)
    nodes = {n.id: n for n in adapter.nodes()}
    speeds_seen: set[float] = set()
    mismatched_distance = 0
    for e in adapter.edges():
        src = nodes[e.src]
        dst = nodes[e.dst]
        distance = math.hypot(dst.lat - src.lat, dst.lon - src.lon)
        assert distance > 0
        assert not math.isclose(e.weight, distance, rel_tol=0, abs_tol=1e-12)
        mismatched_distance += 1
        candidates = (distance / 60.0, distance / 40.0, distance / 25.0)
        assert any(math.isclose(e.weight, c, rel_tol=0, abs_tol=1e-9) for c in candidates)
        for speed in (60.0, 40.0, 25.0):
            if math.isclose(e.weight, distance / speed, rel_tol=0, abs_tol=1e-9):
                speeds_seen.add(speed)
                break
    assert mismatched_distance >= 1
    assert len(speeds_seen) > 1


def test_commercial_deterministic():
    a = CommercialAdapter(n_nodes=50, seed=1)
    b = CommercialAdapter(n_nodes=50, seed=1)
    assert a.nodes() == b.nodes()
    assert a.edges() == b.edges()


def test_all_edge_sources_are_commercial():
    adapter = CommercialAdapter(n_nodes=50, seed=0)
    assert all(e.source == "commercial" for e in adapter.edges())
