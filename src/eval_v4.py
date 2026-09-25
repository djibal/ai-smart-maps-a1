"""Evaluate v4 ranking-trained models against oracle."""
import json
from pathlib import Path

import torch

from src.graph_v3 import make_scenario, route_features, oracle_pick
from src.model_v3 import cloud_model, device_model

VARIANTS = ["linear", "quadratic", "threshold"]
TEST_N = 1000
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


def load(path, model):
    m = model()
    m.load_state_dict(torch.load(path, map_location="cpu"))
    m.eval()
    return m.to(DEVICE)


def pick(model, fa, fb):
    with torch.no_grad():
        xa = torch.tensor([fa], dtype=torch.float32).to(DEVICE)
        xb = torch.tensor([fb], dtype=torch.float32).to(DEVICE)
        return 0 if model(xa).item() >= model(xb).item() else 1


def main():
    out = Path("reports/raw")
    results = {}

    for variant in VARIANTS:
        cloud = load(out / f"cloud-v4-{variant}.pt", cloud_model)
        device = load(out / f"device-v4-{variant}.pt", device_model)

        cloud_ok = device_ok = 0
        for seed in range(2_000_000, 2_000_000 + TEST_N):
            s = make_scenario(seed)
            truth = oracle_pick(s, variant)
            fa = route_features(s, s.routes[0])
            fb = route_features(s, s.routes[1])
            if pick(cloud, fa, fb) == truth:
                cloud_ok += 1
            if pick(device, fa, fb) == truth:
                device_ok += 1

        results[variant] = {
            "cloud_agreement": cloud_ok / TEST_N * 100,
            "device_agreement": device_ok / TEST_N * 100,
            "delta_pp": (cloud_ok - device_ok) / TEST_N * 100,
        }
        print(f"[{variant}] cloud={results[variant]['cloud_agreement']:.1f}% "
              f"device={results[variant]['device_agreement']:.1f}% "
              f"delta={results[variant]['delta_pp']:.1f}pp")

    (out / "eval-v4-summary.json").write_text(json.dumps(results, indent=2))
    print(f"wrote {out / 'eval-v4-summary.json'}")


if __name__ == "__main__":
    main()
