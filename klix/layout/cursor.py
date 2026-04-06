"""Low-level cursor helpers.

Cursor control is kept in its own file so the rest of the framework does not
need to sprinkle escape sequences through UI code.
"""

import sys


class CursorControl:
    def move_to(self, x: int, y: int):
        """Moves the cursor to the specified X, Y position (1-based)."""
        sys.stdout.write(f"\033[{y};{x}H")
        sys.stdout.flush()

    def hide(self):
        """Hides the cursor."""
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

    def show(self):
        """Shows the cursor."""
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()
