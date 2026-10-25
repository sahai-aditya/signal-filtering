"""
Generates every figure used in results/results.pdf.

Reuses the data, filters and metrics from analysis.py to produce:
  - small_multiples: each filter in its own panel against the true signal (seed 42)
  - kalman_gain:     the Kalman gain K at every step vs. the complementary filter's fixed gain
  - rmse_seeds:      average RMSE of every filter over 50 different noise patterns
It also saves the 50-seed averages to results/metrics_50_seeds.csv.

Usage: python report.py
"""

import os

import matplotlib.pyplot as plt

import main
from analysis import make_data, run_filters, compute_metrics, FILTER_NAMES
from filters.kalman_filter import KalmanFilter


FIG_DIR = "results/figures"
N_SEEDS = 50
METRICS = ["rmse", "lag", "residual_noise", "attenuation"]

# same colour for each filter in every figure
COLORS = {"raw": "#b9b8b0", "maf": "#2a78d6", "lpf": "#eb6834", "cf": "#1baf7a", "kf": "#c98a00"}
LABELS = {
    "maf": "Moving Average (N=10)",
    "lpf": "Low Pass (α=0.82)",
    "cf": "Complementary (β=0.975)",
    "kf": "Kalman",
}
FILTERS = ["maf", "lpf", "cf", "kf"]


