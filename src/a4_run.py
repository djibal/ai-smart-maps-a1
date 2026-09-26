import json
from pathlib import Path

from src.mesh.sim import run_trials
from src.mesh.duty import battery_pct_per_day

CONFIGS = [
    ("urban_5pct_20m", 1000, 20, 0.05, 100.0),
    ("urban_10pct_20m", 1000, 20, 0.10, 100.0),
    ("urban_20pct_20m", 1000, 20, 0.20, 100.0),
    ("suburban_5pct_30m", 1000, 30, 0.05, 100.0),
    ("suburban_10pct_30m", 1000, 30, 0.10, 100.0),
    ("open_5pct_50m", 1000, 50, 0.05, 100.0),
    ("open_10pct_50m", 1000, 50, 0.10, 100.0),
    ("always_on_20m", 1000, 20, 1.00, 100.0),
    ("dense_urban_20pct", 2000, 20, 0.20, 100.0),
    ("sparse_suburban_10pct", 500, 30, 0.10, 100.0),
]

N_TRIALS = 30


def main():
    out = Path("reports/raw")
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, density, radius, duty, cycle in CONFIGS:
        print(f"\n[{name}] density={density}/km^2 radius={radius}m duty={duty}")
        r = run_trials(
            n_devices=density, radius=radius,
            duty_cycle=duty, cycle_ms=cycle,
            target_radius_m=200.0, n_trials=N_TRIALS,
            seed=abs(hash(name)) % 65536,
        )
        r["density"] = density
        r["radius_m"] = radius
        r["duty"] = duty
        r["cycle_ms"] = cycle
        r["battery_pct_per_day"] = battery_pct_per_day(duty)
        results[name] = r
        print(f"  p50={r['p50_ms']:.1f}ms p95={r['p95_ms']:.1f}ms "
              f"unreachable={r['n_unreachable']}/{N_TRIALS} "
              f"battery={r['battery_pct_per_day']:.2f}%/day")
    (out / "a4-results.json").write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out / 'a4-results.json'}")


if __name__ == "__main__":
    main()
