"""Layout region objects.

These small classes give the rest of the framework named places to write:
header, main content, and status. The region objects themselves stay thin and
delegate actual rendering to the UI namespace.
"""

from typing import Any, Optional


# Regions are just state holders plus a redraw signal. The engine decides how
# that state is actually painted to the screen.
class Region:
    def __init__(self, name: str, ui: Any):
        self.name = name
        self.ui = ui
        self.content: Optional[str] = None
        self.color: Optional[str] = None

    def set(self, content: str, color: str = None):
        self.content = content
        self.color = color
        self.ui.layout.trigger_redraw()

    def clear(self):
        self.content = None
        self.color = None
        self.ui.layout.trigger_redraw()

class Header(Region):
    pass


# Main content is intentionally the simplest region because most output still
# flows through normal print/stream calls.
class MainContent:
    def __init__(self, ui: Any):
        self.ui = ui

    def print(self, *args, **kwargs):
        self.ui.print(*args, **kwargs)

    def stream(self, *args, **kwargs):
        return self.ui.stream(*args, **kwargs)

class StatusBar:
    def __init__(self, ui: Any):
        self.ui = ui
        self.left = ""
        self.right = ""
        self.color = None

    def set(self, left: str = "", right: str = "", color: str = None):
        self.left = left
        self.right = right
        self.color = color
        self.ui.layout.trigger_redraw()

    def clear(self):
        self.left = ""
        self.right = ""
        self.color = None
        self.ui.layout.trigger_redraw()
