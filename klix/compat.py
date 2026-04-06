import os
import sys
from .output.renderer import BaseRenderer, RichRenderer, FallbackRenderer, CIRenderer
from .output.theme import ThemeConfig

def get_renderer(theme: ThemeConfig) -> BaseRenderer:
    """Detect terminal capabilities and return the appropriate renderer."""
    if os.environ.get("CI") == "true" or not sys.stdout.isatty():
        return CIRenderer(theme)
    if os.environ.get("TERM") == "dumb":
        return FallbackRenderer(theme)
    return RichRenderer(theme)