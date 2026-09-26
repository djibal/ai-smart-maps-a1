import numpy as np


def place_devices(n, area_side_m=1000.0, seed=0):
    rng = np.random.default_rng(seed)
    return rng.uniform(0, area_side_m, size=(n, 2))


def build_adjacency(positions, radius, area_side_m=1000.0):
    diff = positions[:, None, :] - positions[None, :, :]
    diff -= np.round(diff / area_side_m) * area_side_m
    dist2 = (diff ** 2).sum(axis=-1)
    mask = dist2 <= radius ** 2
    np.fill_diagonal(mask, False)
    return [np.where(mask[i])[0] for i in range(len(positions))]


def nodes_within(positions, center_idx, radius, area_side_m=1000.0):
    diff = positions - positions[center_idx]
    diff -= np.round(diff / area_side_m) * area_side_m
    dist = np.sqrt((diff ** 2).sum(axis=-1))
    return np.where(dist <= radius)[0]


def largest_component_size(adj):
    n = len(adj)
    seen = np.zeros(n, dtype=bool)
    best = 0
    for start in range(n):
        if seen[start]:
            continue
        stack = [start]
        seen[start] = True
        size = 0
        while stack:
            u = stack.pop()
            size += 1
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        best = max(best, size)
    return best
