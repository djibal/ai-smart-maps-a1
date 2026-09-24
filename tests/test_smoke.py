from src.graph import make_scenario, route_cost
from src.oracle import score


def test_scenario_has_edges():
    s = make_scenario(0)
    assert len(s.edges) > 0
    assert len(s.routes) == 5


def test_oracle_returns_valid_index():
    s = make_scenario(1)
    idx = score(s)
    assert 0 <= idx < len(s.routes)


def test_oracle_is_deterministic():
    s = make_scenario(2)
    assert score(s) == score(s)
