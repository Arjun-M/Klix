"""Reusable rich-oriented output widgets.

This file implements the higher-level pieces exposed as `session.ui.output.*`.
Most widgets render rich objects when possible and fall back to plain text when
the active renderer does not have a rich console behind it.
"""

import difflib
import json as json_lib
from typing import Any, Optional, Sequence

from rich.box import ROUNDED
from rich.console import Group, RenderableType
from rich.json import JSON
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from .renderer import BaseRenderer


# Spinner/progress handles are stateful objects because callers usually want to
# start something now and update it later from another part of the flow.
class SpinnerHandle:
    def __init__(self, console: Any, message: str, style: str, color: str):
        self._console = console
        self._message = message
        self._style = style
        self._color = color
        self._status = None
        self._started = False

    def start(self) -> None:
        if self._console is None or self._started:
            return
        self._status = self._console.status(self._message, spinner=self._style, spinner_style=self._color)
        self._status.start()
        self._started = True

    def stop(self) -> None:
        if self._status is not None:
            self._status.stop()
        self._status = None
        self._started = False

    def update(self, message: str) -> None:
        self._message = message
        if self._status is not None:
            self._status.update(message)


class FallbackSpinnerHandle:
    def __init__(self, renderer: BaseRenderer, message: str, color: str):
        self._renderer = renderer
        self._message = message
        self._color = color
        self._started = False

    def start(self) -> None:
        if not self._started:
            self._renderer.print(self._message, color=self._color)
            self._started = True

    def stop(self) -> None:
        self._started = False

    def update(self, message: str) -> None:
        self._message = message
        if self._started:
            self._renderer.print(message, color=self._color)


class ProgressHandle:
    def __init__(self, console: Any, total: int, label: str, color: str):
        self._console = console
        self._label = label
        self._color = color
        self._progress = None
        self._task_id = None
        self._started = False
        self._total = total

    def start(self) -> None:
        if self._console is None or self._started:
            return
        self._progress = Progress(
            SpinnerColumn(style=self._color),
            TextColumn(f"[{self._color}]{self._label}"),
            BarColumn(bar_width=None),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self._console,
            transient=False,
        )
        self._task_id = self._progress.add_task(self._label, total=self._total)
        self._progress.start()
        self._started = True

    def stop(self) -> None:
        if self._progress is not None:
            self._progress.stop()
        self._progress = None
        self._task_id = None
        self._started = False

    def update(self, advance: int = 0, completed: Optional[int] = None, total: Optional[int] = None) -> None:
        if self._progress is None or self._task_id is None:
            return
        if total is not None:
            self._total = total
        self._progress.update(self._task_id, advance=advance, completed=completed, total=total)


class FallbackProgressHandle:
    def __init__(self, renderer: BaseRenderer, total: int, label: str, color: str):
        self._renderer = renderer
        self._label = label
        self._color = color
        self._total = max(total, 1)
        self._current = 0

    def start(self) -> None:
        self._renderer.print(f"{self._label}: 0/{self._total}", color=self._color)

    def stop(self) -> None:
        pass

    def update(self, advance: int = 0, completed: Optional[int] = None, total: Optional[int] = None) -> None:
        if total is not None:
            self._total = max(total, 1)
        if completed is not None:
            self._current = completed
        else:
            self._current += advance
        self._renderer.print(f"{self._label}: {self._current}/{self._total}", color=self._color)


