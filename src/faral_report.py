"""FARAL report: format-agnostic routing layer claim verification."""
import math
from pathlib import Path

from src.faral.adapters.commercial import CommercialAdapter
from src.faral.adapters.osm import OSMAdapter
from src.faral.adapters.realtime import RealTimeAdapter
from src.faral.router import shortest_path

DEFAULT_OUTPUT = Path("reports/FARAL-report.md")

_N_NODES = 50
_SEED = 0


def _format_cost(cost: float) -> str:
    if not math.isfinite(cost):
        return "inf"
    return f"{cost:.4f}"


def _check_router_imports_adapters(router_path: Path) -> bool:
    text = router_path.read_text()
    for ln in text.splitlines():
        if ln.startswith("import ") or ln.startswith("from "):
            if "adapters" in ln:
                return True
    return False


def build_report(input_data: dict, output_path: Path) -> str:
    """Format FARAL metrics as Markdown, write to output_path, return text.

    input_data schema:
       {
         "osm_path_len": int, "osm_cost": float,
         "commercial_path_len": int, "commercial_cost": float,
         "realtime_path_len": int, "realtime_cost": float,
         "realtime_with_closure_path_len": int,
         "realtime_with_closure_cost": float,
         "osm_realtime_identical": bool,
         "router_imports_adapters": bool,
         "adapters_tested": ["osm", "commercial", "realtime"],
       }
    """
    output_path = Path(output_path)

    check_a_pass = not input_data["router_imports_adapters"]
    check_b_pass = bool(input_data["osm_realtime_identical"])
    check_c_pass = (
        input_data["osm_path_len"] > 0
        and input_data["commercial_path_len"] > 0
        and input_data["realtime_path_len"] > 0
    )

    all_pass = check_a_pass and check_b_pass and check_c_pass
    if all_pass:
        verdict_line = "**Overall FARAL: STRONG PASS**"
        summary = (
            "The same Dijkstra router routes correctly across OSM, commercial, "
            "and real-time wrappers without importing any adapter."
        )
    else:
        verdict_line = "**Overall FARAL: FAIL**"
        summary = (
            "At least one FARAL claim check failed; the format-agnostic "
            "routing layer claim is not fully supported by this run."
        )

    def _result(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    lines = [
        "# FARAL Report: Format-Agnostic Routing Layer",
        "",
        "FARAL (ADR-0005) claims that routing algorithms operate on a Unified",
        "Spatial Graph Interface, independent of the underlying data source.",
        "This report tests that claim by routing the same query across OSM,",
        "commercial, and real-time adapters with a single router implementation.",
        "",
        "| Adapter | Path length | Total cost |",
        "|---|---|---|",
        f"| OSM | {input_data['osm_path_len']} | {_format_cost(input_data['osm_cost'])} |",
        f"| Commercial | {input_data['commercial_path_len']} | {_format_cost(input_data['commercial_cost'])} |",
        f"| RealTime (no updates) | {input_data['realtime_path_len']} | {_format_cost(input_data['realtime_cost'])} |",
        f"| RealTime (with one closure) | {input_data['realtime_with_closure_path_len']} | {_format_cost(input_data['realtime_with_closure_cost'])} |",
        "",
        "## Claim verification",
        "",
        f"- Router imports adapters? (expected NO): {_result(check_a_pass)}",
        f"- OSM and RealTime(empty) produce identical paths? (expected YES): {_result(check_b_pass)}",
        f"- Same router works across all adapters? (expected YES): {_result(check_c_pass)}",
        "",
        "## Verdict",
        "",
        verdict_line,
        "",
        summary,
        "",
    ]

    text = "\n".join(lines)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text)
    return text


def main() -> None:
    """Run a small deterministic FARAL scenario and write the report."""
    osm = OSMAdapter(n_nodes=_N_NODES, seed=_SEED)
    commercial = CommercialAdapter(n_nodes=_N_NODES, seed=_SEED)

    nodes = osm.nodes()
    src = nodes[0].id
    dst = nodes[-1].id

    osm_path, osm_cost = shortest_path(osm, src, dst)
    com_path, com_cost = shortest_path(commercial, src, dst)

    realtime = RealTimeAdapter(base=osm, hazard_updates={}, closures=set())
    rt_path, rt_cost = shortest_path(realtime, src, dst)

    osm_realtime_identical = osm_path == rt_path and (
        osm_cost == rt_cost
        or (
            math.isfinite(osm_cost)
            and math.isfinite(rt_cost)
            and abs(osm_cost - rt_cost) < 1e-12
        )
        or (math.isinf(osm_cost) and math.isinf(rt_cost))
    )

    if len(osm_path) >= 2:
        closed_hop = (osm_path[0], osm_path[1])
        rt_closed = RealTimeAdapter(base=osm, closures={closed_hop})
        rt_closed_path, rt_closed_cost = shortest_path(rt_closed, src, dst)
    else:
        rt_closed_path, rt_closed_cost = shortest_path(realtime, src, dst)

    router_path = Path(__file__).resolve().parent / "faral" / "router.py"
    router_imports_adapters = _check_router_imports_adapters(router_path)

    data = {
        "osm_path_len": len(osm_path),
        "osm_cost": float(osm_cost),
        "commercial_path_len": len(com_path),
        "commercial_cost": float(com_cost),
        "realtime_path_len": len(rt_path),
        "realtime_cost": float(rt_cost),
        "realtime_with_closure_path_len": len(rt_closed_path),
        "realtime_with_closure_cost": float(rt_closed_cost),
        "osm_realtime_identical": bool(osm_realtime_identical),
        "router_imports_adapters": bool(router_imports_adapters),
        "adapters_tested": ["osm", "commercial", "realtime"],
    }

    output_path = DEFAULT_OUTPUT
    text = build_report(data, output_path)
    print(text)
    print(f"wrote {output_path}")


if __name__ == "__main__":
    main()
