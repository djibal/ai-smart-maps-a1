import torch
from src.federated.data import partition, global_test_set
from src.federated.attack import sign_flip
from src.federated.aggregate import fedavg, krum, trimmed_mean


def test_partition_shape():
    shards = partition(3, 50, base_seed=900_000)
    assert len(shards) == 3
    for s in shards:
        assert len(s) > 0


def test_global_test_set():
    ts = global_test_set(30)
    assert len(ts) == 30
    for f0, f1, truth in ts:
        assert len(f0) == 4
        assert truth in (0, 1)


def test_sign_flip():
    d = {"a": torch.tensor([1.0, 2.0])}
    out = sign_flip(d)
    assert torch.allclose(out["a"], torch.tensor([-1.0, -2.0]))


def test_fedavg_identity():
    d = {"a": torch.tensor([1.0, 2.0])}
    out = fedavg([d, d, d])
    assert torch.allclose(out["a"], torch.tensor([1.0, 2.0]))


def test_trimmed_mean_drops_outlier():
    deltas = [{"a": torch.tensor([1.0])}, {"a": torch.tensor([1.1])},
              {"a": torch.tensor([1.2])}, {"a": torch.tensor([1.1])},
              {"a": torch.tensor([100.0])}]
    out = trimmed_mean(deltas, trim=0.2)
    assert out["a"].item() < 5.0


def test_krum_ignores_outlier():
    deltas = [{"a": torch.tensor([1.0])}, {"a": torch.tensor([1.1])},
              {"a": torch.tensor([1.2])}, {"a": torch.tensor([1.1])},
              {"a": torch.tensor([100.0])}]
    out = krum(deltas, f=1, m=3)
    assert out["a"].item() < 5.0
