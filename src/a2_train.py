"""A2: federated learning convergence experiments."""
import json
from pathlib import Path

import torch
import torch.nn as nn

from src.model_v5 import Scorer
from src.federated.data import partition, global_test_set
from src.federated.attack import sign_flip_scaled as sign_flip
from src.federated.aggregate import fedavg, krum, trimmed_mean
from src.federated.server import run_fl, eval_model


N_DEVICES = 10
PER_DEVICE = 500
N_ROUNDS = 20
N_TEST = 300
DEVICE = "cpu"
SEED = 0


def centralized_baseline(shards, test_set):
    torch.manual_seed(SEED)
    model = Scorer(hidden=32, layers=2)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MarginRankingLoss(margin=1.0)
    all_data = [s for shard in shards for s in shard]
    n = len(all_data)
    bs = 64
    for _ in range(N_ROUNDS):
        model.train()
        idx = torch.randperm(n).tolist()
        for start in range(0, n, bs):
            batch = [all_data[i] for i in idx[start:start + bs]]
            if len(batch) < 2:
                continue
            a = torch.stack([b[0] for b in batch])
            b = torch.stack([b[1] for b in batch])
            t = torch.ones(a.size(0))
            opt.zero_grad()
            loss = loss_fn(model(a), model(b), t)
            loss.backward()
            opt.step()
    return eval_model(model.state_dict(), test_set, device=DEVICE)


def main():
    out = Path("reports/raw")
    out.mkdir(parents=True, exist_ok=True)

    print("Building data...")
    shards = partition(N_DEVICES, PER_DEVICE)
    test_set = global_test_set(N_TEST)
    print(f"  {N_DEVICES} shards, {len(test_set)} test samples")

    results = {}

    print("\n[1] Centralized")
    acc_c = centralized_baseline(shards, test_set)
    results["centralized"] = {"final_acc": acc_c}
    print(f"  centralized = {acc_c:.1f}")

    print("\n[2] FedAvg, honest")
    _, hist = run_fl(shards, test_set, fedavg, n_rounds=N_ROUNDS)
    results["fedavg_honest"] = {"final_acc": hist[-1], "history": hist}

    print("\n[3] FedAvg, 1 Byzantine")
    _, hist = run_fl(shards, test_set, fedavg, n_rounds=N_ROUNDS,
                     n_byzantine=1, attack_fn=sign_flip)
    results["fedavg_1byz"] = {"final_acc": hist[-1], "history": hist}

    print("\n[4] FedAvg, 2 Byzantine")
    _, hist = run_fl(shards, test_set, fedavg, n_rounds=N_ROUNDS,
                     n_byzantine=2, attack_fn=sign_flip)
    results["fedavg_2byz"] = {"final_acc": hist[-1], "history": hist}

    print("\n[5] FedAvg, 3 Byzantine")
    _, hist = run_fl(shards, test_set, fedavg, n_rounds=N_ROUNDS,
                     n_byzantine=3, attack_fn=sign_flip)
    results["fedavg_3byz"] = {"final_acc": hist[-1], "history": hist}

    print("\n[6] Krum(f=3,m=3), 3 Byzantine")
    _, hist = run_fl(shards, test_set, lambda d: krum(d, f=3, m=3),
                     n_rounds=N_ROUNDS, n_byzantine=3, attack_fn=sign_flip)
    results["krum_3byz"] = {"final_acc": hist[-1], "history": hist}

    print("\n[7] TrimmedMean(0.2), 3 Byzantine")
    _, hist = run_fl(shards, test_set, lambda d: trimmed_mean(d, trim=0.2),
                     n_rounds=N_ROUNDS, n_byzantine=3, attack_fn=sign_flip)
    results["trimmed_3byz"] = {"final_acc": hist[-1], "history": hist}

    (out / "a2-results.json").write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out / 'a2-results.json'}")


if __name__ == "__main__":
    main()
