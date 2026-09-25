"""Train 5 seeds per variant. Report distribution, not one sample."""
import json
import statistics
from pathlib import Path

import torch
import torch.nn as nn

from src.graph_v3 import make_scenario, route_cost, route_features, oracle_pick
from src.model_v5 import cloud_model, device_model

VARIANTS = ["linear", "quadratic", "threshold"]
TRAIN_N = 5000
TEST_N = 1000
SEEDS = [0, 1, 2, 3, 4]
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
MARGIN = 1.0


def build_pairs(variant, n, seed_block):
    Xa, Xb = [], []
    for seed in range(n):
        s = make_scenario(seed + seed_block)
        c0 = route_cost(s, s.routes[0], variant)
        c1 = route_cost(s, s.routes[1], variant)
        f0 = route_features(s, s.routes[0])
        f1 = route_features(s, s.routes[1])
        if c0 <= c1:
            Xa.append(f0); Xb.append(f1)
        else:
            Xa.append(f1); Xb.append(f0)
    return (torch.tensor(Xa, dtype=torch.float32),
            torch.tensor(Xb, dtype=torch.float32))


def train_one(model, Xa, Xb, torch_seed):
    torch.manual_seed(torch_seed)
    model = model.to(DEVICE)
    Xa, Xb = Xa.to(DEVICE), Xb.to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MarginRankingLoss(margin=MARGIN)
    target = torch.ones(Xa.size(0)).to(DEVICE)
    for _ in range(80):
        opt.zero_grad()
        loss = loss_fn(model(Xa), model(Xb), target)
        loss.backward()
        opt.step()
    return model


def agreement(model, variant, test_block):
    model.eval()
    ok = 0
    with torch.no_grad():
        for seed in range(test_block, test_block + TEST_N):
            s = make_scenario(seed)
            truth = oracle_pick(s, variant)
            fa = route_features(s, s.routes[0])
            fb = route_features(s, s.routes[1])
            xa = torch.tensor([fa], dtype=torch.float32).to(DEVICE)
            xb = torch.tensor([fb], dtype=torch.float32).to(DEVICE)
            pick = 0 if model(xa).item() >= model(xb).item() else 1
            if pick == truth:
                ok += 1
    return ok / TEST_N * 100


def main():
    out = Path("reports/raw")
    out.mkdir(parents=True, exist_ok=True)
    summary = {}

    for variant in VARIANTS:
        cloud_scores, device_scores = [], []
        for i, torch_seed in enumerate(SEEDS):
            Xa, Xb = build_pairs(variant, TRAIN_N, seed_block=300_000 + i * 10_000)
            cloud = train_one(cloud_model(), Xa, Xb, torch_seed)
            device = train_one(device_model(), Xa, Xb, torch_seed)
            cloud_scores.append(agreement(cloud, variant, test_block=3_000_000 + i * 2_000))
            device_scores.append(agreement(device, variant, test_block=3_000_000 + i * 2_000))
            print(f"[{variant} seed={torch_seed}] cloud={cloud_scores[-1]:.1f} "
                  f"device={device_scores[-1]:.1f}")

        summary[variant] = {
            "cloud_mean": statistics.mean(cloud_scores),
            "cloud_std": statistics.pstdev(cloud_scores),
            "device_mean": statistics.mean(device_scores),
            "device_std": statistics.pstdev(device_scores),
            "delta_mean_pp": statistics.mean(cloud_scores) - statistics.mean(device_scores),
            "cloud_runs": cloud_scores,
            "device_runs": device_scores,
        }

    (out / "train-v5-summary.json").write_text(json.dumps(summary, indent=2))
    print(f"wrote {out / 'train-v5-summary.json'}")


if __name__ == "__main__":
    main()
