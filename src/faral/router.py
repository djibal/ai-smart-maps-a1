"""Dijkstra shortest-path over the UnifiedSpatialGraph interface."""
import heapq
import math

from src.faral.interface import effective_weight


def shortest_path(
    graph, src_id: str, dst_id: str, hazard_penalty: float = 3.0
) -> tuple[list[str], float]:
    """Dijkstra over the UnifiedSpatialGraph interface.
    Returns (path_node_ids, total_cost). Empty path and inf cost if
    unreachable. Uses effective_weight from interface.
    The function MUST NOT import any adapter module. It must not know
    what kind of graph it is routing over."""
    if src_id == dst_id:
        return ([src_id], 0.0)

    best: dict[str, float] = {src_id: 0.0}
    parent: dict[str, str] = {}
    heap: list[tuple[float, str]] = [(0.0, src_id)]

    while heap:
        cost, node_id = heapq.heappop(heap)
        if cost > best.get(node_id, math.inf):
            continue
        if node_id == dst_id:
            break
        for edge in graph.neighbors(node_id):
            if edge.src != node_id:
                continue
            ew = effective_weight(edge, hazard_penalty)
            if math.isinf(ew):
                continue
            new_cost = cost + ew
            if new_cost < best.get(edge.dst, math.inf):
                best[edge.dst] = new_cost
                parent[edge.dst] = node_id
                heapq.heappush(heap, (new_cost, edge.dst))

    if dst_id not in best:
        return ([], float("inf"))

    path: list[str] = [dst_id]
    cur = dst_id
    while cur != src_id:
        cur = parent[cur]
        path.append(cur)
    path.reverse()
    return (path, best[dst_id])
