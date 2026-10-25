"""
Evaluation metrics comparing a filtered signal with the true signal.

rmse            - overall error
lag             - delay in samples that best aligns the two signals
residual_noise  - std. dev. of the error after removing the lag
attenuation     - filtered peak-to-peak / true peak-to-peak
"""

def rmse(signal: list, y_true: list):
    """Compares noisy signal and true signal and returns RMSE value."""
    n = len(signal)
    if len(y_true) != n:
        raise ValueError(f"Filtered signal and true signal must of the same length, got {n} and {len(y_true)}")

    rmse = 0
    for i in range(n):
        rmse += (signal[i] - y_true[i]) ** 2

    rmse = (rmse / n) ** 0.5
    return rmse


def lag(signal: list, y_true: list):
    """Computes RMSE for different shifted signals, returns shift giving smallest RMSE."""
    n = len(signal)
    if len(y_true) != n:
        raise ValueError(f"Filtered signal and true signal must of the same length, got {n} and {len(y_true)}")

    max_shift = 30  # means can't shift more than 30 values in the list
    best_shift, lowest_rmse = 0, float("inf")
    for s in range(max_shift):
        shift_rmse = rmse(signal[s:], y_true[:n-s])

        if shift_rmse < lowest_rmse:
            lowest_rmse = shift_rmse
            best_shift = s

    return best_shift


def residual_noise(signal: list, y_true: list):
    """Finds lag, shifts the signal then calculates standard deviation of error."""
    n = len(signal)
    if len(y_true) != n:
        raise ValueError(f"Filtered signal and true signal must of the same length, got {n} and {len(y_true)}")

    s = lag(signal, y_true)
    errors = [signal[s + i] - y_true[i] for i in range(n - s)]
    mean_error = sum(errors) / (n - s)

    residual_noise = 0
    for i in range(n - s):
        residual_noise += (errors[i] - mean_error) ** 2

    residual_noise = (residual_noise / (n - s - 1)) ** 0.5
    return residual_noise


def attenuation(signal: list, y_true: list):
    """Finds max and min of both filtered and true signal and computes amplitude attenuation."""
    n = len(signal)
    if len(y_true) != n:
        raise ValueError(f"Filtered signal and true signal must of the same length, got {n} and {len(y_true)}")

    signal_max = max(signal)
    signal_min = min(signal)
    true_max = max(y_true)
    true_min = min(y_true)

    attenuation = (signal_max - signal_min) / (true_max - true_min)
    return attenuation