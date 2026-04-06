"""Simple region-based layout engine.

This is the glue between high-level UI regions and the renderer. It tracks
header/status state and performs coarse redraws when those regions change.
"""

from typing import Any
from .regions import Header, MainContent, StatusBar


class LayoutEngine:
    def __init__(self, ui: Any):
        self.ui = ui
        self.header = Header("HEADER", ui)
        self.main = MainContent(ui)
        self.status = StatusBar(ui)
        self._needs_redraw = False
        self._last_header_content: str = ""
        self._last_status_left: str = ""
        self._last_status_right: str = ""
        
    # Region objects call this when they change. The redraw is deferred so the
    # caller does not need to think about the mechanics immediately.
    def trigger_redraw(self):
        """Signals that the UI needs a redraw."""
        self._needs_redraw = True

    # This redraw strategy is intentionally blunt. It is not trying to be a
    # full-screen terminal framework; it just keeps static regions coherent.
    def redraw_ui(self):
        """Performs a full redraw of the static UI elements if needed.
        This is a basic implementation that just clears and redraws,
        not a true persistent live region.
        """
        if not self._needs_redraw:
            return

        self._needs_redraw = False
        
        current_header_content = self.header.content or ""
        current_status_left = self.status.left or ""
        current_status_right = self.status.right or ""

        # Avoid repainting when the logical layout state is unchanged.
        if (current_header_content == self._last_header_content and
            current_status_left == self._last_status_left and
            current_status_right == self._last_status_right):
            return

        # The current implementation redraws by clearing and replaying the
        # static regions. That is simple, but it is also why main content is
        # treated as append-only output elsewhere.
        self.ui.clear()
        self.ui.move_cursor(0, 0) # Move to top-left

        # Header is rendered first so it behaves like a fixed top region.
        if self.header.content:
            self.ui.print(self.header.content, color=self.header.color)
            if hasattr(self.ui.renderer, "console"): # Add a separator only if rich is active
                console_width = self.ui.renderer.console.size.width
                self.ui.print("-" * console_width, color=self.header.color)
            self._last_header_content = self.header.content
        else:
            self._last_header_content = ""

        # Main content is still owned by the normal print path. This file only
        # manages the coarse layout regions around it.

        # Status is rendered last to simulate a bottom summary line.
        if self.status.left or self.status.right:
            # This is not truly bottom-anchored yet; it is an append-only
            # compromise until the layout system grows a richer live model.
            console_width = self.ui.renderer.console.size.width if hasattr(self.ui.renderer, "console") else 80 # Default to 80 if no rich console
            status_line = f"{current_status_left:<{console_width // 2}}{current_status_right:>{console_width // 2}}"
            self.ui.print(status_line, color=self.status.color)
            self._last_status_left = self.status.left
            self._last_status_right = self.status.right
        else:
            self._last_status_left = ""
            self._last_status_right = ""

        # prompt_toolkit expects the input cursor to land after any redraw
        # output; this handoff is intentionally approximate.
        self.ui.move_cursor_to_input_line() # This method needs to be added to UINamespace
