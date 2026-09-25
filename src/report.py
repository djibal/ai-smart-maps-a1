"""Aggregate A1 results into a report."""
import json
from pathlib import Path

raw = Path("reports/raw/results.json")
out = Path("reports/A1-report.md")


def main():
    results = json.loads(raw.read_text())
    n = len(results)
    cloud_agree = sum(r["cloud_agrees"] for r in results) / n * 100
    device_agree = sum(r["device_agrees"] for r in results) / n * 100
    delta = cloud_agree - device_agree

    avg_cloud = sum(r["t_cloud_ms"] for r in results) / n
    avg_device = sum(r["t_device_ms"] for r in results) / n

    verdict = "PASS" if (
        cloud_agree >= 70 and device_agree >= 70 and delta <= 5.0
    ) else "FAIL"

    lines = [
        "# A1 Report",
        "",
        f"- Scenarios: {n}",
        "- Random baseline: 50.0%",
        f"- Cloud rank agreement: {cloud_agree:.1f}%",
        f"- Device rank agreement: {device_agree:.1f}%",
        f"- Delta: {delta:.1f} pp",
        f"- Avg cloud latency: {avg_cloud:.0f} ms",
        f"- Avg device latency: {avg_device:.0f} ms",
        "",
        f"## Verdict: {verdict}",
        "",
        "Pass criterion: both models > 70% and delta <= 5.0 pp.",
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
