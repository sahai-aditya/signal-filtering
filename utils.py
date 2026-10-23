from math import pi as PI
from math import sin, cos

from random import random

import matplotlib.pyplot as plt


def generate_data(start=0, end=2*PI, N=100, A=2):
    """Adds noise to a synthetic sine function and returns list of the form: [[x1, x2, ..., xN], [y1, y2, ... yN]]"""
    h = (end - start) / N
    noise_amp = 0.5 * A    # maximum noise that can be added

    x_points = [start + i * h for i in range(0, N + 1)]
    y_points = [(A * sin(x) + (random() - 0.5) * noise_amp) for x in x_points]

    return (x_points, y_points)


def simulate_calibration(N=20, A=2):
    """
    Returns a list of rate values with some artificial noise and a bias.
    Here x represents t and y represents v (or dx/dt).
    """
    bias = random() * 0.25  # will give a random value: [0, 0.25)
    noise_amp = 0.2 * A     # noise amplitude in sensor, has to match with value used in generate_rates

    rate_values = [((random() - 0.5) * noise_amp + bias) for _ in range(N)]
    
    return rate_values, bias


def generate_rates(bias, x_points, A=2):
    """Adds noise to a synthetic cosine function and returns list of the form: [[x1, x2, ..., xN], [y1, y2, ... yN]]"""
    noise_amp = 0.2 * A    # maximum noise that can be added

    y_points = [(A * cos(x) + (random() - 0.5) * noise_amp + bias) for x in x_points]

    return (x_points, y_points)


def display_individual_filter(raw_data, filtered_data, title, label, filename=None):
    """
    Displays raw data and processed data together in a single graph.
    Will also save the graph as .png if 'save' set to True.
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


if __name__ == "__main__":
    raw = generate_data()
    clean = [raw[0][:], [(sin(x)) for x in raw[0]]]
    display_individual_filter(raw, clean, "Clean", "clean")