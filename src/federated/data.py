"""Non-IID data partitioning for federated simulation."""
import torch
from src.graph_v3 import make_scenario, route_cost, route_features

VARIANTS = ["linear", "quadratic", "threshold"]


def _pair(seed, variant):
    s = make_scenario(seed)
    c0 = route_cost(s, s.routes[0], variant)
    c1 = route_cost(s, s.routes[1], variant)
    f0 = route_features(s, s.routes[0])
    f1 = route_features(s, s.routes[1])
    cheaper, expensive = (f0, f1) if c0 <= c1 else (f1, f0)
    return (torch.tensor(cheaper, dtype=torch.float32),
            torch.tensor(expensive, dtype=torch.float32))


def partition(n_devices, per_device, base_seed=500_000, variant_skew=0.8):
    shards = []
    for i in range(n_devices):
        primary = i % 3
        samples = []
        for vidx, variant in enumerate(VARIANTS):
            w = variant_skew if vidx == primary else (1 - variant_skew) / 2
            n = int(per_device * w)
            for j in range(n):
                seed = base_seed + i * 100_000 + vidx * 10_000 + j
                samples.append(_pair(seed, variant))
        shards.append(samples)
    return shards


def global_test_set(n, base_seed=4_000_000):
    out = []
    for i in range(n):
        variant = VARIANTS[i % 3]
        seed = base_seed + i
        s = make_scenario(seed)
        c0 = route_cost(s, s.routes[0], variant)
        c1 = route_cost(s, s.routes[1], variant)
        f0 = route_features(s, s.routes[0])
        f1 = route_features(s, s.routes[1])
        truth = 0 if c0 <= c1 else 1
        out.append((f0, f1, truth))
    return out
