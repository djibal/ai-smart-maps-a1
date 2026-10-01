"""Tests for the TDLA markdown report formatter."""
from src.tdla_report import build_report

_TIERS = ("hot", "warm", "cold", "archive")


def _tier_stats(count: int, stored_kb: float) -> dict:
    return {"count": count, "total_stored_size_kb": stored_kb}


def _snapshot(stored_kb_each: float, count: int = 4) -> dict:
    return {name: _tier_stats(count, stored_kb_each) for name in _TIERS}


def _latency(fail_tier: str | None = None) -> dict:
    entries = {}
    for name in _TIERS:
        passed = name != fail_tier
        entries[name] = {
            "p95_ms": 8.0 if passed else 50.0,
            "slo_ms": 10.0,
            "pass": passed,
        }
    return entries


def _synthetic_input(
    *,
    day_730_each: float = 25.0,
    final_each: float = 25.0,
    final_day: int = 1094,
    fail_tier: str | None = None,
) -> dict:
    """Complete synthetic TDLA input. Day keys are strings, matching JSON."""
    return {
        "config": {
            "n_cities": 100,
            "sim_days": 1095,
            "segment_km_per_city": 5000,
        },
        "aggregate": {
            "snapshots": {
                "730": _snapshot(day_730_each),
                str(final_day): _snapshot(final_each),
            },
            "final_day": final_day,
            "n_cities": 100,
        },
        "latency": _latency(fail_tier),
    }


def test_build_report_writes_file(tmp_path):
    output_path = tmp_path / "reports" / "TDLA-report.md"
    text = build_report(_synthetic_input(), output_path)
    assert output_path.exists()
    written = output_path.read_text()
    assert "**Overall TDLA:" in written
    assert "**Overall TDLA:" in text


def test_verdict_strong(tmp_path):
    text = build_report(_synthetic_input(), tmp_path / "TDLA-report.md")
    assert "Overall TDLA: STRONG PASS" in text
    assert "PARTIAL PASS" not in text
    assert "**Overall TDLA: FAIL**" not in text


def test_verdict_partial(tmp_path):
    text = build_report(
        _synthetic_input(fail_tier="cold"),
        tmp_path / "TDLA-report.md",
    )
    assert "Overall TDLA: PARTIAL PASS" in text
    assert "STRONG PASS" not in text


def test_verdict_fail_on_storage_growth(tmp_path):
    # Day 730 sum = 4 * 25 = 100; final sum = 4 * 40 = 160 (> 1.5x).
    text = build_report(
        _synthetic_input(day_730_each=25.0, final_each=40.0),
        tmp_path / "TDLA-report.md",
    )
    assert "**Overall TDLA: FAIL**" in text
    assert "STRONG PASS" not in text
    assert "PARTIAL PASS" not in text
