"""Simple region-based layout engine.

This is the glue between high-level UI regions and the renderer. It tracks
header/status state and performs coarse redraws when those regions change.
"""

from typing import Any, List
from .regions import Header, MainContent, StatusBar, Panel
try:
    from rich.columns import Columns
    from rich.panel import Panel as RichPanel
    from rich.text import Text
except ImportError:
    Columns = None
    RichPanel = None
    Text = None


class LayoutEngine:
    def __init__(self, ui: Any):
        self.ui = ui
        self.header = Header("HEADER", ui)
        self.main = MainContent(ui)
        self.status = StatusBar(ui)
        self.left = Panel("LEFT", ui)
        self.right = Panel("RIGHT", ui)
        self._needs_redraw = False
        self._main_buffer: List[dict[str, Any]] = []
        self._split_active = False
        self._split_ratio = 0.5
        self._split_direction = "horizontal"
        self._is_redrawing = False

    @property
    def split_active(self) -> bool:
        return self._split_active

    def has_sticky_header(self) -> bool:
        return bool(self.header.content)

    def should_capture_output(self) -> bool:
        return self.has_sticky_header() and not self._is_redrawing

    # Region objects call this when they change. The redraw is deferred so the
    # caller does not need to think about the mechanics immediately.
    def trigger_redraw(self):
        """Signals that the UI needs a redraw."""
        self._needs_redraw = True

    def append_main_output(
        self,
        text: str,
        color: str = None,
        bold: bool = False,
        dim: bool = False,
        italic: bool = False,
        end: str = "\n",
    ):
        self._main_buffer.append(
            {
                "text": text,
                "color": color,
                "bold": bold,
                "dim": dim,
                "italic": italic,
                "end": end,
            }
        )
        self.trigger_redraw()
        self.redraw_ui()

    def clear_main_output(self):
        self._main_buffer.clear()
        self.trigger_redraw()

    def split(self, *, direction: str = "horizontal", ratio: float = 0.5):
        if direction not in {"horizontal", "vertical"}:
            raise ValueError("unsupported split direction")
        self._split_active = True
        self._split_direction = direction
        self._split_ratio = max(0.0, min(1.0, ratio))
        self.trigger_redraw()

    def disable_split(self):
        self._split_active = False
        self._split_ratio = 0.5
        self._split_direction = "horizontal"
        self.trigger_redraw()

    def append_panel_output(
        self,
        panel: str,
        text: str,
        color: str = None,
        bold: bool = False,
        dim: bool = False,
        italic: bool = False,
        end: str = "\n",
    ):
        target = self.left if panel == "LEFT" else self.right
        target.buffer.append(
            {
                "text": text,
                "color": color,
                "bold": bold,
                "dim": dim,
                "italic": italic,
                "end": end,
            }
        )
        self.trigger_redraw()
        self.redraw_ui()

    def _render_panel_text(self, panel: Panel) -> "Text":
        if Text is None:
            return None
        rendered = Text()
        for entry in panel.buffer:
            style = entry.get("color")
            rendered.append(entry.get("text", ""), style=style)
            rendered.append(entry.get("end", ""))
        if not rendered.plain:
            rendered.append("\n")
        return rendered

    # This redraw strategy is intentionally blunt. It is not trying to be a
    # full-screen terminal framework; it just keeps static regions coherent.
    def redraw_ui(self):
        """Performs a full redraw of the sticky layout regions when needed."""
        if not self._needs_redraw:
            return

        self._needs_redraw = False
        self._is_redrawing = True
        try:
            self.ui._clear_direct()
            self.ui.move_cursor(0, 0)

            console_width = self.ui.renderer.console.size.width if hasattr(self.ui.renderer, "console") else 80

            if self.header.content:
                self.ui._print_direct(self.header.content, color=self.header.color)
                if hasattr(self.ui.renderer, "console"):
                    self.ui._print_direct("-" * console_width, color=self.header.color)

            if not self._split_active:
                for entry in self._main_buffer:
                    self.ui._print_direct(**entry)
            else:
                if hasattr(self.ui.renderer, "console") and Columns and RichPanel and Text:
                    console_width = self.ui.renderer.console.size.width
                    left_width = max(10, int(console_width * self._split_ratio))
                    right_width = max(10, console_width - left_width - 1)
                    left_render = self._render_panel_text(self.left) or Text()
                    right_render = self._render_panel_text(self.right) or Text()
                    panels = [
                        RichPanel(
                            left_render,
                            title="Left",
                            border_style=self.ui.renderer.theme.border or "border",
                            width=left_width,
                        ),
                        RichPanel(
                            right_render,
                            title="Right",
                            border_style=self.ui.renderer.theme.border or "border",
                            width=right_width,
                        ),
                    ]
                    self.ui.renderer.console.print(
                        Columns(panels, expand=True, padding=(0, 1), equal=False, column_first=False),
                    )
                else:
                    for entry in self.left.buffer:
                        self.ui._print_direct(**entry)
                    self.ui._print_direct("---------------- split ----------------")
                    for entry in self.right.buffer:
                        self.ui._print_direct(**entry)

            if self.status.left or self.status.right:
                console_width = self.ui.renderer.console.size.width if hasattr(self.ui.renderer, "console") else 80
                status_line = f"{self.status.left:<{console_width // 2}}{self.status.right:>{console_width // 2}}"
                self.ui._print_direct(status_line, color=self.status.color)

            if self.has_sticky_header():
                self.ui.move_cursor_to_input_line()
        finally:
            self._is_redrawing = False
