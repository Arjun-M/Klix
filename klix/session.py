"""Per-session state and metadata primitives.

Klix treats every terminal instance as an isolated session. This file defines
the small objects that represent that runtime boundary: typed state, terminal
metadata, and background task ownership.
"""

import uuid
import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


# Session state is intentionally lightweight. Apps are expected to subclass it
# rather than mutate unstructured globals.
class SessionState:
    """Base class for typed session state."""
    pass


# Metadata is captured once at session startup and then treated as read-mostly
# context for handlers and middleware.
@dataclass
class TerminalMetadata:
    env: Dict[str, str] = field(default_factory=dict)
    width: int = 0
    height: int = 0
    start_time: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    term_program: Optional[str] = None
    interactive: bool = False


# Session is the object passed through most of the framework. It holds user
# state plus the runtime handles that are attached after startup.
class Session:
    def __init__(
        self,
        id: str | None = None,
        state: SessionState | None = None,
        metadata: TerminalMetadata | None = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.state = state or SessionState()
        
        # Placeholders for future subsystems
        self.ui = None
        self.input_engine = None
        self.history: list[str] = []
        self.metadata = metadata or TerminalMetadata()
        self._tasks: set[asyncio.Task] = set()

    # Background tasks are tracked so the app can wait on or clean them up when
    # the session exits.
    def create_task(self, coro) -> asyncio.Task:
        """Schedule a background task within the session."""
        task = asyncio.create_task(coro)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
        return task
