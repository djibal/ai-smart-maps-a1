"""A4-v2: civic beacon configurations."""
import json
from pathlib import Path

from src.mesh.sim_v2 import run_trials_v2
from src.mesh.duty import battery_pct_per_day

CONFIGS = [
    # name,                        mobile_n, m_radius, m_duty, beacons, b_radius
    ("no_beacons_baseline",        1000, 20, 0.10, 0, 100),
    ("10_beacons_20m_10pct",       1000, 20, 0.10, 10, 100),
    ("20_beacons_20m_10pct",       1000, 20, 0.10, 20, 100),
    ("50_beacons_20m_10pct",       1000, 20, 0.10, 50, 100),
    ("20_beacons_20m_5pct",        1000, 20, 0.05, 20, 100),
    ("20_beacons_20m_20pct",       1000, 20, 0.20, 20, 100),
    ("20_beacons_30m_10pct",       1000, 30, 0.10, 20, 100),
    ("20_beacons_20m_10pct_50r",   1000, 20, 0.10, 20, 50),
]

N_TRIALS = 30


def main():
    out = Path("reports/raw")
    out.mkdir(parents=True, exist_ok=True)

    results = {}
    for name, n_mob, m_rad, m_duty, n_bcn, b_rad in CONFIGS:
        print(f"\n[{name}] mobile={n_mob}/{m_rad}m/{m_duty} "
              f"beacons={n_bcn}/{b_rad}m")
        r = run_trials_v2(
            n_mobile=n_mob, mobile_radius=m_rad, mobile_duty=m_duty,
            n_beacons=n_bcn, beacon_radius=b_rad,
            n_trials=N_TRIALS, seed=abs(hash(name)) % 65536,
        )
        r["mobile_n"] = n_mob
        r["mobile_radius"] = m_rad
        r["mobile_duty"] = m_duty
        r["beacons"] = n_bcn
        r["beacon_radius"] = b_rad
        r["battery_pct_per_day"] = battery_pct_per_day(m_duty)
        results[name] = r
        print(f"  p50={r['p50_ms']:.1f}ms p95={r['p95_ms']:.1f}ms "
              f"unreachable={r['n_unreachable']}/{N_TRIALS} "
              f"mobile_battery={r['battery_pct_per_day']:.2f}%/day")

    (out / "a4-v2-results.json").write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out / 'a4-v2-results.json'}")


if __name__ == "__main__":
    main()
