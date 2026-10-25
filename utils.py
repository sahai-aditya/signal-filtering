"""
Synthetic data generation and plotting helpers.

Creates the noisy sine (position), the biased noisy cosine (rate) and the
stationary calibration readings, and plots a single filter against the raw
signal. Shared constants (amplitude, noise levels, range) live here.
"""

from math import pi as PI
from math import sin, cos

from random import random

import matplotlib.pyplot as plt


RATE_NOISE_FRAC = 0.2
POSITION_NOISE_FRAC = 0.5
AMPLITUDE = 2
START = 0
END = 2 * PI
N = 100


def generate_data(start=START, end=END, N=N, A=AMPLITUDE, position_noise_frac=POSITION_NOISE_FRAC):
    """Adds noise to a synthetic sine function and returns tuple of the form: (([x1, x2, ..., xN], [y1, y2, ... yN]), dx)"""
    dx = (end - start) / N
    noise_amp = position_noise_frac * A

    x_points = [start + i * dx for i in range(0, N + 1)]
    y_points = [A * sin(x) + (random() - 0.5) * noise_amp for x in x_points]

    return (x_points, y_points), dx


def simulate_calibration(N=200, A=AMPLITUDE, position_noise_frac=POSITION_NOISE_FRAC, rate_noise_frac=RATE_NOISE_FRAC):
    """
    Returns tuple containing rate values list (some noise and bias) and position values list (noise, no bias)
    and the bias.
    """
    bias = random() * 0.25  # will give a random value: [0, 0.25)
    rate_noise_amp = rate_noise_frac * A
    position_noise_amp = position_noise_frac * A

    rate_values = [(random() - 0.5) * rate_noise_amp + bias for _ in range(N)]

    phase = random() * 2 * PI
    position_values = [A * sin(phase) + (random() - 0.5) * position_noise_amp for _ in range(N)]
    
    return rate_values, position_values, bias


def generate_rates(bias, x_points, A=AMPLITUDE, rate_noise_frac=RATE_NOISE_FRAC):
    """Adds noise to a synthetic cosine function and returns tuple of the form: ([x1, x2, ..., xN], [y1, y2, ... yN])"""
    noise_amp = rate_noise_frac * A

    y_points = [A * cos(x) + (random() - 0.5) * noise_amp + bias for x in x_points]

    return (x_points, y_points)


def display_individual_filter(raw_data, filtered_data, title, label, filename=None):
    """
    Displays raw data and processed data together in a single graph.
    Will also save the graph as .png if filename given.
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    # plotting raw data
    ax.plot(raw_data[0], raw_data[1], color="tab:orange", linestyle="--", label="raw")

    # plotting filtered data
    ax.plot(filtered_data[0], filtered_data[1], color="tab:blue", linestyle="-", label=label)

    ax.set_title(title)
    ax.set_xlabel("X values (rad)")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True)

    if filename:
        fig.savefig(f"results/{filename}.png", dpi=300, bbox_inches="tight")

    plt.show()