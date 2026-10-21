from utils import *

from filters.moving_average_filter import *


raw_data = generate_data()

# implementing the moving average filter with N = 10
MovingFilter = MovingAverageFilter(N=10)
clean_vals = [raw_data[0], []]

for reading in raw_data[1]:
    clean_vals[1].append(MovingFilter.update(reading))

display_individual_filter(
    raw_data,
    clean_vals,
    "Moving Average Filter (N=10)",
    "Moving Average Filtered Values",
    filename="moving_average_N10"
)
