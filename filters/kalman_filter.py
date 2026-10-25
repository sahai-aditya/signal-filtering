class KalmanFilter:
    """
    1D Kalman filter that fuses a direct measurement of x with
    a measurement of its rate of change (dx/dt).

    x_pred = x[n-1] + (v[n] - bias) * dt
    P_pred = P[n-1] + Q
    K      = P_pred / (P_pred + R)
    x[n]   = x_pred + K * (x_m[n] - x_pred)
    P[n]   = (1 - K) * P_pred

    Unlike the complementary filter, the gain K is computed every step.
    bias, R and Q come from calibrate(), which must be called first.
    Processes one sample at a time, so it works for both
    stored and real-time data.
    """
    def __init__(self):
        self.bias = None
        self.R = None
        self.rates_var = None

        self.prev_pos = None
        self.prev_uncertainty = None

        self.gains = []

    def calibrate(self, stationary_rates: list, stationary_positions: list):
        """
        Computes bias, R and Q using the stationary sensor readings.
        stationary_rates -> list containing value of rate (dx/dt) while keeping sensor stationary
        stationary_positions -> list containing value of x while keeping sensor stationary
        """
        if len(stationary_rates) < 2:
            raise ValueError("Need at least two readings to calibrate.")

        rates_mean, positions_mean = 0, 0
        rates_var, positions_var = 0, 0
        N = len(stationary_rates)

        for i in range(N):
            rates_mean += stationary_rates[i]
            positions_mean += stationary_positions[i]

        rates_mean /= N
        positions_mean /= N

        for i in range(N):
            rates_var += (stationary_rates[i] - rates_mean) ** 2
            positions_var += (stationary_positions[i] - positions_mean) ** 2

        rates_var /= (N - 1)
        positions_var /= (N - 1)

        self.bias = rates_mean
        self.R = positions_var
        self.rates_var = rates_var

        self.prev_uncertainty = self.R  # as R variance in position -> initial uncertainty in position

    def update(self, xm: float, vm: float, dt: float):
        """Using new position and rate measurements, returns new estimate and updates attrs: prev_pos and prev_uncertainty."""
        if self.R is None:
            raise RuntimeError("Call calibrate() before update.")

        if self.prev_pos is None:
            self.prev_pos = xm
            return xm

        vc = vm - self.bias
        x_pred = self.prev_pos + vc * dt
        p_pred = self.prev_uncertainty + self.rates_var * dt ** 2
        k = p_pred / (p_pred + self.R)

        clean_val = x_pred + k * (xm - x_pred)
        p = (1 - k) * p_pred

        self.prev_pos = clean_val
        self.prev_uncertainty = p
        self.gains.append(k)

        return clean_val

    def reset(self):
        """Forget the filter's history; keep the calibration."""
        self.prev_pos = None
        self.prev_uncertainty = self.R
