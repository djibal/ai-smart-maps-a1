from src.faral.adapters.osm import OSMAdapter


def test_adapter_returns_nodes_and_edges():
    n_nodes = 50
    adapter = OSMAdapter(n_nodes=n_nodes, seed=0)
    nodes = adapter.nodes()
    edges = adapter.edges()
    assert len(nodes) == n_nodes
    assert len(edges) > 0
    ids = {n.id for n in nodes}
    for e in edges:
        assert e.src in ids
        assert e.dst in ids
        assert e.weight > 0
        assert e.hazard == 0.0
        assert e.closed is False


def test_adapter_deterministic():
    a = OSMAdapter(n_nodes=50, seed=1)
    b = OSMAdapter(n_nodes=50, seed=1)
    assert a.nodes() == b.nodes()
    assert a.edges() == b.edges()


def test_neighbors_matches_edges():
    adapter = OSMAdapter(n_nodes=50, seed=0)
    edges = adapter.edges()
    for node in adapter.nodes():
        outgoing = [e for e in edges if e.src == node.id]
        assert adapter.neighbors(node.id) == outgoing


def test_all_edge_sources_are_osm():
    adapter = OSMAdapter(n_nodes=50, seed=0)
    assert all(e.source == "osm" for e in adapter.edges())
