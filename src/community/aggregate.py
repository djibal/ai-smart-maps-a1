"""Aggregation rules for community reports."""
import numpy as np


def majority(report_matrix):
    return (report_matrix.mean(axis=0) > 0.5).astype(int)


def supermajority(report_matrix, threshold=2.0 / 3.0):
    return (report_matrix.mean(axis=0) >= threshold).astype(int)


def reputation_weighted(report_matrix, reputations, n_rounds=3):
    reps = reputations.astype(float).copy()
    n_locations = report_matrix.shape[1]
    consensus = np.zeros(n_locations, dtype=int)
    for _ in range(n_rounds):
        weights = reps[:, None]
        weighted = (report_matrix * weights).sum(axis=0) / max(reps.sum(), 1e-9)
        consensus = (weighted > 0.5).astype(int)
        agree = (report_matrix == consensus[None, :]).mean(axis=1)
        reps = reps * (0.5 + agree)
        reps = np.maximum(reps, 1e-3)
        reps = reps / reps.sum() * len(reps)
    return consensus


def bayesian_aggregate(report_matrix, prior=0.30):
    p_honest = 0.85
    lr_true = p_honest / (1 - p_honest)
    lr_false = (1 - p_honest) / p_honest
    prior_logodds = np.log(prior / (1 - prior))
    logodds = np.full(report_matrix.shape[1], prior_logodds)
    for r in report_matrix:
        logodds = logodds + np.where(r == 1, np.log(lr_true), np.log(lr_false))
    prob = 1.0 / (1.0 + np.exp(-logodds))
    return (prob > 0.5).astype(int)
