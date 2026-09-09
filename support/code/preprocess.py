"""Example preprocessing module for the CUMCM template.

Replace this file with the real preprocessing program used in the contest.
The program is intentionally self-contained and runnable.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np


@dataclass
class StandardScaler:
    mean_: np.ndarray | None = None
    scale_: np.ndarray | None = None

    def fit(self, x: np.ndarray) -> "StandardScaler":
        x = np.asarray(x, dtype=float)
        self.mean_ = x.mean(axis=0)
        self.scale_ = x.std(axis=0)
        self.scale_ = np.where(self.scale_ == 0.0, 1.0, self.scale_)
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.mean_ is None or self.scale_ is None:
            raise RuntimeError("fit must be called before transform")
        x = np.asarray(x, dtype=float)
        return (x - self.mean_) / self.scale_

    def fit_transform(self, x: np.ndarray) -> np.ndarray:
        return self.fit(x).transform(x)


def minmax_scale(x: np.ndarray) -> np.ndarray:
    """Scale each column to [0, 1]."""
    x = np.asarray(x, dtype=float)
    low = x.min(axis=0)
    high = x.max(axis=0)
    span = np.where(high > low, high - low, 1.0)
    return (x - low) / span


def train_test_split(
    x: np.ndarray,
    y: np.ndarray,
    test_ratio: float = 0.25,
    seed: int = 2026,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Random but reproducible train/test split."""
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if not 0.0 < test_ratio < 1.0:
        raise ValueError("test_ratio must be in (0, 1)")
    if len(x) != len(y):
        raise ValueError("x and y must have the same number of rows")

    rng = np.random.default_rng(seed)
    order = rng.permutation(len(x))
    n_test = max(1, int(round(len(x) * test_ratio)))
    test_idx = order[:n_test]
    train_idx = order[n_test:]
    return x[train_idx], x[test_idx], y[train_idx], y[test_idx]


def make_demo_data(n: int = 120, seed: int = 2026) -> Tuple[np.ndarray, np.ndarray]:
    """Generate a deterministic toy dataset for template compilation."""
    rng = np.random.default_rng(seed)
    x1 = rng.uniform(0.0, 10.0, n)
    x2 = rng.normal(5.0, 1.5, n)
    x3 = rng.uniform(-2.0, 2.0, n)
    noise = rng.normal(0.0, 0.25, n)
    y = 1.8 * x1 - 0.7 * x2 + 0.4 * x3 + 3.2 + noise
    x = np.column_stack([x1, x2, x3])
    return x, y


def save_matrix(path: str | Path, array: np.ndarray) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(path, np.asarray(array), delimiter=",", fmt="%.8f")


if __name__ == "__main__":
    x_demo, y_demo = make_demo_data()
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x_demo)
    print("x shape:", x_scaled.shape)
    print("y shape:", y_demo.shape)
    print("first scaled row:", x_scaled[0])
