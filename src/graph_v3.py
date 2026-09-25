"""Graph generator with multiple cost-function variants for A1-v3."""
import random
from dataclasses import dataclass


@dataclass
class Edge:
    src: int
    dst: int
    weight: float
    hazard: float


@dataclass
class Scenario:
    id: int
    nodes: int
    edges: list
    routes: list  # exactly 2


def make_scenario(seed: int, nodes: int = 20, routes: int = 2) -> Scenario:
    rng = random.Random(seed)
    edges = []
    for a in range(nodes):
        for b in range(a + 1, nodes):
            if rng.random() < 0.15:
                edges.append(Edge(a, b, rng.uniform(1, 10), rng.uniform(0, 1)))
    route_list = []
    for _ in range(routes):
        length = rng.randint(2, 5)
        route = [rng.randint(0, nodes - 1) for _ in range(length)]
        route_list.append(route)
    return Scenario(id=seed, nodes=nodes, edges=edges, routes=route_list)


def _route_stats(scenario, route):
    total_w = 0.0
    total_h = 0.0
    max_h = 0.0
    missing = 0
    for a, b in zip(route, route[1:]):
        found = None
        for e in scenario.edges:
            if {e.src, e.dst} == {a, b}:
                found = e
                break
        if found is None:
            missing += 1
        else:
            total_w += found.weight
            total_h += found.hazard
            max_h = max(max_h, found.hazard)
    return {
        "num_edges": len(route) - 1,
        "sum_w": total_w,
        "sum_h": total_h,
        "max_h": max_h,
        "missing": missing,
    }


def route_cost(scenario, route, variant: str = "linear") -> float:
    s = _route_stats(scenario, route)
    base = s["sum_w"] + 3.0 * s["sum_h"] + 50.0 * s["missing"]
    if variant == "linear":
        return base
    if variant == "quadratic":
        return base + 0.1 * s["sum_w"] ** 2
    if variant == "threshold":
        return base + 100.0 * max(0.0, s["max_h"] - 0.5)
    raise ValueError(f"unknown variant {variant}")


def oracle_pick(scenario, variant: str) -> int:
    costs = [route_cost(scenario, r, variant) for r in scenario.routes]
    return int(min(range(len(costs)), key=lambda i: costs[i]))


def route_features(scenario, route):
    s = _route_stats(scenario, route)
    return [s["num_edges"], s["sum_w"], s["sum_h"], s["missing"]]
