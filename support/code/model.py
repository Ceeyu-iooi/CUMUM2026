"""Example modelling module for the CUMCM template.

The functions use only NumPy so that the sample remains easy to run.
Replace the complete file with the real contest model implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np


@dataclass
class LinearModel:
    coef_: np.ndarray | None = None
    intercept_: float = 0.0

    def fit(self, x: np.ndarray, y: np.ndarray) -> "LinearModel":
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float).reshape(-1)
        if x.ndim != 2:
            raise ValueError("x must be a 2-D matrix")
        if len(x) != len(y):
            raise ValueError("x and y must have the same number of rows")

        design = np.column_stack([np.ones(len(x)), x])
        beta, *_ = np.linalg.lstsq(design, y, rcond=None)
        self.intercept_ = float(beta[0])
        self.coef_ = beta[1:]
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.coef_ is None:
            raise RuntimeError("fit must be called before predict")
        x = np.asarray(x, dtype=float)
        return self.intercept_ + x @ self.coef_


def mae(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.mean(np.abs(y_true - y_pred)))


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def r2_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    if ss_tot == 0.0:
        return 0.0
    return float(1.0 - ss_res / ss_tot)


def evaluate(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    return {
        "MAE": mae(y_true, y_pred),
        "RMSE": rmse(y_true, y_pred),
        "R2": r2_score(y_true, y_pred),
    }


def sensitivity_analysis(
    model: LinearModel,
    x: np.ndarray,
    ratios: np.ndarray | None = None,
) -> Dict[float, float]:
    """Perturb the first feature and report the mean prediction."""
    if ratios is None:
        ratios = np.array([-0.20, -0.10, 0.0, 0.10, 0.20])
    x = np.asarray(x, dtype=float)
    output: Dict[float, float] = {}
    for ratio in ratios:
        x_new = x.copy()
        x_new[:, 0] *= 1.0 + float(ratio)
        output[float(ratio)] = float(model.predict(x_new).mean())
    return output


def resource_allocation(
    costs: np.ndarray,
    effects: np.ndarray,
    budget: float,
    step: float = 0.1,
) -> np.ndarray:
    """Small greedy example for an allocation-type subproblem.

    This is only a template demonstration, not a universal optimizer.
    """
    costs = np.asarray(costs, dtype=float)
    effects = np.asarray(effects, dtype=float)
    if np.any(costs <= 0.0):
        raise ValueError("all costs must be positive")
    if budget < 0.0:
        raise ValueError("budget must be non-negative")

    score = effects / costs
    order = np.argsort(score)[::-1]
    x = np.zeros_like(costs)
    remaining = float(budget)

    for idx in order:
        unit_cost = costs[idx] * step
        while remaining + 1e-12 >= unit_cost and x[idx] + step <= 1.0 + 1e-12:
            x[idx] += step
            remaining -= unit_cost
    return np.clip(x, 0.0, 1.0)


if __name__ == "__main__":
    rng = np.random.default_rng(2026)
    x_demo = rng.normal(size=(30, 3))
    y_demo = 2.0 * x_demo[:, 0] - x_demo[:, 1] + 0.5
    model = LinearModel().fit(x_demo, y_demo)
    pred = model.predict(x_demo)
    print(evaluate(y_demo, pred))
