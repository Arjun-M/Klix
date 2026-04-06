"""Low-level prompt_toolkit input engine.

The engine owns the raw prompt session and mode-aware prompting behavior.
Higher-level input components build on top of this file rather than talking to
prompt_toolkit directly everywhere.
"""

from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
import asyncio
import sys
from typing import Optional, Any

from .modes import InputMode


class InputEngine:
    def __init__(self, completer: Optional[Any] = None, is_ci: bool = False):
        self.mode = InputMode.COMMAND
        self.history = InMemoryHistory()
        self.completer = completer
        self.is_ci = is_ci
        if not self.is_ci:
            self.pt_session = PromptSession(history=self.history, completer=self.completer)
        
    def set_mode(self, mode: InputMode):
        self.mode = mode

    # This is the single prompt boundary used by the rest of the framework.
    # CI mode drops back to plain stdin/stdout so tests and pipes are stable.
    async def prompt_async(self, message: str = "> ", default: Any = "") -> Any:
        """Asynchronously prompt for input."""
        if self.is_ci:
            if message:
                print(message, end="", flush=True)

            line = sys.stdin.readline()
            if line == "":
                return "/exit"
            return line.rstrip("\n")

        is_password = (self.mode == InputMode.PASSWORD)
        multiline = (self.mode == InputMode.MULTILINE)
        
        bindings = KeyBindings()

        # Ctrl+L is handled globally here so every prompt gets the same screen
        # clearing behavior without each component re-registering it.
        @bindings.add('c-l')
        def _(event):
            event.app.renderer.clear()

        # Multiline mode keeps Enter as submit but still offers an escape hatch
        # for inserting newlines without leaving prompt_toolkit.
        if self.mode == InputMode.MULTILINE:
            @bindings.add('escape', 'enter')
            def _(event):
                event.app.current_buffer.insert_text('\n')
            
            @bindings.add('enter')
            def _(event):
                event.app.current_buffer.validate_and_handle()

        completer = self.completer if self.mode == InputMode.COMMAND else None

        try:
            result = await self.pt_session.prompt_async(
                message,
                is_password=is_password,
                multiline=multiline,
                key_bindings=bindings,
                completer=completer
            )
        except EOFError:
            # Ctrl+D
            return "/exit"

        if self.mode == InputMode.CONFIRM:
            # Confirm mode is intentionally opinionated: callers get a boolean
            # rather than raw text when they opt into this mode.
            return result.strip().lower() in ('y', 'yes', 'true', '1')

        return result
