"""Honest and Byzantine reporters."""
import numpy as np


def honest_reports(truth, accuracy, rng):
    n = len(truth)
    correct = rng.random(n) < accuracy
    return np.where(correct, truth, 1 - truth)


def byzantine_random(truth, rng):
    return (rng.random(len(truth)) < 0.5).astype(int)


def byzantine_invert(truth, rng=None):
    return (1 - truth).astype(int)


def byzantine_coordinated(truth, rng=None):
    """All Byzantine reporters report 'hazard present' regardless of truth."""
    return np.ones(len(truth), dtype=int)


BYZANTINE = {
    "random": byzantine_random,
    "invert": byzantine_invert,
    "coordinated": byzantine_coordinated,
}
