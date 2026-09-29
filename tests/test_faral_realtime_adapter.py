from src.faral.adapters.realtime import RealTimeAdapter
from src.faral.interface import Edge, Node, effective_weight


class _StubBase:
    def __init__(self):
        self._nodes = [
            Node(id="a", lat=0.0, lon=0.0),
            Node(id="b", lat=0.0, lon=0.5),
            Node(id="c", lat=0.5, lon=0.0),
        ]
        self._edges = [
            Edge(
                src="a",
                dst="b",
                weight=0.5,
                hazard=0.0,
                closed=False,
                source="osm",
            ),
            Edge(
                src="a",
                dst="c",
                weight=0.5,
                hazard=0.1,
                closed=False,
                source="osm",
            ),
            Edge(
                src="b",
                dst="c",
                weight=0.7,
                hazard=0.0,
                closed=False,
                source="commercial",
            ),
        ]
        self._by_src: dict[str, list[Edge]] = {}
        for e in self._edges:
            self._by_src.setdefault(e.src, []).append(e)

    def nodes(self) -> list[Node]:
        return list(self._nodes)

    def edges(self) -> list[Edge]:
        return list(self._edges)

    def neighbors(self, node_id: str) -> list[Edge]:
        return list(self._by_src.get(node_id, []))


def test_realtime_passes_through_unchanged_edges():
    base = _StubBase()
    rt = RealTimeAdapter(base, hazard_updates={}, closures=set())
    assert rt.edges() == base.edges()
    for node in base.nodes():
        assert rt.neighbors(node.id) == base.neighbors(node.id)


def test_realtime_applies_hazard_update():
    base = _StubBase()
    key = ("a", "c")
    rt = RealTimeAdapter(base, hazard_updates={key: 0.85}, closures=set())
    edges = { (e.src, e.dst): e for e in rt.edges() }
    assert edges[key].hazard == 0.85
    assert edges[key].closed is False
    assert edges[("a", "b")].hazard == 0.0
    assert edges[("b", "c")].hazard == 0.0


def test_realtime_applies_closure():
    base = _StubBase()
    key = ("a", "b")
    rt = RealTimeAdapter(base, hazard_updates=None, closures={key})
    edges = {(e.src, e.dst): e for e in rt.edges()}
    assert edges[key].closed is True
    assert effective_weight(edges[key]) == float("inf")


def test_realtime_source_unchanged():
    base = _StubBase()
    rt_hazard = RealTimeAdapter(
        base, hazard_updates={("a", "c"): 0.5}, closures=set()
    )
    for e in rt_hazard.edges():
        base_e = next(
            be for be in base.edges() if be.src == e.src and be.dst == e.dst
        )
        assert e.source == base_e.source
        assert e.source != "realtime"

    rt_closed = RealTimeAdapter(base, hazard_updates=None, closures={("b", "c")})
    closed = next(e for e in rt_closed.edges() if e.src == "b" and e.dst == "c")
    assert closed.source == "commercial"
    assert closed.source != "realtime"
