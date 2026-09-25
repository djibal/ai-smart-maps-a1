"""FL orchestration: local train, aggregate, evaluate."""
import torch
import torch.nn as nn

from src.model_v5 import Scorer


def local_train(global_state, shard, epochs=1, batch_size=64, lr=1e-3, device="cpu"):
    model = Scorer(hidden=32, layers=2)
    model.load_state_dict(global_state)
    model.to(device)
    model.train()
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MarginRankingLoss(margin=1.0)
    n = len(shard)
    for _ in range(epochs):
        indices = torch.randperm(n).tolist()
        for start in range(0, n, batch_size):
            batch = [shard[i] for i in indices[start:start + batch_size]]
            if len(batch) < 2:
                continue
            a = torch.stack([b[0] for b in batch]).to(device)
            b = torch.stack([b[1] for b in batch]).to(device)
            t = torch.ones(a.size(0)).to(device)
            opt.zero_grad()
            loss = loss_fn(model(a), model(b), t)
            loss.backward()
            opt.step()
    new_state = model.state_dict()
    delta = {k: (new_state[k].cpu() - global_state[k].cpu()) for k in global_state.keys()}
    return delta


def eval_model(state, test_set, device="cpu"):
    model = Scorer(hidden=32, layers=2)
    model.load_state_dict(state)
    model.eval()
    model.to(device)
    correct = 0
    with torch.no_grad():
        for f0, f1, truth in test_set:
            a = torch.tensor([f0], dtype=torch.float32).to(device)
            b = torch.tensor([f1], dtype=torch.float32).to(device)
            pick = 0 if model(a).item() >= model(b).item() else 1
            if pick == truth:
                correct += 1
    return correct / len(test_set) * 100


def run_fl(shards, test_set, aggregator, n_rounds=20, n_byzantine=0,
           attack_fn=None, device="cpu", seed=0):
    torch.manual_seed(seed)
    global_state = Scorer(hidden=32, layers=2).state_dict()
    history = []
    for r in range(n_rounds):
        deltas = []
        for i, shard in enumerate(shards):
            d = local_train(global_state, shard, device=device)
            if i < n_byzantine and attack_fn is not None:
                d = attack_fn(d)
            deltas.append(d)
        agg = aggregator(deltas)
        global_state = {k: global_state[k] + agg[k] for k in global_state.keys()}
        acc = eval_model(global_state, test_set, device=device)
        history.append(acc)
        print(f"    round {r+1}/{n_rounds} acc={acc:.1f}")
    return global_state, history
