"""Renderer implementations for terminal output.

The renderer layer is where Klix decides how output actually reaches the
terminal. The rest of the framework talks in terms of semantic colors and
simple print operations; this file translates that into rich output or basic
fallback output depending on the environment.
"""

from rich.console import Console
from .theme import ThemeConfig


class BaseRenderer:
    def __init__(self, theme: ThemeConfig):
        self.theme = theme

    def print(self, text: str, color: str = None, bold: bool = False, dim: bool = False, italic: bool = False, end: str = "\n"):
        raise NotImplementedError()

    def clear(self):
        raise NotImplementedError()


# RichRenderer is the normal interactive path. It resolves semantic theme keys
# into real rich styles before printing.
class RichRenderer(BaseRenderer):
    def __init__(self, theme: ThemeConfig):
        super().__init__(theme)
        self.console = Console()

    def _resolve_color(self, color: str) -> str:
        if not color:
            return self.theme.text
        # Theme keys like "accent" or "error" are allowed anywhere a component
        # accepts a color value.
        if hasattr(self.theme, color):
            return getattr(self.theme, color)
        return color

    def print(self, text: str, color: str = None, bold: bool = False, dim: bool = False, italic: bool = False, end: str = "\n"):
        resolved_color = self._resolve_color(color)
        style_parts = []
        if resolved_color and resolved_color != "default":
            style_parts.append(resolved_color)
        if bold:
            style_parts.append("bold")
        if dim:
            style_parts.append("dim")
        if italic:
            style_parts.append("italic")
            
        style = " ".join(style_parts)
        if style:
            self.console.print(text, style=style, end=end)
        else:
            self.console.print(text, end=end)

    def clear(self):
        self.console.clear()


# Fallback mode intentionally does very little styling. Its job is not to be
# pretty, just to keep the framework usable when rich output is a bad fit.
class FallbackRenderer(BaseRenderer):
    def print(self, text: str, color: str = None, bold: bool = False, dim: bool = False, italic: bool = False, end: str = "\n"):
        print(text, end=end)

    def clear(self):
        print("\033[2J\033[H", end="")

class CIRenderer(FallbackRenderer):
    pass
