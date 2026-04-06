"""Theme model shared by renderers and widgets.

ThemeConfig keeps the styling surface intentionally small and semantic so apps
can talk about "accent" or "warning" rather than threading raw ANSI details
through every component call.
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class ThemeConfig:
    accent: Optional[str] = "#00D4FF"
    background: Optional[str] = "default"
    text: Optional[str] = "#F9FAFB"
    muted: Optional[str] = "#6B7280"
    info: Optional[str] = "#3B82F6"
    border: Optional[str] = "#374151"
    cursor: Optional[str] = "#7C3AED"
    success: Optional[str] = "#22C55E"
    warning: Optional[str] = "#F59E0B"
    error: Optional[str] = "#EF4444"
