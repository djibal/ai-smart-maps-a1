"""A1 test harness: run oracle, cloud, device on N scenarios."""
import argparse
import json
import time
from pathlib import Path

from src.graph import make_scenario
from src.oracle import score as oracle_score
from src.cloud import pick as cloud_pick
from src.device import pick as device_pick


def run(n: int):
    results = []
    for seed in range(n):
        s = make_scenario(seed)
        t0 = time.time()
        o = oracle_score(s)
        t_oracle = time.time() - t0

        t0 = time.time()
        c = cloud_pick(s)
        t_cloud = time.time() - t0

        t0 = time.time()
        d = device_pick(s)
        t_device = time.time() - t0

        results.append({
            "seed": seed,
            "oracle": o,
            "cloud": c,
            "device": d,
            "cloud_agrees": c == o,
            "device_agrees": d == o,
            "t_oracle_ms": t_oracle * 1000,
            "t_cloud_ms": t_cloud * 1000,
            "t_device_ms": t_device * 1000,
        })
        print(f"[{seed+1}/{n}] oracle={o} cloud={c} device={d} "
              f"(cloud {t_cloud*1000:.0f}ms, device {t_device*1000:.0f}ms)")

    out = Path("reports/raw/results.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out}")
    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--scenarios", type=int, default=100)
    args = p.parse_args()
    run(args.scenarios)
