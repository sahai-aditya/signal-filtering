class LowPassFilter:
    """
    First-order low-pass filter (exponential smoothing).
    
    y[n] = alpha * y[n-1] + (1 - alpha) * x[n]

    Higher alpha means more smoothing and more lag.
    Processes one sample at a time, so it works for both
    stored and real-time data.
    """

    def __init__(self, alpha: float):
        if not 0 <= alpha < 1:
            raise ValueError(f"alpha must be [0, 1), got {alpha}.")

        self.alpha = alpha
        self.prev_pos = None

    def update(self, new_val: float):
        """Using the last estimate and the new reading, computes the new estimate."""
        if self.prev_pos is None:  # for first sample when last estimate does not exist
            self.prev_pos = new_val
            return new_val

        clean_val = self.alpha * self.prev_pos + (1 - self.alpha) * new_val
        self.prev_pos = clean_val

        return clean_val

    def reset(self):
        """Forget the filter's history, so it can be reused on new data."""
        self.prev_pos = None
