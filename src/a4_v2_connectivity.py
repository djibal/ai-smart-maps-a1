"""A4-v2 connectivity check: largest component per config."""
import numpy as np

from src.mesh.geometry import largest_component_size
from src.mesh.beacons import place_beacons_grid
from src.mesh.sim_v2 import _build_adjacency_het

CONFIGS = [
    ("no_beacons_baseline",    1000, 20, 0,  100),
    ("10_beacons_20m",         1000, 20, 10, 100),
    ("20_beacons_20m",         1000, 20, 20, 100),
    ("50_beacons_20m",         1000, 20, 50, 100),
    ("20_beacons_30m_mobile",  1000, 30, 20, 100),
    ("100_beacons_20m",        1000, 20, 100, 100),
    ("400_beacons_20m",        1000, 20, 400, 100),
]


def main():
    rng = np.random.default_rng(42)
    for name, n_mob, m_rad, n_bcn, b_rad in CONFIGS:
        mob = rng.uniform(0, 1000, size=(n_mob, 2))
        bcn = place_beacons_grid(n_bcn, 1000.0)
        n_bcn_actual = len(bcn)
        if n_bcn_actual > 0:
            positions = np.vstack([mob, bcn])
            ranges = np.array([m_rad] * n_mob + [b_rad] * n_bcn_actual)
        else:
            positions = mob
            ranges = np.array([m_rad] * n_mob)
        adj = _build_adjacency_het(positions, ranges)
        n = len(positions)
        largest = largest_component_size(adj)
        print(f"{name:28s} n={n:5d} largest_component={largest}/{n} "
              f"({largest/n*100:.1f}%)")


if __name__ == "__main__":
    main()
