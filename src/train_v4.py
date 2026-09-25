"""Train cloud and device scorers with pairwise margin ranking loss."""
import json
from pathlib import Path

import torch
import torch.nn as nn

from src.graph_v3 import make_scenario, route_cost, route_features
from src.model_v3 import cloud_model, device_model

VARIANTS = ["linear", "quadratic", "threshold"]
TRAIN_N = 5000
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
MARGIN = 1.0


def build_pairs(variant: str, n: int):
    """Return (feat_cheaper, feat_expensive) pairs based on oracle cost."""
    Xa, Xb = [], []
    for seed in range(n):
        s = make_scenario(seed + 200_000)  # different seed block than v3
        c0 = route_cost(s, s.routes[0], variant)
        c1 = route_cost(s, s.routes[1], variant)
        f0 = route_features(s, s.routes[0])
        f1 = route_features(s, s.routes[1])
        if c0 <= c1:
            Xa.append(f0); Xb.append(f1)
        else:
            Xa.append(f1); Xb.append(f0)
    return (
        torch.tensor(Xa, dtype=torch.float32),
        torch.tensor(Xb, dtype=torch.float32),
    )


def train_one(model, Xa, Xb, epochs=80, lr=1e-3):
    model = model.to(DEVICE)
    Xa, Xb = Xa.to(DEVICE), Xb.to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MarginRankingLoss(margin=MARGIN)
    target = torch.ones(Xa.size(0)).to(DEVICE)  # cheaper should score higher
    for _ in range(epochs):
        opt.zero_grad()
        sa = model(Xa)
        sb = model(Xb)
        loss = loss_fn(sa, sb, target)
        loss.backward()
        opt.step()
    return model, float(loss.item())


def main():
    out = Path("reports/raw")
    out.mkdir(parents=True, exist_ok=True)
    summary = {}

    for variant in VARIANTS:
        Xa, Xb = build_pairs(variant, TRAIN_N)
        cloud, cl = train_one(cloud_model(), Xa, Xb)
        device, dl = train_one(device_model(), Xa, Xb)

        torch.save(cloud.state_dict(), out / f"cloud-v4-{variant}.pt")
        torch.save(device.state_dict(), out / f"device-v4-{variant}.pt")

        summary[variant] = {"cloud_loss": cl, "device_loss": dl}
        print(f"[{variant}] cloud_loss={cl:.4f} device_loss={dl:.4f}")

    (out / "train-v4-summary.json").write_text(json.dumps(summary, indent=2))
    print(f"wrote {out / 'train-v4-summary.json'}")


if __name__ == "__main__":
    main()
