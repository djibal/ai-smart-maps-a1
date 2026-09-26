"""A4-v3: realistic propagation runs."""
import json
from pathlib import Path

from src.mesh.sim_v3 import run_trials_v3
from src.mesh.duty import battery_pct_per_day

# All configs use 50 beacons/km^2 (the A4-v2 pass point) unless noted.
CONFIGS = [
    # name,                    mobile_n, m_radius, m_duty, beacons, b_radius, atten, p_loss, p_beacon_out
    ("baseline_50b",           1000, 20, 0.10, 50, 100, 1.0, 0.00, 0.00),
    ("loss_10pct",             1000, 20, 0.10, 50, 100, 1.0, 0.10, 0.00),
    ("loss_20pct",             1000, 20, 0.10, 50, 100, 1.0, 0.20, 0.00),
    ("atten_0.7",              1000, 20, 0.10, 50, 100, 0.7, 0.00, 0.00),
    ("atten_0.5",              1000, 20, 0.10, 50, 100, 0.5, 0.00, 0.00),
    ("beacon_out_5pct",        1000, 20, 0.10, 50, 100, 1.0, 0.00, 0.05),
    ("beacon_out_10pct",       1000, 20, 0.10, 50, 100, 1.0, 0.00, 0.10),
    ("mild_combined",          1000, 20, 0.10, 50, 100, 0.7, 0.10, 0.05),
    ("severe_combined",        1000, 20, 0.10, 50, 100, 0.5, 0.20, 0.10),
    ("100b_severe_combined",   1000, 20, 0.10, 100, 100, 0.5, 0.20, 0.10),
]

N_TRIALS = 30


def main():
    out = Path("reports/raw")
    out.mkdir(parents=True, exist_ok=True)
    results = {}

    for (name, n_mob, m_rad, m_duty, n_bcn, b_rad,
         atten, p_loss, p_out) in CONFIGS:
        print(f"\n[{name}] beacons={n_bcn}/{b_rad}m atten={atten} "
              f"loss={p_loss} outage={p_out}")
        r = run_trials_v3(
            n_mobile=n_mob, mobile_radius=m_rad, mobile_duty=m_duty,
            n_beacons=n_bcn, beacon_radius=b_rad,
            n_trials=N_TRIALS, seed=abs(hash(name)) % 65536,
            atten=atten, p_loss=p_loss, p_beacon_out=p_out,
        )
        r["mobile_n"] = n_mob
        r["mobile_radius"] = m_rad
        r["mobile_duty"] = m_duty
        r["beacons"] = n_bcn
        r["beacon_radius"] = b_rad
        r["atten"] = atten
        r["p_loss"] = p_loss
        r["p_beacon_out"] = p_out
        r["battery_pct_per_day"] = battery_pct_per_day(m_duty)
        results[name] = r
        print(f"  p50={r['p50_ms']:.1f}ms p95={r['p95_ms']:.1f}ms "
              f"unreachable={r['n_unreachable']}/{N_TRIALS}")

    (out / "a4-v3-results.json").write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out / 'a4-v3-results.json'}")


if __name__ == "__main__":
    main()
