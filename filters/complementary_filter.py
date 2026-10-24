class ComplementaryFilter:
    """
    Complementary filter that fuses a direct measurement of x with
    a measurement of its rate of change (dx/dt).

    x_pred = x[n-1] + (v[n] - bias) * dt
    x[n]   = beta * x_pred + (1 - beta) * x_m[n]

    The rate source is trusted over short times (smooth, but drifts),
    and the direct source over long times (noisy, but drift-free).
    Higher beta means more smoothing, but slower drift correction.
    Processes one sample at a time, so it works for both
    stored and real-time data.
    """
    def __init__(self, beta: float):
        if not 0 < beta < 1:
            raise ValueError(f"beta must be (0, 1), got {beta}.")

        self.beta = beta
        self.bias = None
        self.prev_pos = None

    def calibrate(self, stationary_rates: list):
        """Estimate the rate bias from readings taken while x is not changing."""
        if len(stationary_rates) == 0:
            raise ValueError("Need at least one reading to calibrate.")

        self.bias = sum(stationary_rates) / len(stationary_rates)

    def update(self, xm: float, vm: float, dt: float):
        """
        Return the new estimate of x.

        xm: measured value of x
        vm: measured rate of change of x (dx/dt)
        dt: time since the previous sample
        """
        if self.bias is None:
            raise RuntimeError("Call calibrate() before update.")

        if self.prev_pos is None:
            self.prev_pos = xm
            return xm

        vc = vm - self.bias # get the unbiased rate

        x_pred = self.prev_pos + vc * dt
        clean_val = self.beta * x_pred + (1 - self.beta) * xm

        self.prev_pos = clean_val
        return clean_val

    def reset(self):
        """Forget the filter's history; keep the calibration."""
        self.prev_pos = None
