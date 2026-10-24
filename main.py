import sys

from utils import generate_data, simulate_calibration, generate_rates, display_individual_filter

from filters.moving_average_filter import MovingAverageFilter
from filters.low_pass_filter import LowPassFilter
from filters.complementary_filter import ComplementaryFilter
from filters.kalman_filter import KalmanFilter


raw_data, dt = generate_data()
calibration_rates, calibration_positions, bias = simulate_calibration()
rates_data = generate_rates(bias, raw_data[0])


# implementing the moving average filter with N = 10
def run_moving_average(N=10):
    maf = MovingAverageFilter(N)
    filtered = [maf.update(reading) for reading in raw_data[1]]

    display_individual_filter(
        raw_data,
        [raw_data[0], filtered],
        f"Moving Average Filter (N={f})",
        "Moving Average Filtered Values",
        # filename=f"moving_average_N{N}"
    )


# implementing low pass filter with different values of alpha to get a comparison
def run_low_pass_filter():
    alpha_vals = [0.5, 0.7, 0.82, 0.9, 0.95]

    for alpha in alpha_vals:
        lpf = LowPassFilter(alpha)
        filtered = [lpf.update(reading) for reading in raw_data[1]]

        display_individual_filter(
            raw_data,
            [raw_data[0], filtered],
            f"Low Pass Filter (α={alpha})",
            "Low Pass Filtered Values",
            # filename=f"low_pass_{round(alpha * 100)}"
        )


# implementing the complementary filter
def run_complementary_filter():
    beta_vals = [0.90, 0.95, 0.99]
    for beta in beta_vals:
        cf = ComplementaryFilter(beta)
        cf.calibrate(calibration_rates)

        filtered = [cf.update(raw_data[1][i], rates_data[1][i], dt) for i in range(len(raw_data[0]))]

        display_individual_filter(
            raw_data,
            [raw_data[0], filtered],
            f"Complementary Filter (β={cf.beta})",
            "Complementary Filtered Values",
            # filename=f"complementary_{round(beta * 100)}"
        )


# implementing the kalman filter
def run_kalman_filter():
    kf = KalmanFilter()
    kf.calibrate(calibration_rates, calibration_positions)

    filtered = [kf.update(raw_data[1][i], rates_data[1][i], dt) for i in range(len(raw_data[0]))]

    display_individual_filter(
        raw_data,
        [raw_data[0], filtered],
        "Kalman Filter",
        "Kalman Filtered Values",
        # filename="kalman_filter"
    )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py [moving_average | low_pass | complementary | kalman]")
        sys.exit(1)

    choice = sys.argv[1]

    if choice == "moving_average":
        run_moving_average()

    elif choice == "low_pass":
        run_low_pass_filter()

    elif choice == "complementary":
        run_complementary_filter()

    elif choice == "kalman":
        run_kalman_filter()

    else:
        print(f"Unknown filter: {choice}")
        sys.exit(1)
