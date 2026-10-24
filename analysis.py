import random
from math import sin
import matplotlib.pyplot as plt

from utils import generate_data, simulate_calibration, generate_rates, AMPLITUDE
from metrics import rmse, lag, residual_noise, attenuation

from filters.moving_average_filter import MovingAverageFilter
from filters.low_pass_filter import LowPassFilter
from filters.complementary_filter import ComplementaryFilter
from filters.kalman_filter import KalmanFilter


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

def run_filters(raw_positions: list, raw_rates: list, dt: float, calibration_rates: float, calibration_positions: float):
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

    n = len(raw_positions)
    return {
        "maf": [maf.update(raw_positions[i]) for i in range(n)],
        "lpf": [lpf.update(raw_positions[i]) for i in range(n)],
        "cf": [cf.update(raw_positions[i], raw_rates[i], dt) for i in range(n)],
        "kf": [kf.update(raw_positions[i], raw_rates[i], dt) for i in range(n)],
    }

def compute_metrics(outputs: dict, y_noisy: list, y_true: list, dt: float):
    """Returns a disctionary containing the evaluation metrics."""
    metrics = {"maf": {}, "lpf": {}, "cf": {}, "kf": {}}

    for name, signal in metrics.items():
        metrics[name]["rmse"] = rmse(y_noisy, y_true)
        metrics[name]["lag"] = lag(y_noisy, y_true)
        metrics[name]["residual_noise"] = residual_noise(y_noisy, y_true)
        metrics[name]["attenuation"] = attenuation(y_noisy, y_true)

    return metrics

def display_metrics(metrics: dict):
    """Prints all the metrics neatly on the CLI."""
    names = {
        "maf": "Moving Average Filter",
        "lpf": "Low Pass Filter",
        "cf": "Complementary Filter",
        "kf": "Kalman Filter"
    }

    for name in names:
        print(f"\n{names[name]}")
        print(f"RMSE: {metrics[name]["rmse"]}")
        print(f"lag (rad): {metrics[name]["lag"]}")
        print(f"residual noise: {metrics[name]["residual_noise"]}")
        print(f"amplitude attenuation: {metrics[name]["attenuation"]}")

def plot_overlay(x_points: list, y_true: list, outputs: dict, filename=None):
    """Plots all filters in the same graph for comparison. If filename given, also saves the figure."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_points, y_true, color="black", linewidth=2, label="true")

    for name, filtered in outputs.items():
        ax.plot(x_points, filtered, label=name)

    ax.set_title("Filters Comparison")
    ax.set_xlabel("X values (rad)")
    ax.set_ylabel("Signal Value")
    ax.legend()
    ax.grid(True)

    if filename:
        fig.savefig(f"results/{filename}.png", dpi=300, bbox_inches="tight")

    plt.show()


if __name__ == "__main__":
    x_points, y_noisy, raw_rates, y_true, calibration_rates, calibration_positions, bias, dt = make_data()
    outputs = run_filters(y_noisy, raw_rates, dt, calibration_rates, calibration_positions)
    metrics = compute_metrics(outputs, y_noisy, y_true, dt)
    display_metrics(metrics)
    plot_overlay(x_points, y_true, outputs)
