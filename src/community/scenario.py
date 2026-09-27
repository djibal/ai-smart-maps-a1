"""Generate hazard scenarios: locations with ground-truth hazard state."""
import numpy as np


def make_scenario(n_locations, hazard_rate=0.30, seed=0):
    rng = np.random.default_rng(seed)
    truth = (rng.random(n_locations) < hazard_rate).astype(int)
    return truth
