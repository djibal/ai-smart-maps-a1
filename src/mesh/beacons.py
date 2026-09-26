"""Civic beacon placement: fixed super-nodes on a grid."""
import numpy as np


def place_beacons_grid(n_per_km2, area_side_m=1000.0):
    """Place beacons on an approximately square grid, n_per_km2 per km^2."""
    if n_per_km2 <= 0:
        return np.zeros((0, 2))
    grid_dim = int(np.ceil(np.sqrt(n_per_km2)))
    spacing = area_side_m / grid_dim
    xs = np.arange(grid_dim) * spacing + spacing / 2.0
    ys = np.arange(grid_dim) * spacing + spacing / 2.0
    xx, yy = np.meshgrid(xs, ys)
    return np.stack([xx.ravel(), yy.ravel()], axis=1)


def combine_nodes(mobile_positions, beacon_positions):
    """Return (positions, is_beacon)."""
    n_mob = len(mobile_positions)
    n_bcn = len(beacon_positions)
    positions = np.vstack([mobile_positions, beacon_positions])
    is_beacon = np.array([False] * n_mob + [True] * n_bcn)
    return positions, is_beacon