def save(fig, name: str):
    """Saves a figure as PNG (for the README) and PDF (for the LaTeX report)."""
    fig.savefig(f"{FIG_DIR}/{name}.png", dpi=200, bbox_inches="tight")
    fig.savefig(f"{FIG_DIR}/{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_small_multiples(x_points: list, y_true: list, outputs: dict):
    """
    Each filter in its own panel (2x2 grid) against the true signal and the noisy input.
    The shaded area between a filter and the true signal is its error.
    """
    fig, axes = plt.subplots(2, 2, figsize=(10, 5.5), sharex=True, sharey=True)

    for ax, name in zip(axes.flat, FILTERS):
        ax.plot(x_points, outputs["raw"], color=COLORS["raw"], linewidth=0.8)
        ax.fill_between(x_points, outputs[name], y_true, color=COLORS[name], alpha=0.25, linewidth=0)
        ax.plot(x_points, y_true, color="black", linewidth=1.6)
        ax.plot(x_points, outputs[name], color=COLORS[name], linewidth=2)

        ax.set_title(LABELS[name], loc="left", fontweight="bold")
        ax.grid(True, alpha=0.3)

    fig.supxlabel("X values (rad)")
    fig.supylabel("Signal Value")
    fig.suptitle("Black = true signal, grey = noisy input, shaded = error", fontsize=10)
    fig.tight_layout()
    save(fig, "small_multiples")


def kalman_gains(calibration_rates: list, calibration_positions: list, dt: float, n: int):
    """
    Returns the Kalman gain K at every step.

    K only depends on R and Q (never on the measurements), so we can repeat
    steps 2, 3 and 5 of the Kalman filter on their own to see how K changes.
    """
    
    R, Q = kf.R, kf.rates_var * dt ** 2

    p = R           # starting uncertainty, same as in KalmanFilter.calibrate()
    gains = []
    for _ in range(n - 1):  # the first sample only sets the starting estimate
        p_pred = p + Q              # step 2: uncertainty grows
        k = p_pred / (p_pred + R)   # step 3: Kalman gain
        p = (1 - k) * p_pred        # step 5: uncertainty shrinks
        gains.append(k)

    return gains


def plot_kalman_gain(gains: list, beta: float = 0.975):
    """Kalman gain over time compared with the complementary filter's fixed gain."""
    fig, ax = plt.subplots(figsize=(9, 3.2))
    steps = range(1, len(gains) + 1)
    ax.plot(steps, gains, color=COLORS["kf"], linewidth=2, label="Kalman gain K")
    ax.axhline(1 - beta, color=COLORS["cf"], linewidth=1.5, linestyle="--",
               label=f"Complementary gain 1 − β = {1 - beta:.3f}")

    ax.set_ylim(0, 0.55)
    ax.set_xlabel("Sample")
    ax.set_ylabel("Gain")
    ax.set_title(f"K starts at {gains[0]:.2f} and settles at {gains[-1]:.3f}", fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    save(fig, "kalman_gain")


def multi_seed_metrics(n_seeds: int = N_SEEDS):
    """Runs the full comparison for seeds 0 .. n_seeds-1 and returns mean and std. dev. of every metric."""
    values = {name: {m: [] for m in METRICS} for name in FILTER_NAMES}

    for seed in range(n_seeds):
        x_points, y_noisy, rates, y_true, cal_rates, cal_positions, bias, dt = make_data(seed)
        outputs = run_filters(y_noisy, rates, dt, cal_rates, cal_positions)
        metrics = compute_metrics(outputs, y_true, dt)

        for name in metrics:
            for m in METRICS:
                values[name][m].append(metrics[name][m])

    summary = {}
    for name in values:
        summary[name] = {}
        for m in METRICS:
            v = values[name][m]
            mean = sum(v) / len(v)
            std = (sum((x - mean) ** 2 for x in v) / (len(v) - 1)) ** 0.5
            summary[name][m] = (mean, std)

    # kf_wins counts number of seeds for which kf has lower rmse than cf to find which is actually better
    kf_wins = sum(1 for i in range(n_seeds) if values["kf"]["rmse"][i] < values["cf"]["rmse"][i])
    return summary, kf_wins


def save_multi_seed(summary: dict, filename: str = "results/metrics_50_seeds.csv"):
    """Saves mean and std. dev. of every metric as a CSV file."""
    with open(filename, "w") as f:
        f.write("Filter,RMSE mean,RMSE std,Lag mean (rad),Lag std (rad),Residual Noise mean,"
                "Residual Noise std,Attenuation mean,Attenuation std\n")
        for name in summary:
            row = [f"{summary[name][m][i]:.4f}" for m in METRICS for i in (0, 1)]
            f.write(f"{FILTER_NAMES[name]}," + ",".join(row) + "\n")


def plot_rmse_seeds(summary: dict):
    """Bar chart of RMSE (mean ± std) over all seeds."""
    names = ["raw"] + FILTERS
    labels = ["Raw", "Moving avg", "Low-pass", "Complementary", "Kalman"]
    means = [summary[n]["rmse"][0] for n in names]
    stds = [summary[n]["rmse"][1] for n in names]

    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    bars = ax.bar(labels, means, yerr=stds, color=[COLORS[n] for n in names], width=0.6, capsize=4)
    for bar, mean, std in zip(bars, means, stds):
        ax.text(bar.get_x() + bar.get_width() / 2, mean + std + 0.01, f"{mean:.3f}", ha="center", fontsize=9)

    ax.set_ylabel(f"RMSE (mean ± std, {N_SEEDS} seeds)")
    ax.set_ylim(0, 0.5)
    ax.grid(True, axis="y", alpha=0.3)
    save(fig, "rmse_seeds")


if __name__ == "__main__":
    os.makedirs(FIG_DIR, exist_ok=True)

    # seeded run (same data as analysis.py)
    x_points, y_noisy, rates, y_true, cal_rates, cal_positions, bias, dt = make_data()
    outputs = run_filters(y_noisy, rates, dt, cal_rates, cal_positions)

    # Figure 1: each filter in its own panel
    plot_small_multiples(x_points, y_true, outputs)

    # Figure 2: Kalman gain
    kf = main.run_kalman_filter()
    plot_kalman_gain(kf.gains)
    print(f"Kalman gain: first = {kf.gains[0]:.3f}, last = {kf.gains[-1]:.4f}")

    # Figure 3: robustness over many seeds
    summary, kf_wins = multi_seed_metrics()
    save_multi_seed(summary)
    plot_rmse_seeds(summary)
    print(f"Kalman beat complementary in {kf_wins}/{N_SEEDS} seeds")
    for name in summary:
        rmse_mean, rmse_std = summary[name]["rmse"]
        print(f"{FILTER_NAMES[name]:<22} RMSE {rmse_mean:.3f} ± {rmse_std:.3f}")

    print(f"Figures saved to {FIG_DIR}/")
