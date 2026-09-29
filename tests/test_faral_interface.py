import math

from src.faral.interface import Edge, effective_weight


def test_effective_weight_no_hazard():
    e = Edge(src="a", dst="b", weight=2.0, hazard=0.0, closed=False, source="osm")
    assert effective_weight(e) == 2.0


def test_effective_weight_with_hazard():
    e = Edge(src="a", dst="b", weight=2.0, hazard=0.5, closed=False, source="osm")
    assert effective_weight(e) == 3.5


def test_effective_weight_closed_is_inf():
    e = Edge(src="a", dst="b", weight=2.0, hazard=0.5, closed=True, source="osm")
    assert math.isinf(effective_weight(e))
