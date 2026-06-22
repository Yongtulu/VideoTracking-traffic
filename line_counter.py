"""
Virtual line crossing counter with direction detection.

Uses the sign of the cross product of the line vector and the vector from
line-start to the object's centroid to determine which side the object is on.
A crossing is registered when the sign flips between frames.
"""

import numpy as np
from config import LABEL_IN, LABEL_OUT


def _side(lx1: int, ly1: int, lx2: int, ly2: int, px: float, py: float) -> int:
    """Return +1 or -1 depending on which side of the line (lx1,ly1)→(lx2,ly2) point p is on."""
    cross = (lx2 - lx1) * (py - ly1) - (ly2 - ly1) * (px - lx1)
    return 1 if cross >= 0 else -1


class LineCounter:
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        # track_id → last known side (+1 / -1)
        self._last_side: dict[int, int] = {}
        self.counts = {LABEL_IN: 0, LABEL_OUT: 0}
        # track_id → direction label for the current frame (for drawing)
        self.crossed_this_frame: dict[int, str] = {}

    def update(self, track_id: int, cx: float, cy: float) -> str | None:
        """
        Call once per tracked object per frame.
        Returns the direction label if a crossing happened, else None.
        """
        current_side = _side(self.x1, self.y1, self.x2, self.y2, cx, cy)
        self.crossed_this_frame.pop(track_id, None)

        if track_id in self._last_side:
            if self._last_side[track_id] != current_side:
                # Determine direction: crossing from positive side → "IN", else "OUT"
                # Positive side is "above/left" of the line depending on orientation.
                # Convention: going from side +1 to -1 means crossing downward → IN
                direction = LABEL_IN if self._last_side[track_id] == 1 else LABEL_OUT
                self.counts[direction] += 1
                self.crossed_this_frame[track_id] = direction
                self._last_side[track_id] = current_side
                return direction

        self._last_side[track_id] = current_side
        return None

    def reset_frame(self):
        self.crossed_this_frame.clear()
