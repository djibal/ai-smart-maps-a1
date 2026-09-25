"""Byzantine attack simulations."""
import torch


def sign_flip(delta):
    """Flip sign. Weak when deltas are near zero."""
    return {k: -v for k, v in delta.items()}


def sign_flip_scaled(delta, factor=10.0):
    """Flip sign and amplify. Realistic adversarial strength."""
    return {k: -v * factor for k, v in delta.items()}


def scale(delta, factor=10.0):
    return {k: v * factor for k, v in delta.items()}


def random_noise(delta):
    return {k: torch.randn_like(v) * (v.std() + 1e-6) for k, v in delta.items()}


ATTACKS = {
    "sign_flip": sign_flip,
    "sign_flip_scaled": sign_flip_scaled,
    "scale": scale,
    "random_noise": random_noise,
}
