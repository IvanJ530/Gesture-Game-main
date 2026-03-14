"""
Tier 3 – UI
Logger: appends one row per resolved round to a timestamped CSV file.

Columns: round, p1_gesture, p2_gesture, p1_hp, p2_hp, result, timestamp
"""

import csv
import os
import time


class Logger:
    COLUMNS = ["round", "p1_gesture", "p2_gesture",
               "p1_hp", "p2_hp", "result", "timestamp"]

    def __init__(self, log_dir: str = "logs"):
        os.makedirs(log_dir, exist_ok=True)
        ts = int(time.time())
        self._path = os.path.join(log_dir, f"game_{ts}.csv")
        with open(self._path, "w", newline="") as f:
            csv.writer(f).writerow(self.COLUMNS)
        print(f"[Logger] Writing to {self._path}")

    def log(self, round_num: int, p1_gesture: str, p2_gesture: str,
            p1_hp: int, p2_hp: int, result: str):
        """Append one round's data."""
        with open(self._path, "a", newline="") as f:
            csv.writer(f).writerow([
                round_num, p1_gesture, p2_gesture,
                p1_hp, p2_hp, result,
                round(time.time(), 3),
            ])
