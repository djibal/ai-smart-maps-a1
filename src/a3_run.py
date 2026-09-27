"""A3: Byzantine-fault-tolerant community report pipeline."""
import json
from pathlib import Path

import numpy as np

from src.community.scenario import make_scenario
from src.community.reporters import honest_reports, BYZANTINE
from src.community.aggregate import (
    majority, supermajority, reputation_weighted, bayesian_aggregate,
)

N_LOCATIONS = 500
N_REPORTERS = 20
HONEST_ACCURACY = 0.85
N_TRIALS = 20

CONFIGS = [
    (0.00, "random"),
    (0.10, "random"),
    (0.20, "random"),
    (0.30, "random"),
    (0.30, "invert"),
    (0.30, "coordinated"),
]


def one_trial(byz_frac, strategy, seed):
    truth = make_scenario(N_LOCATIONS, seed=seed)
    rng = np.random.default_rng(seed + 10_000)
    n_byz = int(round(N_REPORTERS * byz_frac))
    n_honest = N_REPORTERS - n_byz

    reports = []
    for i in range(n_honest):
        reports.append(honest_reports(truth, HONEST_ACCURACY, rng))
    for i in range(n_byz):
        reports.append(BYZANTINE[strategy](truth, rng))
    report_matrix = np.array(reports)

    reputations = np.ones(N_REPORTERS)
    results = {}
    for name, agg in [
        ("majority", lambda m, r: majority(m)),
        ("supermajority", lambda m, r: supermajority(m)),
        ("reputation_weighted", lambda m, r: reputation_weighted(m, r)),
        ("bayesian", lambda m, r: bayesian_aggregate(m)),
    ]:
        verdict = agg(report_matrix, reputations)
        results[name] = (verdict == truth).mean()
    return results


def main():
    out = Path("reports/raw")
    out.mkdir(parents=True, exist_ok=True)
    summary = {}
    for byz_frac, strategy in CONFIGS:
        key = f"byz{int(byz_frac*100):02d}_{strategy}"
        print(f"\n[{key}]")
        trial_results = {k: [] for k in
                         ["majority", "supermajority", "reputation_weighted", "bayesian"]}
        for t in range(N_TRIALS):
            r = one_trial(byz_frac, strategy, seed=t * 1000 + 1)
            for k, v in r.items():
                trial_results[k].append(v)
        agg = {k: float(np.mean(v)) for k, v in trial_results.items()}
        std = {k: float(np.std(v)) for k, v in trial_results.items()}
        for k in agg:
            print(f"  {k:22s} {agg[k]*100:5.1f}% +/- {std[k]*100:.1f}")
        summary[key] = {
            "byzantine_frac": byz_frac,
            "strategy": strategy,
            "accuracy": agg,
            "accuracy_std": std,
        }
    (out / "a3-results.json").write_text(json.dumps(summary, indent=2))
    print(f"\nwrote {out / 'a3-results.json'}")


if __name__ == "__main__":
    main()
