"""Aggregation rules: FedAvg, Krum, TrimmedMean."""
import torch


def _stack(deltas):
    keys = deltas[0].keys()
    return {k: torch.stack([d[k] for d in deltas]) for k in keys}


def fedavg(deltas):
    stacked = _stack(deltas)
    return {k: v.mean(dim=0) for k, v in stacked.items()}


def trimmed_mean(deltas, trim=0.2):
    stacked = _stack(deltas)
    n = len(deltas)
    k = max(1, int(n * trim))
    out = {}
    for key, v in stacked.items():
        sorted_v, _ = torch.sort(v, dim=0)
        out[key] = sorted_v[k:n - k].mean(dim=0)
    return out


def _flatten(delta):
    return torch.cat([v.flatten() for v in delta.values()])


def krum(deltas, f=1, m=None):
    n = len(deltas)
    if m is None:
        m = 1
    if n < 2 * f + 3:
        return fedavg(deltas)
    flat = torch.stack([_flatten(d) for d in deltas])
    dists = torch.cdist(flat, flat) ** 2
    n_neighbors = n - f - 2
    scores = []
    for i in range(n):
        d_i = dists[i].clone()
        d_i[i] = float("inf")
        sorted_d, _ = torch.sort(d_i)
        scores.append(sorted_d[:n_neighbors].sum().item())
    scores = torch.tensor(scores)
    selected = torch.argsort(scores)[:m]
    return fedavg([deltas[i.item()] for i in selected])
