from utils import *

from filters.moving_average_filter import *
from filters.low_pass_filter import *


raw_data = generate_data()

"""
# implementing the moving average filter with N = 10
maf = MovingAverageFilter(N=10)

filtered = [maf.update(reading) for reading in raw_data[1]]

display_individual_filter(
    raw_data,
    [raw_data[0], filtered],
    "Moving Average Filter (N=10)",
    "Moving Average Filtered Values",
    # filename="moving_average_N10"
)
"""

# implementing low pass filter with different values of alpha to get a comparison
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
