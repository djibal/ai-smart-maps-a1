"""Synthetic commercial-map shaped graph. Deterministic from seed."""
import math

import numpy as np

from src.faral.interface import Edge, Node

# Fixed k in {2, 4}; connect to 3 nearest neighbors when possible.
_K_NEAREST = 3
# Jitter uses a different stream than OSMAdapter so geometry can differ at equal seed.
_JITTER_SEED_OFFSET = 10_000

_ROAD_CLASSES = ("primary", "secondary", "residential")
_SPEED_KMH = {"primary": 60.0, "secondary": 40.0, "residential": 25.0}


class CommercialAdapter:
    """Synthetic commercial-map shaped graph. Different edge schema
    internally: uses travel_time_minutes and road_class instead of raw
    distance. Exposes the same UnifiedSpatialGraph interface.

    Node layout matches :class:`OSMAdapter` (``ceil(sqrt(n))`` lattice on a
    1 km square, k=3 nearest neighbors, tie-break by destination id) but
    jitter is drawn from ``np.random.default_rng(seed + 10_000)`` so routes
    can differ from OSM at the same ``seed``. Edge ``weight`` is travel
    time in hours (distance km divided by road-class speed).
    """

    def __init__(self, n_nodes: int = 50, seed: int = 0):
        rng = np.random.default_rng(seed + _JITTER_SEED_OFFSET)
        n = max(1, int(n_nodes))
        side = max(1, math.ceil(math.sqrt(n)))
        step = 1.0 / (side - 1) if side > 1 else 0.0
        jitter_amp = 0.2 * step if side > 1 else 0.0

        nodes: list[Node] = []
        for i in range(n):
            row, col = divmod(i, side)
            y = row * step
            x = col * step
            if jitter_amp > 0:
                y = float(np.clip(y + rng.uniform(-jitter_amp, jitter_amp), 0.0, 1.0))
                x = float(np.clip(x + rng.uniform(-jitter_amp, jitter_amp), 0.0, 1.0))
            nodes.append(Node(id=f"n{i}", lat=y, lon=x))

        coords = np.array([[nd.lat, nd.lon] for nd in nodes], dtype=float)
        edges: list[Edge] = []
        seen: set[tuple[str, str]] = set()
        for i, src in enumerate(nodes):
            others = []
            for j, dst in enumerate(nodes):
                if i == j:
                    continue
                d = float(np.linalg.norm(coords[i] - coords[j]))
                others.append((d, dst.id, j))
            others.sort(key=lambda t: (t[0], t[1]))
            k = min(_K_NEAREST, len(others))
            for d, dst_id, _j in others[:k]:
                key = (src.id, dst_id)
                if key in seen or d <= 0:
                    continue
                seen.add(key)
                road_class = _ROAD_CLASSES[int(rng.integers(0, len(_ROAD_CLASSES)))]
                speed_kmh = _SPEED_KMH[road_class]
                travel_time_hours = d / speed_kmh
                edges.append(
                    Edge(
                        src=src.id,
                        dst=dst_id,
                        weight=travel_time_hours,
                        hazard=0.0,
                        closed=False,
                        source="commercial",
                    )
                )

        self._nodes = nodes
        self._edges = edges
        self._by_src: dict[str, list[Edge]] = {}
        for e in edges:
            self._by_src.setdefault(e.src, []).append(e)

    def nodes(self) -> list[Node]:
        return list(self._nodes)

    def edges(self) -> list[Edge]:
        return list(self._edges)

    def neighbors(self, node_id: str) -> list[Edge]:
        return list(self._by_src.get(node_id, []))
