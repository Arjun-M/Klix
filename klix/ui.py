"""Session-level UI namespace.

`session.ui` is the main convenience surface app code touches. This file wires
the renderer, input widgets, output widgets, layout engine, and cursor helpers
into one object so handlers do not need to know where each subsystem lives.
"""

import sys
from .output.renderer import BaseRenderer
from .output.widgets import OutputWidgets
from .input.components import UIInputNamespace
from .input.engine import InputEngine
from .layout.engine import LayoutEngine
from .layout.cursor import CursorControl


class UINamespace:
    def __init__(self, renderer: BaseRenderer, engine: InputEngine):
        self.renderer = renderer
        self.output = OutputWidgets(renderer, self)
        self.input = UIInputNamespace(engine, self)
        self.layout = LayoutEngine(self)
        self.cursor = CursorControl()

    def _print_direct(
        self,
        text: str,
        color: str = None,
        bold: bool = False,
        dim: bool = False,
        italic: bool = False,
        end: str = "\n",
    ):
        self.renderer.print(text, color=color, bold=bold, dim=dim, italic=italic, end=end)

    def _clear_direct(self):
        self.renderer.clear()

    # This is the narrow print surface the rest of Klix uses. Rich-specific
    # concerns stay down in the renderer layer.
    def print(
        self,
        text: str,
        color: str = None,
        bold: bool = False,
        dim: bool = False,
        italic: bool = False,
        end: str = "\n",
    ):
        if self.layout.should_capture_output():
            self.layout.append_main_output(
                text,
                color=color,
                bold=bold,
                dim=dim,
                italic=italic,
                end=end,
            )
            return
        self._print_direct(text, color=color, bold=bold, dim=dim, italic=italic, end=end)

    def clear(self):
        if self.layout.has_sticky_header():
            self.layout.clear_main_output()
            self.layout.redraw_ui()
            return
        self._clear_direct()

    def newline(self):
        self.print("")

    def bell(self):
        sys.stdout.write("\a")
        sys.stdout.flush()

    def move_cursor(self, x: int, y: int):
        self.cursor.move_to(x, y)

    # Redraws can temporarily move the prompt off where prompt_toolkit expects
    # it. This helper gives the layout engine one place to restore that state.
    def move_cursor_to_input_line(self):
        sys.stdout.write("\n")
        sys.stdout.flush()

    # Streaming is implemented as repeated prints so output widgets and app code
    # can share the same renderer path.
    async def stream(self, generator, color: str = None, end: str = "\n"):
        async for chunk in generator:
            self.print(chunk, color=color, end="")
        self.print("", end=end)
