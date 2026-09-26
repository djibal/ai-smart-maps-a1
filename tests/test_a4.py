import numpy as np
from src.mesh.geometry import place_devices, build_adjacency, largest_component_size
from src.mesh.duty import expected_scan_latency_ms, battery_pct_per_day


def test_place_devices_shape():
    p = place_devices(100, seed=0)
    assert p.shape == (100, 2)
    assert p.min() >= 0 and p.max() <= 1000


def test_adjacency_under_radius():
    p = np.array([[0.0, 0.0], [10.0, 0.0], [100.0, 0.0]])
    adj = build_adjacency(p, radius=20.0)
    assert 1 in adj[0]
    assert 0 in adj[1]
    assert 2 not in adj[0]


def test_scan_latency_decreases_with_duty():
    assert expected_scan_latency_ms(0.50) < expected_scan_latency_ms(0.05)


def test_battery_under_budget_at_5pct():
    assert battery_pct_per_day(0.05) < 3.0


def test_largest_component_small_graph():
    adj = [[1], [0, 2], [1], []]
    assert largest_component_size(adj) == 3
