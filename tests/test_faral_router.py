import math
from pathlib import Path

import pytest

from src.faral.adapters.commercial import CommercialAdapter
from src.faral.adapters.osm import OSMAdapter
from src.faral.adapters.realtime import RealTimeAdapter
from src.faral.interface import Edge, Node
from src.faral.router import shortest_path


def test_router_finds_path_on_osm():
    adapter = OSMAdapter(n_nodes=50, seed=0)
    nodes = adapter.nodes()
    src = nodes[0].id
    dst = nodes[-1].id
    path, cost = shortest_path(adapter, src, dst)
    assert path
    assert path[0] == src
    assert path[-1] == dst
    assert math.isfinite(cost)
    if src != dst:
        assert cost > 0


def test_router_returns_empty_on_unreachable():
    class DisconnectedGraph:
        def nodes(self) -> list[Node]:
            return [Node(id="a", lat=0.0, lon=0.0), Node(id="b", lat=1.0, lon=1.0)]

        def edges(self) -> list[Edge]:
            return []

        def neighbors(self, node_id: str) -> list[Edge]:
            return []

    graph = DisconnectedGraph()
    path, cost = shortest_path(graph, "a", "b")
    assert path == []
    assert math.isinf(cost)


def test_router_same_interface_for_all_adapters():
    n_nodes = 50
    seed = 0
    osm = OSMAdapter(n_nodes=n_nodes, seed=seed)
    commercial = CommercialAdapter(n_nodes=n_nodes, seed=seed)
    realtime = RealTimeAdapter(base=osm, hazard_updates={}, closures=set())

    nodes = osm.nodes()
    src = nodes[0].id
    dst = nodes[-1].id

    osm_path, osm_cost = shortest_path(osm, src, dst)
    rt_path, rt_cost = shortest_path(realtime, src, dst)
    com_path, com_cost = shortest_path(commercial, src, dst)

    assert osm_path and math.isfinite(osm_cost)
    assert rt_path and math.isfinite(rt_cost)
    assert com_path and math.isfinite(com_cost)

    assert osm_path == rt_path
    assert osm_cost == pytest.approx(rt_cost)

    assert com_path[0] == src
    assert com_path[-1] == dst
    assert math.isfinite(com_cost)


def test_router_zero_change_proof():
    class LineGraph:
        def nodes(self) -> list[Node]:
            return [
                Node(id="A", lat=0.0, lon=0.0),
                Node(id="B", lat=0.0, lon=1.0),
                Node(id="C", lat=0.0, lon=2.0),
            ]

        def edges(self) -> list[Edge]:
            return [
                Edge(src="A", dst="B", weight=1.5, hazard=0.0, closed=False, source="test"),
                Edge(src="B", dst="C", weight=2.5, hazard=0.0, closed=False, source="test"),
            ]

        def neighbors(self, node_id: str) -> list[Edge]:
            return [e for e in self.edges() if e.src == node_id]

    graph = LineGraph()
    path, cost = shortest_path(graph, "A", "C")
    assert path == ["A", "B", "C"]
    assert cost == pytest.approx(1.5 + 2.5)

    text = Path("src/faral/router.py").read_text()
    import_lines = [
        ln for ln in text.splitlines() if ln.startswith("import ") or ln.startswith("from ")
    ]
    blob = "\n".join(import_lines)
    assert "adapters" not in blob
    assert "isinstance" not in text


def test_router_respects_closure():
    osm = OSMAdapter(n_nodes=50, seed=0)
    nodes = osm.nodes()
    src = nodes[0].id
    dst = nodes[-1].id

    old_path, old_cost = shortest_path(osm, src, dst)
    assert len(old_path) >= 2
    closed_hop = (old_path[0], old_path[1])
    rt = RealTimeAdapter(base=osm, closures={closed_hop})
    new_path, new_cost = shortest_path(rt, src, dst)

    assert new_path != old_path or new_cost > old_cost + 1e-12


def test_router_respects_hazard_penalty():
    class TwoPathGraph:
        def nodes(self) -> list[Node]:
            return [
                Node(id="A", lat=0.0, lon=0.0),
                Node(id="B", lat=0.0, lon=1.0),
                Node(id="C", lat=0.0, lon=2.0),
            ]

        def edges(self) -> list[Edge]:
            return [
                Edge(src="A", dst="B", weight=1.0, hazard=1.0, closed=False, source="test"),
                Edge(src="B", dst="C", weight=1.0, hazard=1.0, closed=False, source="test"),
                Edge(src="A", dst="C", weight=5.0, hazard=0.0, closed=False, source="test"),
            ]

        def neighbors(self, node_id: str) -> list[Edge]:
            return [e for e in self.edges() if e.src == node_id]

    graph = TwoPathGraph()
    path_0, cost_0 = shortest_path(graph, "A", "C", hazard_penalty=0.0)
    path_10, cost_10 = shortest_path(graph, "A", "C", hazard_penalty=10.0)

    assert math.isfinite(cost_0)
    assert math.isfinite(cost_10)
    assert cost_10 >= cost_0
    assert cost_10 > cost_0 or path_10 != path_0
