from src.faral_report import build_report


def _synthetic_input(**overrides) -> dict:
    data = {
        "osm_path_len": 5,
        "osm_cost": 1.5,
        "commercial_path_len": 4,
        "commercial_cost": 2.25,
        "realtime_path_len": 5,
        "realtime_cost": 1.5,
        "realtime_with_closure_path_len": 6,
        "realtime_with_closure_cost": 2.0,
        "osm_realtime_identical": True,
        "router_imports_adapters": False,
        "adapters_tested": ["osm", "commercial", "realtime"],
    }
    data.update(overrides)
    return data


def test_build_report_writes_file(tmp_path):
    output_path = tmp_path / "out" / "FARAL-report.md"
    text = build_report(_synthetic_input(), output_path)
    assert output_path.exists()
    assert "**Overall FARAL:" in text
    assert "**Overall FARAL:" in output_path.read_text()


def test_verdict_strong(tmp_path):
    output_path = tmp_path / "FARAL-report.md"
    text = build_report(_synthetic_input(), output_path)
    assert "Overall FARAL: STRONG PASS" in text
    assert "**Overall FARAL: STRONG PASS**" in text
    assert "**Overall FARAL: FAIL**" not in text


def test_verdict_fail_on_adapter_import(tmp_path):
    output_path = tmp_path / "FARAL-report.md"
    text = build_report(_synthetic_input(router_imports_adapters=True), output_path)
    assert "Overall FARAL: FAIL" in text
    assert "**Overall FARAL: FAIL**" in text
    assert "STRONG PASS" not in text


def test_verdict_fail_on_different_paths(tmp_path):
    output_path = tmp_path / "FARAL-report.md"
    text = build_report(_synthetic_input(osm_realtime_identical=False), output_path)
    assert "Overall FARAL: FAIL" in text
    assert "**Overall FARAL: FAIL**" in text
    assert "STRONG PASS" not in text
