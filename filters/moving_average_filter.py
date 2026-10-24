class MovingAverageFilter:
    """
    Moving average filter over the last N samples.

    Processes one sample at a time, so it works for both
    stored and real-time data.
    """
    def __init__(self, N):
        if N < 1:
            raise ValueError(f"N must be at least 1, got {N}.")

        self.N = N  # number of readings considered while computing average
        self.recent_vals = []   # will be of length N
    
    def update(self, xm: float):
        """Using the last N values, computes the new average."""
        clean_val = 0

        if len(self.recent_vals) >= self.N:
            del self.recent_vals[0]
        
        self.recent_vals.append(xm)

        for val in self.recent_vals:
            clean_val += val

        clean_val /= len(self.recent_vals)

        return clean_val

    def reset(self):
        """Forget the filter's history, so it can be reused on new data."""
        self.recent_vals = []    