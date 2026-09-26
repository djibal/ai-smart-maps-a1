import numpy as np
from src.mesh.beacons import place_beacons_grid, combine_nodes


def test_beacon_grid_shape():
    b = place_beacons_grid(20)
    assert b.shape[1] == 2
    assert len(b) >= 20  # ceil(sqrt(20))^2 = 25


def test_beacon_grid_density():
    b = place_beacons_grid(100)
    assert len(b) == 100  # 10x10 grid


def test_beacon_positions_inside_area():
    b = place_beacons_grid(25, area_side_m=1000.0)
    assert b[:, 0].min() >= 0 and b[:, 0].max() <= 1000
    assert b[:, 1].min() >= 0 and b[:, 1].max() <= 1000


def test_combine_nodes():
    mob = np.array([[1.0, 1.0], [2.0, 2.0]])
    bcn = np.array([[10.0, 10.0]])
    pos, is_b = combine_nodes(mob, bcn)
    assert pos.shape == (3, 2)
    assert is_b.tolist() == [False, False, True]
