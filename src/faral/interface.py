"""Unified spatial graph types and effective-weight helper."""
import math
from dataclasses import dataclass
from typing import Protocol


@dataclass
class Node:
    id: str
    lat: float
    lon: float


@dataclass
class Edge:
    src: str  # node id
    dst: str  # node id
    weight: float  # base travel cost
    hazard: float  # 0..1, higher = more hazardous
    closed: bool  # hard closed flag
    source: str  # which adapter produced this edge


class UnifiedSpatialGraph(Protocol):
    def nodes(self) -> list[Node]: ...
    def edges(self) -> list[Edge]: ...
    def neighbors(self, node_id: str) -> list[Edge]: ...


def effective_weight(e: Edge, hazard_penalty: float = 3.0) -> float:
    """Return weight + hazard_penalty * hazard if not closed, else inf."""
    if e.closed:
        return math.inf
    return e.weight + hazard_penalty * e.hazard
