"""Real-time hazard and closure overlay on a base spatial graph."""
from src.faral.interface import Edge, Node


class RealTimeAdapter:
    """Wraps another adapter and overlays hazard/closure updates."""

    def __init__(
        self,
        base,
        hazard_updates: dict[tuple[str, str], float] | None = None,
        closures: set[tuple[str, str]] | None = None,
    ):
        self._base = base
        self._hazard_updates = hazard_updates or {}
        self._closures = closures or set()

    def _overlay(self, e: Edge) -> Edge:
        key = (e.src, e.dst)
        if key in self._closures:
            return Edge(
                src=e.src,
                dst=e.dst,
                weight=e.weight,
                hazard=self._hazard_updates.get(key, e.hazard),
                closed=True,
                source=e.source,
            )
        if key in self._hazard_updates:
            return Edge(
                src=e.src,
                dst=e.dst,
                weight=e.weight,
                hazard=self._hazard_updates[key],
                closed=e.closed,
                source=e.source,
            )
        return e

    def nodes(self) -> list[Node]:
        return self._base.nodes()

    def edges(self) -> list[Edge]:
        return [self._overlay(e) for e in self._base.edges()]

    def neighbors(self, node_id: str) -> list[Edge]:
        return [self._overlay(e) for e in self._base.neighbors(node_id)]