class OutputWidgets:
    def __init__(self, renderer: BaseRenderer, ui: Any = None):
        self.renderer = renderer
        self.ui = ui

    # Widget code accepts semantic color names and resolves them here once so
    # each widget does not repeat renderer-specific lookup logic.
    def _resolve(self, color: Optional[str], fallback: str = "text") -> str:
        target = color or fallback
        if hasattr(self.renderer, "_resolve_color"):
            resolved = self.renderer._resolve_color(target)
            return resolved if resolved else "default"
        return target or "default"

    def _renderable_title(self, title: Optional[str], color: Optional[str]) -> Optional[Text]:
        if title is None:
            return None
        return Text(title, style=self._resolve(color, "accent"))

    def _print_renderable(self, renderable: RenderableType) -> None:
        if hasattr(self.renderer, "console"):
            self.renderer.console.print(renderable)
        else:
            self.renderer.print(str(renderable))

    # Tables stay intentionally lightweight: headers, rows, and optional column
    # alignment. Anything more specialized should be built by app code.
    def table(
        self,
        headers: Sequence[str],
        rows: Sequence[Sequence[Any]],
        header_color: str = None,
        border_color: str = None,
        alignments: Optional[Sequence[str]] = None,
    ) -> None:
        if hasattr(self.renderer, "console"):
            table = Table(
                show_header=True,
                header_style=self._resolve(header_color, "accent"),
                border_style=self._resolve(border_color, "border"),
                box=ROUNDED,
            )
            alignments = list(alignments or [])
            for index, header in enumerate(headers):
                justify = alignments[index] if index < len(alignments) else "left"
                table.add_column(str(header), justify=justify)
            for row in rows:
                table.add_row(*[str(item) for item in row])
            self._print_renderable(table)
            return

        self.renderer.print(" | ".join(str(header) for header in headers), color=header_color)
        self.renderer.print("-" * 40, color=border_color)
        for row in rows:
            self.renderer.print(" | ".join(str(item) for item in row))

    # `panel` is the core bordered container primitive. `card` is just a more
    # semantic alias for apps that prefer that wording.
    def panel(
        self,
        content: Any,
        title: str = None,
        border_color: str = None,
        title_color: str = None,
    ) -> None:
        if hasattr(self.renderer, "console"):
            renderable = Panel(
                content,
                title=self._renderable_title(title, title_color or border_color),
                border_style=self._resolve(border_color, "border"),
                box=ROUNDED,
            )
            self._print_renderable(renderable)
            return

        if title:
            self.renderer.print(f"[{title}]", color=title_color or border_color)
        self.renderer.print(str(content))

    def card(
        self,
        content: Any,
        title: str = None,
        border_color: str = None,
        title_color: str = None,
    ) -> None:
        self.panel(content=content, title=title, border_color=border_color, title_color=title_color)

    def markdown(self, text: str) -> None:
        if hasattr(self.renderer, "console"):
            self._print_renderable(Markdown(text))
        else:
            self.renderer.print(text)

    def code(self, text: str, lang: str = "python", theme: str = "monokai") -> None:
        if hasattr(self.renderer, "console"):
            self._print_renderable(Syntax(text, lang, theme=theme, line_numbers=True))
        else:
            self.renderer.print(text)

    def json(self, data: Any, indent: int = 2) -> None:
        if hasattr(self.renderer, "console"):
            self._print_renderable(JSON(json_lib.dumps(data, indent=indent)))
        else:
            self.renderer.print(json_lib.dumps(data, indent=indent))

    def tree(self, data: dict, color: str = None) -> None:
        if hasattr(self.renderer, "console"):
            # Tree building is recursive because rich's Tree API is itself
            # recursive; this keeps nested dicts and lists readable with little
            # ceremony from the caller.
            def _build_tree(node: Any, tree_node: Tree) -> None:
                if isinstance(node, dict):
                    for key, value in node.items():
                        child = tree_node.add(str(key))
                        _build_tree(value, child)
                elif isinstance(node, list):
                    for item in node:
                        tree_node.add(str(item))
                elif node is not None:
                    tree_node.add(str(node))

            root_key = list(data.keys())[0] if data else "root"
            tree = Tree(str(root_key), style=self._resolve(color, "accent"))
            if data:
                payload = data[root_key] if len(data) == 1 else data
                _build_tree(payload, tree)
            self._print_renderable(tree)
            return

        self.renderer.print(json_lib.dumps(data, indent=2), color=color)

    # Diff output is line-oriented and uses semantic success/error/warning
    # colors rather than trying to emulate a full git diff parser.
    def diff(self, old: str, new: str) -> None:
        diff_lines = list(difflib.ndiff(old.splitlines(), new.splitlines()))
        for line in diff_lines:
            if line.startswith("+ "):
                self.renderer.print(line, color="success")
            elif line.startswith("- "):
                self.renderer.print(line, color="error")
            elif line.startswith("? "):
                self.renderer.print(line, color="warning")
            else:
                self.renderer.print(line)

    def spinner(self, message: str, style: str = "dots", color: str = None):
        resolved = self._resolve(color, "accent")
        console = getattr(self.renderer, "console", None)
        if console is not None:
            return SpinnerHandle(console, message, style, resolved)
        return FallbackSpinnerHandle(self.renderer, message, resolved)

    def progress(self, total: int, label: str = "", color: str = None, width: int = None):
        resolved = self._resolve(color, "accent")
        console = getattr(self.renderer, "console", None)
        if console is not None:
            return ProgressHandle(console, total, label or "Progress", resolved)
        return FallbackProgressHandle(self.renderer, total, label or "Progress", resolved)

    def group(self, *renderables: Any) -> None:
        if hasattr(self.renderer, "console"):
            self._print_renderable(Group(*renderables))
        else:
            for renderable in renderables:
                self.renderer.print(str(renderable))
