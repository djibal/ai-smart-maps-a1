import heapq
import numpy as np

from src.mesh.geometry import build_adjacency, nodes_within
from src.mesh.duty import sample_receive_delay_ms


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


def simulate_once(positions, radius, duty_cycle, cycle_ms,
                  target_radius_m, source_idx,
                  tx_ms=1.0, backoff_ms=2.0, rng=None):
    if rng is None:
        rng = np.random.default_rng(0)
    adj = build_adjacency(positions, radius)
    target_nodes = nodes_within(positions, source_idx, target_radius_m)
    recv_delay = sample_receive_delay_ms(duty_cycle, cycle_ms, rng, len(positions))
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


def run_trials(n_devices, radius, duty_cycle, cycle_ms,
               target_radius_m=200.0,
               n_trials=30, area_side_m=1000.0, seed=0):
    times = []
    for i in range(n_trials):
        rng = np.random.default_rng(seed + i)
        positions = rng.uniform(0, area_side_m, size=(n_devices, 2))
        source_idx = rng.integers(0, n_devices)
        arrival, target_nodes = simulate_once(
            positions, radius, duty_cycle, cycle_ms,
            target_radius_m, int(source_idx), rng=rng,
        )
        t = coverage_time(arrival, target_nodes, coverage_frac=0.90)
        times.append(t)
    times = np.asarray(times)
    finite = times[np.isfinite(times)]
    return {
        "n_trials": n_trials,
        "n_unreachable": int(np.sum(~np.isfinite(times))),
        "p50_ms": float(np.percentile(finite, 50)) if len(finite) else float("inf"),
        "p95_ms": float(np.percentile(finite, 95)) if len(finite) else float("inf"),
        "max_ms": float(finite.max()) if len(finite) else float("inf"),
    }
