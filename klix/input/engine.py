"""Low-level prompt_toolkit input engine.

The engine owns the raw prompt session and mode-aware prompting behavior.
Higher-level input components build on top of this file rather than talking to
prompt_toolkit directly everywhere.
"""

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
import inspect
import sys
from typing import Any, Optional

from .history import SessionHistory
from .modes import InputMode
from ..output.theme import ThemeConfig


class InputEngine:
    def __init__(
        self,
        completer: Optional[Any] = None,
        is_ci: bool = False,
        clear_input_on_submit: bool = False,
        session_history: Optional[list[str]] = None,
        max_history_size: Optional[int] = None,
        theme: Optional[ThemeConfig] = None,
    ):
        self.mode = InputMode.COMMAND
        self.history = SessionHistory(session_history, max_size=max_history_size)
        self.completer = completer
        self.is_ci = is_ci
        self.clear_input_on_submit = clear_input_on_submit
        self.theme = theme or ThemeConfig()
        if not self.is_ci:
            self.pt_session = PromptSession(history=self.history, completer=self.completer)

    def set_mode(self, mode: InputMode):
        self.mode = mode

    def _record_history(self, value: str) -> None:
        if self.mode == InputMode.COMMAND:
            self.history.append_string(value)

    def _build_key_bindings(self) -> KeyBindings:
        bindings = KeyBindings()

        # Ctrl+L is handled globally here so every prompt gets the same screen
        # clearing behavior without each component re-registering it.
        @bindings.add('c-l')
        def _(event):
            event.app.renderer.clear()

        if self.mode == InputMode.MULTILINE:
            # Terminals generally don't expose a distinct Shift+Enter event to
            # prompt_toolkit. Klix uses Escape+Enter as the portable newline
            # path and also accepts Control-J for terminals that emit LF.
            @bindings.add('escape', 'enter')
            def _(event):
                event.app.current_buffer.insert_text('\n')

            @bindings.add('c-j')
            def _(event):
                event.app.current_buffer.insert_text('\n')

            @bindings.add('enter')
            def _(event):
                event.app.current_buffer.validate_and_handle()

        return bindings

    def build_prompt_style(self) -> Optional[Style]:
        input_background = self.theme.input_background
        if not input_background:
            return None

        input_text_color = self.theme.input_text_color or self.theme.text or "default"
        selected_background = self.theme.border or input_background
        completion_background = self.theme.background or input_background

        return Style.from_dict(
            {
                "": f"bg:{input_background} {input_text_color}",
                "prompt": input_text_color,
                "bottom-toolbar": f"bg:{input_background} {input_text_color}",
                "bottom-toolbar.text": input_text_color,
                "completion-menu": f"bg:{completion_background} {input_text_color}",
                "completion-menu.completion.current": f"bg:{input_background} {input_text_color} reverse",
                "completion-menu.meta.completion": f"bg:{completion_background} {input_text_color}",
                "completion-menu.meta.completion.current": f"bg:{input_background} {input_text_color}",
                "selected": f"bg:{selected_background} {input_text_color}",
            }
        )

    async def _prompt_session_async(self, session: PromptSession, message: str, **kwargs: Any) -> Any:
        supported = inspect.signature(session.prompt_async).parameters
        if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in supported.values()):
            return await session.prompt_async(message, **kwargs)
        filtered_kwargs = {key: value for key, value in kwargs.items() if key in supported}
        return await session.prompt_async(message, **filtered_kwargs)

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

            result = line.rstrip('\n')
            self._record_history(result)
            return result

        is_password = (self.mode == InputMode.PASSWORD)
        multiline = (self.mode == InputMode.MULTILINE)
        completer = self.completer if self.mode == InputMode.COMMAND else None

        try:
            result = await self._prompt_session_async(
                self.pt_session,
                message,
                is_password=is_password,
                multiline=multiline,
                key_bindings=self._build_key_bindings(),
                completer=completer,
                style=self.build_prompt_style(),
                erase_when_done=self.clear_input_on_submit,
            )
        except EOFError:
            # Ctrl+D
            return "/exit"

        if self.mode == InputMode.CONFIRM:
            # Confirm mode is intentionally opinionated: callers get a boolean
            # rather than raw text when they opt into this mode.
            return result.strip().lower() in ('y', 'yes', 'true', '1')

        return result
