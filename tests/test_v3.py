from src.graph_v3 import make_scenario, route_features, route_cost, oracle_pick


def test_features_shape():
    s = make_scenario(0)
    f = route_features(s, s.routes[0])
    assert len(f) == 4
    assert all(isinstance(x, (int, float)) for x in f)


def test_oracle_returns_valid_index():
    s = make_scenario(1)
    for variant in ["linear", "quadratic", "threshold"]:
        idx = oracle_pick(s, variant)
        assert idx in (0, 1)


def test_cost_is_deterministic():
    s = make_scenario(2)
    for variant in ["linear", "quadratic", "threshold"]:
        assert route_cost(s, s.routes[0], variant) == route_cost(s, s.routes[0], variant)
