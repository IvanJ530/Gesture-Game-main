"""
Tier 2 – Processor
StabilityFilter: sliding-window majority vote per player.

Problem it solves: raw frame-by-frame predictions flicker between gestures
due to motion blur, partial occlusion, or lighting changes.  We accumulate
the last N predictions and only emit a label when one class holds >= threshold
fraction of the window.
"""

from collections import deque


class StabilityFilter:
    def __init__(self, window_size: int = 10, threshold: float = 0.6):
        """
        window_size : number of recent predictions to consider
        threshold   : minimum fraction [0,1] for a prediction to be confirmed
        """
        self._window_size = window_size
        self._threshold   = threshold
        self._buffers = {1: deque(maxlen=window_size),
                         2: deque(maxlen=window_size)}

    # ------------------------------------------------------------------
    def update(self, player: int, gesture: str):
        """Push the latest raw prediction for a player (1 or 2)."""
        self._buffers[player].append(gesture)

    def get_stable(self, player: int):
        """
        Returns the confirmed gesture string if the buffer has enough votes,
        otherwise returns None (not stable yet).
        """
        buf = self._buffers[player]
        if len(buf) < self._window_size:
            return None                         # window not full yet

        counts = {}
        for g in buf:
            counts[g] = counts.get(g, 0) + 1

        best = max(counts, key=counts.get)
        if counts[best] / self._window_size >= self._threshold:
            return best
        return None

    def best_guess(self, player: int):
        """
        Returns the most frequent gesture in the buffer regardless of threshold.
        Useful as a fallback when the window isn't full yet.
        """
        buf = self._buffers[player]
        if not buf:
            return None
        counts = {}
        for g in buf:
            counts[g] = counts.get(g, 0) + 1
        return max(counts, key=counts.get)

    def reset(self, player: int = None):
        """Clear buffer(s). Pass player=1 or 2 to clear one side only."""
        if player is None:
            for p in self._buffers:
                self._buffers[p].clear()
        else:
            self._buffers[player].clear()
