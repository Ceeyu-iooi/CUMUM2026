"""Complete runnable example entry point for the CUMCM template.

Run from this directory with:
    python main.py

In a real contest project, replace this demo with the complete program used
for the paper. Every source file used in the paper should also be typeset in
the paper appendix and included in the submitted support-material archive.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from model import LinearModel, evaluate, resource_allocation, sensitivity_analysis
from preprocess import StandardScaler, make_demo_data, train_test_split


ROOT = Path(__file__).resolve().parent
RESULT_DIR = ROOT.parent / "result"


def write_metrics(path: Path, metrics: dict[str, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["metric", "value"])
        for key, value in metrics.items():
            writer.writerow([key, f"{value:.8f}"])


def write_sensitivity(path: Path, result: dict[float, float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["perturbation", "mean_prediction"])
        for ratio, value in sorted(result.items()):
            writer.writerow([f"{ratio:.4f}", f"{value:.8f}"])


def run_regression_demo() -> dict[str, float]:
    x, y = make_demo_data(n=160, seed=2026)
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_ratio=0.25,
        seed=2026,
    )

    scaler = StandardScaler()
    x_train_scaled = scaler.fit_transform(x_train)
    x_test_scaled = scaler.transform(x_test)

    model = LinearModel().fit(x_train_scaled, y_train)
    prediction = model.predict(x_test_scaled)
    metrics = evaluate(y_test, prediction)

    sens = sensitivity_analysis(model, x_test_scaled)
    write_metrics(RESULT_DIR / "metrics.csv", metrics)
    write_sensitivity(RESULT_DIR / "sensitivity.csv", sens)

    print("Regression metrics")
    for key, value in metrics.items():
        print(f"  {key}: {value:.6f}")

    print("Sensitivity analysis")
    for ratio, value in sorted(sens.items()):
        print(f"  {ratio:+.0%}: {value:.6f}")
    return metrics


def run_allocation_demo() -> np.ndarray:
    costs = np.array([3.0, 4.0, 2.5, 5.0, 6.0])
    effects = np.array([7.0, 8.0, 5.5, 9.0, 10.0])
    budget = 12.0
    decision = resource_allocation(costs, effects, budget, step=0.1)
    total_cost = float(costs @ decision)
    total_effect = float(effects @ decision)

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    np.savetxt(
        RESULT_DIR / "allocation.csv",
        np.column_stack([costs, effects, decision]),
        delimiter=",",
        header="cost,effect,decision",
        comments="",
        fmt="%.6f",
    )

    print("Allocation result")
    print("  decision:", decision)
    print(f"  total cost: {total_cost:.6f}")
    print(f"  total effect: {total_effect:.6f}")
    return decision


def main() -> None:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    run_regression_demo()
    run_allocation_demo()
    print(f"Results written to: {RESULT_DIR}")


if __name__ == "__main__":
    main()
