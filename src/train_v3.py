"""Train cloud and device scorers on generated scenarios."""
import json
from pathlib import Path

import torch
import torch.nn as nn

from src.graph_v3 import (
    make_scenario, route_cost, route_features, oracle_pick,
)
from src.model_v3 import cloud_model, device_model

VARIANTS = ["linear", "quadratic", "threshold"]
TRAIN_N = 5000
TEST_N = 1000
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


def build_dataset(variant: str, n: int):
    X, y = [], []
    for seed in range(n):
        s = make_scenario(seed + (100_000 if variant else 0))
        for r in s.routes:
            X.append(route_features(s, r))
            y.append(route_cost(s, r, variant))
    return torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)


def train_one(model, X, y, epochs=50, lr=1e-3):
    model = model.to(DEVICE)
    X = X.to(DEVICE)
    y = y.to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()
    for epoch in range(epochs):
        opt.zero_grad()
        pred = model(X)
        loss = loss_fn(pred, y)
        loss.backward()
        opt.step()
    return model, float(loss.item())


def main():
    out = Path("reports/raw")
    out.mkdir(parents=True, exist_ok=True)
    summary = {}

    for variant in VARIANTS:
        Xtr, ytr = build_dataset(variant, TRAIN_N)
        cloud, cl = train_one(cloud_model(), Xtr, ytr)
        device, dl = train_one(device_model(), Xtr, ytr)

        torch.save(cloud.state_dict(), out / f"cloud-{variant}.pt")
        torch.save(device.state_dict(), out / f"device-{variant}.pt")

        summary[variant] = {
            "cloud_loss": cl,
            "device_loss": dl,
            "train_n": TRAIN_N,
            "device": DEVICE,
        }
        print(f"[{variant}] cloud_loss={cl:.3f} device_loss={dl:.3f}")

    (out / "train-summary.json").write_text(json.dumps(summary, indent=2))
    print(f"wrote {out / 'train-summary.json'}")


if __name__ == "__main__":
    main()
