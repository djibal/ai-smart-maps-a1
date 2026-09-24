"""Graph generator for A1 route scoring scenarios."""
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
    routes: list  # list of list-of-node-ids
    optimal_index: int = -1


def make_scenario(seed: int, nodes: int = 20, routes: int = 5) -> Scenario:
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


def route_cost(scenario: Scenario, route: list) -> float:
    """Sum edge weights along route; if edge missing, penalty."""
    total = 0.0
    for a, b in zip(route, route[1:]):
        found = None
        for e in scenario.edges:
            if {e.src, e.dst} == {a, b}:
                found = e
                break
        if found is None:
            total += 50.0  # missing edge penalty
        else:
            total += found.weight + found.hazard * 3.0
    return total
