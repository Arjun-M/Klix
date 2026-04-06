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
from .layout.cursor import CursorControl # Import CursorControl


class UINamespace:
    def __init__(self, renderer: BaseRenderer, engine: InputEngine):
        self.renderer = renderer
        self.output = OutputWidgets(renderer, self)
        self.input = UIInputNamespace(engine, self)
        self.layout = LayoutEngine(self)
        self.cursor = CursorControl() # Instantiate CursorControl

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
        self.renderer.print(text, color=color, bold=bold, dim=dim, italic=italic, end=end)

    def clear(self):
        self.renderer.clear()

    def newline(self):
        self.print("")

    def bell(self):
        sys.stdout.write("\a")
        sys.stdout.flush()

    def move_cursor(self, x: int, y: int):
        self.cursor.move_to(x, y) # Delegate to CursorControl

    # Redraws can temporarily move the prompt off where prompt_toolkit expects
    # it. This helper gives the layout engine one place to restore that state.
    def move_cursor_to_input_line(self):
        # This is a placeholder for prompt_toolkit to re-render its input line correctly.
        # It typically involves printing enough newlines to push the cursor below any rendered content.
        # Actual implementation will depend on prompt_toolkit's internal layout management.
        sys.stdout.write("\n") # Just move to next line for now.
        sys.stdout.flush()

    # Streaming is implemented as repeated prints so output widgets and app code
    # can share the same renderer path.
    async def stream(self, generator, color: str = None, end: str = "\n"):
        async for chunk in generator:
            self.renderer.print(chunk, color=color, end="")
        self.renderer.print("", end=end)
