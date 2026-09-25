"""Cloud and device models for A1-v5. Slightly larger device."""
import torch
import torch.nn as nn


class Scorer(nn.Module):
    def __init__(self, hidden: int, layers: int):
        super().__init__()
        mods = []
        in_dim = 4
        for _ in range(layers):
            mods.append(nn.Linear(in_dim, hidden))
            mods.append(nn.ReLU())
            in_dim = hidden
        mods.append(nn.Linear(in_dim, 1))
        self.net = nn.Sequential(*mods)

    def forward(self, x):
        return self.net(x).squeeze(-1)


def cloud_model():
    return Scorer(hidden=128, layers=3)


def device_model():
    return Scorer(hidden=32, layers=2)
