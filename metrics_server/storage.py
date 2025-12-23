"""
In-memory storage for the latest telemetry snapshot.
"""

import time

class TelemetryStorage:
    def __init__(self):
        self._snapshot = {}

    def update(self, data):
        ts = int(time.time())
        # Build a new snapshot with timestamp and replace the reference atomically
        self._snapshot = {
            sw: {**metrics, "timestamp": ts}
            for sw, metrics in data.items()
        }

    def snapshot(self):
        return self._snapshot
