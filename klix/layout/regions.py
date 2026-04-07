"""Layout region objects.

These small classes give the rest of the framework named places to write:
header, main content, and status. The region objects themselves stay thin and
delegate actual rendering to the UI namespace.
"""

from typing import Any, Optional


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
        self.ui.layout.redraw_ui()

    def clear(self):
        self.content = None
        self.color = None
        self.ui.layout.trigger_redraw()
        self.ui.layout.redraw_ui()


class Header(Region):
    pass


class Panel:
    def __init__(self, name: str, ui: Any):
        self.name = name
        self.ui = ui
        self.buffer: list[dict[str, Any]] = []

    def print(self, *args, **kwargs):
        self.ui.layout.append_panel_output(self.name, *args, **kwargs)

    def stream(self, *args, **kwargs):
        return self.print(*args, **kwargs)


class MainContent:
    def __init__(self, ui: Any):
        self.ui = ui

    def print(self, *args, **kwargs):
        if self.ui.layout.split_active:
            self.ui.layout.left.print(*args, **kwargs)
        else:
            self.ui.print(*args, **kwargs)

    def stream(self, *args, **kwargs):
        return self.print(*args, **kwargs)


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
        self.ui.layout.redraw_ui()

    def clear(self):
        self.left = ""
        self.right = ""
        self.color = None
        self.ui.layout.trigger_redraw()
        self.ui.layout.redraw_ui()
