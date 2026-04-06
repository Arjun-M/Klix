"""Lightweight event bus used by the App lifecycle.

Klix events are deliberately simple: named listeners registered in order and
emitted sequentially. This keeps lifecycle hooks easy to reason about while
still supporting both sync and async handlers.
"""

from typing import Dict, List, Callable
import inspect


class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    # Registration order matters because listeners are run in the same order
    # they are added. That makes lifecycle behavior predictable.
    def on(self, event_name: str):
        def decorator(func: Callable):
            if event_name not in self._listeners:
                self._listeners[event_name] = []
            self._listeners[event_name].append(func)
            return func
        return decorator

    async def emit(self, event_name: str, *args, **kwargs):
        """Emit an event, calling all registered handlers in order."""
        if event_name not in self._listeners:
            return
            
        # Sync and async listeners can coexist on the same event without the
        # caller having to care which style was used.
        for handler in self._listeners[event_name]:
            if inspect.iscoroutinefunction(handler):
                await handler(*args, **kwargs)
            else:
                handler(*args, **kwargs)
