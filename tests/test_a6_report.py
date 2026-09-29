import json

from src.a6_report import write_report


def _synthetic_results(combined_detect_90d: float) -> dict:
    return {
        "osm": {
            "mean_lag_days": 365.2,
            "detect_90d": 0.10,
            "detect_90d_std": 0.02,
        },
        "satellite": {
            "mean_lag_days": 45.0,
            "detect_90d": 0.55,
            "detect_90d_std": 0.04,
        },
        "user": {
            "mean_lag_days": 20.0,
            "detect_90d": 0.60,
            "detect_90d_std": 0.05,
        },
        "combined": {
            "mean_lag_days": 80.0,
            "detect_90d": combined_detect_90d,
            "detect_90d_std": 0.03,
        },
        "n_trials": 20,
        "n_changes_total": 1800,
    }


def _write_and_read(tmp_path, combined_detect_90d: float) -> str:
    input_path = tmp_path / "a6-results.json"
    output_path = tmp_path / "A6-report.md"
    input_path.write_text(json.dumps(_synthetic_results(combined_detect_90d)))
    return write_report(input_path, output_path)


def test_report_writes_file(tmp_path):
    input_path = tmp_path / "a6-results.json"
    output_path = tmp_path / "out" / "A6-report.md"
    input_path.write_text(json.dumps(_synthetic_results(0.75)))
    text = write_report(input_path, output_path)
    assert output_path.exists()
    assert "**Overall A6: PARTIAL PASS**" in text
    assert "**Overall A6: PARTIAL PASS**" in output_path.read_text()


def test_verdict_partial(tmp_path):
    text = _write_and_read(tmp_path, 0.75)
    assert "Overall A6: PARTIAL PASS" in text
    assert "**Overall A6: PARTIAL PASS**" in text


def test_verdict_strong(tmp_path):
    text = _write_and_read(tmp_path, 0.95)
    assert "Overall A6: STRONG PASS" in text
    assert "**Overall A6: STRONG PASS**" in text


def test_verdict_fail(tmp_path):
    text = _write_and_read(tmp_path, 0.50)
    assert "Overall A6: FAIL" in text
    assert "**Overall A6: FAIL**" in text
    assert "PARTIAL PASS" not in text
    assert "STRONG PASS" not in text
