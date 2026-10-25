"""
Side-by-side comparison of all four filters.

Generates one seeded dataset, runs every filter on it, computes RMSE, lag,
residual noise and amplitude attenuation, prints them, saves them to
results/metrics.csv and plots all filters against the true signal.

Usage: python analysis.py
"""

import random
from math import sin
import matplotlib.pyplot as plt

from utils import generate_data, simulate_calibration, generate_rates, AMPLITUDE
from metrics import rmse, lag, residual_noise, attenuation

from filters.moving_average_filter import MovingAverageFilter
from filters.low_pass_filter import LowPassFilter
from filters.complementary_filter import ComplementaryFilter
from filters.kalman_filter import KalmanFilter


FILTER_NAMES = {
    "raw": "Raw Signal",
    "maf": "Moving Average Filter",
    "lpf": "Low Pass Filter",
    "cf": "Complementary Filter",
    "kf": "Kalman Filter"
}


def make_data(seed=42):
    """Generates all the data noise and clean both for analysis."""
    random.seed(seed)

    # x: [x1, x2, ..., xN]; yn: noisy y
    (x_points, y_noisy), dt = generate_data()
    calibration_rates, calibration_positions, bias = simulate_calibration()
    _, rates = generate_rates(bias, x_points)

    y_true = [AMPLITUDE * sin(x) for x in x_points]

    return (
        x_points,
        y_noisy,
        rates,
        y_true,
        calibration_rates,
        calibration_positions,
        bias,
        dt,
    )


def run_filters(y_noisy: list, raw_rates: list, dt: float, calibration_rates: float, calibration_positions: float):
    """Returns dictionary containing filtered data from each filter."""
    N = 10          # for moving average filter
    maf = MovingAverageFilter(N)

    alpha = 0.82    # for low pass filter
    lpf = LowPassFilter(alpha)

    beta = 0.975    # for complementary filter
    cf = ComplementaryFilter(beta)
    cf.calibrate(calibration_rates)

    kf = KalmanFilter()
    kf.calibrate(calibration_rates, calibration_positions)

    n = len(y_noisy)
    return {
        "raw": y_noisy,
        "maf": [maf.update(y_noisy[i]) for i in range(n)],
        "lpf": [lpf.update(y_noisy[i]) for i in range(n)],
        "cf": [cf.update(y_noisy[i], raw_rates[i], dt) for i in range(n)],
        "kf": [kf.update(y_noisy[i], raw_rates[i], dt) for i in range(n)],
    }


def compute_metrics(outputs: dict, y_true: list, dt: float):
    """Returns a disctionary containing the evaluation metrics."""
    metrics = {"raw": {}, "maf": {}, "lpf": {}, "cf": {}, "kf": {}}

    for name, signal in outputs.items():
        metrics[name]["rmse"] = rmse(signal, y_true)
        metrics[name]["lag"] = lag(signal, y_true) * dt
        metrics[name]["residual_noise"] = residual_noise(signal, y_true)
        metrics[name]["attenuation"] = attenuation(signal, y_true)

    return metrics


def display_metrics(metrics: dict):
    """Prints all the metrics neatly on the CLI."""
    for name in metrics:
        print(f"\n{FILTER_NAMES[name]} ({name})")
        print(f"RMSE: {metrics[name]["rmse"]:.4f}")
        print(f"lag (rad): {metrics[name]["lag"]:.4f}")
        print(f"residual noise: {metrics[name]["residual_noise"]:.4f}")
        print(f"amplitude attenuation: {metrics[name]["attenuation"]:.4f}")


def save_metrics(metrics: dict, filename="results/metrics.csv"):
    """Saves the metrics in a csv file."""
    with open(filename, "w") as f:
        f.write("Filter,RMSE,Lag (rad),Residual Noise,Attenuation\n")

        for name in metrics:
            f.write(f"{FILTER_NAMES[name]},{metrics[name]["rmse"]:.4f},{metrics[name]["lag"]:.4f},{metrics[name]["residual_noise"]:.4f},{metrics[name]["attenuation"]:.4f}\n")


def plot_overlay(x_points: list, y_true: list, outputs: dict, filename=None):
    """Plots all filters in the same graph for comparison. If filename given, also saves the figure."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_points, y_true, color="black", linewidth=2, label="true")

    ax.plot(x_points, outputs["raw"], color="lightgray", linewidth=1, label="Raw Signal")
    ax.plot(x_points, outputs["maf"], label="Moving Average Filter (N=10)")
    ax.plot(x_points, outputs["lpf"], label="Low Pass Filter (α=0.82)")
    ax.plot(x_points, outputs["cf"], label="Complementary Filter (β=0.975)")
    ax.plot(x_points, outputs["kf"], label="Kalman Filter")

    ax.set_title("Filters Comparison")
    ax.set_xlabel("X values (rad)")
    ax.set_ylabel("Signal Value")
    ax.legend(loc="lower left")
    ax.grid(True)

    if filename:
        fig.savefig(f"results/{filename}.png", dpi=300, bbox_inches="tight")

    plt.show()


if __name__ == "__main__":
    x_points, y_noisy, raw_rates, y_true, calibration_rates, calibration_positions, bias, dt = make_data()
    outputs = run_filters(y_noisy, raw_rates, dt, calibration_rates, calibration_positions)
    metrics = compute_metrics(outputs, y_true, dt)
    display_metrics(metrics)
    save_metrics(metrics)
    plot_overlay(x_points, y_true, outputs, "comparison_overlay")
