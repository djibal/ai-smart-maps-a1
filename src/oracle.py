"""Oracle: hand-coded optimal route scorer."""
from src.graph import Scenario, route_cost


def score(scenario: Scenario) -> int:
    costs = [route_cost(scenario, r) for r in scenario.routes]
    return int(min(range(len(costs)), key=lambda i: costs[i]))
