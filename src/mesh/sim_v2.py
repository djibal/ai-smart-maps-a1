"""A4-v2 simulation: heterogeneous mesh with civic beacons."""
import heapq
import numpy as np

from src.mesh.geometry import nodes_within
from src.mesh.duty import sample_receive_delay_ms


def _build_adjacency_het(positions, ranges, area_side_m=1000.0):
    """Bidirectional edge if dist(a,b) <= min(range_a, range_b)."""
    n = len(positions)
    diff = positions[:, None, :] - positions[None, :, :]
    diff -= np.round(diff / area_side_m) * area_side_m
    dist = np.sqrt((diff ** 2).sum(axis=-1))
    min_range = np.minimum(ranges[:, None], ranges[None, :])
    mask = dist <= min_range
    np.fill_diagonal(mask, False)
    return [np.where(mask[i])[0] for i in range(n)]


def _dijkstra(adj, source, edge_weights_at_receiver):
    n = len(adj)
    arrival = np.full(n, np.inf)
    arrival[source] = 0.0
    pq = [(0.0, source)]
    done = np.zeros(n, dtype=bool)
    while pq:
        t, u = heapq.heappop(pq)
        if done[u]:
            continue
        done[u] = True
        for v in adj[u]:
            if done[v]:
                continue
            nt = t + edge_weights_at_receiver[v]
            if nt < arrival[v]:
                arrival[v] = nt
                heapq.heappush(pq, (nt, v))
    return arrival


def simulate_once_het(positions, ranges, duties, is_beacon,
                      cycle_ms, target_radius_m, source_idx,
                      tx_ms=1.0, backoff_ms=2.0, rng=None):
    if rng is None:
        rng = np.random.default_rng(0)
    n = len(positions)
    adj = _build_adjacency_het(positions, ranges)
    target_nodes = nodes_within(positions, source_idx, target_radius_m)

    # Per-node receive delay: mobile duty-cycled, beacon always-on.
    recv_delay = np.zeros(n)
    mobile = ~is_beacon
    if mobile.any():
        recv_delay[mobile] = sample_receive_delay_ms(
            duties[mobile][0], cycle_ms, rng, int(mobile.sum())
        )
    edge_w = tx_ms + backoff_ms + recv_delay
    arrival = _dijkstra(adj, source_idx, edge_w)
    return arrival, target_nodes


def coverage_time(arrival, target_nodes, coverage_frac=0.90):
    times = np.sort(arrival[target_nodes])
    times = times[np.isfinite(times)]
    if len(times) == 0:
        return float("inf")
    k = max(1, int(np.ceil(coverage_frac * len(target_nodes))))
    if k > len(times):
        return float("inf")
    return float(times[k - 1])


def run_trials_v2(n_mobile, mobile_radius, mobile_duty,
                  n_beacons, beacon_radius,
                  cycle_ms=100.0, target_radius_m=200.0,
                  n_trials=30, area_side_m=1000.0, seed=0):
    from src.mesh.beacons import place_beacons_grid

    times = []
    for i in range(n_trials):
        rng = np.random.default_rng(seed + i)
        mobile_pos = rng.uniform(0, area_side_m, size=(n_mobile, 2))
        beacon_pos = place_beacons_grid(n_beacons, area_side_m)

        n_bcn = len(beacon_pos)
        if n_bcn > 0:
            positions = np.vstack([mobile_pos, beacon_pos])
            is_beacon = np.array([False] * n_mobile + [True] * n_bcn)
            ranges = np.array([mobile_radius] * n_mobile + [beacon_radius] * n_bcn)
            duties = np.array([mobile_duty] * n_mobile + [1.0] * n_bcn)
        else:
            positions = mobile_pos
            is_beacon = np.array([False] * n_mobile)
            ranges = np.array([mobile_radius] * n_mobile)
            duties = np.array([mobile_duty] * n_mobile)

        # Source is a random mobile device
        source_idx = int(rng.integers(0, n_mobile))

        arrival, target_nodes = simulate_once_het(
            positions, ranges, duties, is_beacon,
            cycle_ms, target_radius_m, source_idx, rng=rng,
        )
        times.append(coverage_time(arrival, target_nodes, coverage_frac=0.90))

    times = np.asarray(times)
    finite = times[np.isfinite(times)]
    return {
        "n_trials": n_trials,
        "n_unreachable": int(np.sum(~np.isfinite(times))),
        "p50_ms": float(np.percentile(finite, 50)) if len(finite) else float("inf"),
        "p95_ms": float(np.percentile(finite, 95)) if len(finite) else float("inf"),
        "max_ms": float(finite.max()) if len(finite) else float("inf"),
    }
