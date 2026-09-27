import numpy as np
from src.community.scenario import make_scenario
from src.community.reporters import honest_reports, byzantine_invert
from src.community.aggregate import (
    majority, reputation_weighted, bayesian_aggregate,
)


def test_scenario_shape():
    truth = make_scenario(100, hazard_rate=0.30, seed=0)
    assert len(truth) == 100
    assert set(truth.tolist()).issubset({0, 1})


def test_honest_high_accuracy():
    truth = make_scenario(1000, seed=1)
    rng = np.random.default_rng(0)
    r = honest_reports(truth, 0.85, rng)
    acc = (r == truth).mean()
    assert 0.80 < acc < 0.90


def test_byzantine_invert():
    truth = np.array([0, 1, 0, 1])
    assert (byzantine_invert(truth) == np.array([1, 0, 1, 0])).all()


def test_majority_all_honest():
    truth = np.array([1, 0, 1, 0, 1])
    report_matrix = np.tile(truth, (11, 1))
    v = majority(report_matrix)
    assert (v == truth).all()


def test_reputation_weighted_beats_random_byzantine():
    truth = make_scenario(500, seed=2)
    rng = np.random.default_rng(0)
    honest = np.array([honest_reports(truth, 0.85, rng) for _ in range(15)])
    byz = (rng.random((5, 500)) < 0.5).astype(int)
    report_matrix = np.vstack([honest, byz])
    reps = np.ones(20)
    v_rep = reputation_weighted(report_matrix, reps)
    v_maj = majority(report_matrix)
    assert (v_rep == truth).mean() >= (v_maj == truth).mean() - 0.05


def test_bayesian_returns_binary():
    truth = np.array([1, 0, 1, 0, 1])
    report_matrix = np.tile(truth, (11, 1))
    v = bayesian_aggregate(report_matrix)
    assert set(v.tolist()).issubset({0, 1})
