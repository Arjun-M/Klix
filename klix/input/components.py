"""Higher-level interactive input components.

This file turns the low-level input engine into reusable UI primitives exposed
as `session.ui.input.*`. Some components are simple prompt wrappers, while the
selector-style components use prompt_toolkit dialogs for richer interaction.
"""

from typing import Any, Callable, Optional, Sequence

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.history import DummyHistory
from prompt_toolkit.shortcuts.prompt import CompleteStyle
from prompt_toolkit.shortcuts import checkboxlist_dialog, radiolist_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import ValidationError, Validator

from ..errors import InputCancelledError
from .engine import InputEngine
from .modes import InputMode


# Fuzzy selector matching is kept local here because it is a UI concern rather
# than a router concern.
def _fuzzy_match(query: str, option: str) -> bool:
    query = query.lower()
    option = option.lower()
    if not query:
        return True

    pos = 0
    for char in query:
        pos = option.find(char, pos)
        if pos == -1:
            return False
        pos += 1
    return True


class UIInputNamespace:
    def __init__(self, engine: InputEngine, ui: Any):
        self.engine = engine
        self.ui = ui

    # Components resolve semantic theme keys through the active renderer so
    # input widgets respect the same palette as output widgets.
    def _resolve_color(self, color: Optional[str], fallback: str = "text") -> str:
        renderer = self.ui.renderer
        target = color or fallback
        if hasattr(renderer, "_resolve_color"):
            return renderer._resolve_color(target)
        return target

    def _dialog_style(self, accent: Optional[str] = None) -> Style:
        accent_color = self._resolve_color(accent, "accent")
        text_color = self._resolve_color(None, "text")
        muted_color = self._resolve_color("muted", "muted")
        border_color = self._resolve_color("border", "border")
        background_color = self.ui.renderer.theme.background or "default"

        return Style.from_dict(
            {
                "dialog": f"bg:{background_color} {text_color}",
                "dialog.body": f"bg:{background_color} {text_color}",
                "dialog frame.label": f"bold {accent_color}",
                "dialog shadow": f"bg:{background_color}",
                "button": text_color,
                "button.focused": f"bg:{accent_color} {background_color}",
                "radio": text_color,
                "radio-selected": f"bold {accent_color}",
                "checkbox": text_color,
                "checkbox-selected": f"bold {accent_color}",
                "dialog.body text-area": text_color,
                "dialog.body label": muted_color,
                "dialog.body frame.border": border_color,
            }
        )

    # Dialogs are async like the rest of Klix. CI mode short-circuits because
    # interactive dialogs do not make sense in a non-TTY pipeline.
    async def _run_dialog(self, dialog: Any) -> Any:
        if self.engine.is_ci:
            return None
        return await dialog.run_async()

    # Text input is the generic building block. Validation hooks are wrapped in
    # a prompt_toolkit validator so callers can provide lightweight business
    # rules without importing prompt_toolkit themselves.
    async def text(
        self,
        prompt: str,
        color: str = None,
        placeholder: str = "",
        default: str = "",
        validate: Optional[Callable[[str], Any]] = None,
    ) -> str:
        if self.engine.is_ci:
            self.ui.print(prompt, color=color or "accent", end=" ")
            return default

        validator = None
        if validate is not None:
            class _PromptValidator(Validator):
                def validate(self, document) -> None:
                    try:
                        result = validate(document.text)
                    except ValueError as exc:
                        raise ValidationError(message=str(exc)) from exc

                    if result is False:
                        raise ValidationError(message="Invalid input.")
                    if isinstance(result, str):
                        raise ValidationError(message=result)

            validator = _PromptValidator()

        self.engine.set_mode(InputMode.COMMAND)
        session = PromptSession(history=self.engine.history, completer=self.engine.completer)
        return await session.prompt_async(
            f"{prompt} ",
            default=default,
            placeholder=placeholder or None,
            validator=validator,
            validate_while_typing=False,
        )

    # Password prompts use a throwaway history object so secrets do not leak
    # into interactive history navigation.
    async def secret(self, prompt: str) -> str:
        if self.engine.is_ci:
            self.ui.print(prompt, color="accent", end=" ")
            return ""

        self.engine.set_mode(InputMode.PASSWORD)
        session = PromptSession(history=DummyHistory())
        return await session.prompt_async(f"{prompt} ", is_password=True)

    # Confirm is kept explicit instead of relying on the engine's boolean mode
    # so the empty-input default path remains under this component's control.
    async def confirm(self, question: str, default: bool = True) -> bool:
        if self.engine.is_ci:
            return default

        self.engine.set_mode(InputMode.COMMAND)
        default_suffix = "Y/n" if default else "y/N"
        session = PromptSession(history=DummyHistory())

        while True:
            response = await session.prompt_async(f"{question} [{default_suffix}] ")
            response = response.strip().lower()
            if response == "":
                return default
            if response in {"y", "yes", "true", "1"}:
                return True
            if response in {"n", "no", "false", "0"}:
                return False
            self.ui.print("Enter y or n.", color="warning")

    # Select and multiselect lean on prompt_toolkit's built-in dialogs. Klix
    # mainly supplies theme integration and cancellation behavior.
    async def select(
        self,
        options: Sequence[str],
        label: str = "",
        cursor_color: str = None,
        default: Optional[str] = None,
    ) -> str:
        if not options:
            raise ValueError("select() requires at least one option.")
        if self.engine.is_ci:
            return default or options[0]

        self.engine.set_mode(InputMode.SELECT)
        values = [(option, option) for option in options]
        dialog = radiolist_dialog(
            title=label or "Select",
            text="Use arrow keys to choose an option.",
            values=values,
            default=default or options[0],
            style=self._dialog_style(cursor_color),
        )
        result = await self._run_dialog(dialog)
        if result is None:
            raise InputCancelledError("Selection cancelled.")
        return result

    async def multiselect(
        self,
        options: Sequence[str],
        label: str = "",
        checked_color: str = None,
        default: Optional[Sequence[str]] = None,
    ) -> list[str]:
        if self.engine.is_ci:
            return list(default or [])

        self.engine.set_mode(InputMode.SELECT)
        values = [(option, option) for option in options]
        dialog = checkboxlist_dialog(
            title=label or "Select multiple",
            text="Use arrow keys, Space to toggle, Enter to confirm.",
            values=values,
            default_values=list(default or []),
            style=self._dialog_style(checked_color),
        )
        result = await self._run_dialog(dialog)
        if result is None:
            raise InputCancelledError("Multi-select cancelled.")
        return list(result)

    # Fuzzy search uses a normal prompt with fuzzy completion rather than a
    # separate dialog so typing stays fast and lightweight.
    async def fuzzy(
        self,
        options: Sequence[str],
        label: str = "",
        default: str = "",
    ) -> str:
        if not options:
            raise ValueError("fuzzy() requires at least one option.")
        if self.engine.is_ci:
            return default or options[0]

        self.engine.set_mode(InputMode.SEARCH)
        completer = FuzzyWordCompleter(list(options), WORD=True)
        session = PromptSession(history=DummyHistory(), completer=completer)

        def _validator() -> Validator:
            class _FuzzyValidator(Validator):
                def validate(self, document) -> None:
                    text = document.text.strip()
                    if not text:
                        raise ValidationError(message="Type to search.")
                    if any(_fuzzy_match(text, option) for option in options):
                        return
                    raise ValidationError(message="No matching option.")

            return _FuzzyValidator()

        text = await session.prompt_async(
            f"{label or 'Search'} ",
            default=default,
            placeholder="Type to filter options",
            complete_style=CompleteStyle.COLUMN,
            complete_while_typing=True,
            validator=_validator(),
            validate_while_typing=False,
        )
        text = text.strip()
        if text in options:
            return text
        for option in options:
            if _fuzzy_match(text, option):
                return option
        raise InputCancelledError("No option selected.")

    # Number input reuses the text component so validation and prompting behave
    # consistently across field types.
    async def number(self, prompt: str, min_val: float = None, max_val: float = None) -> float:
        def _validate(value: str) -> bool:
            try:
                number = float(value)
            except ValueError as exc:
                raise ValueError("Enter a numeric value.") from exc

            if min_val is not None and number < min_val:
                raise ValueError(f"Value must be >= {min_val}.")
            if max_val is not None and number > max_val:
                raise ValueError(f"Value must be <= {max_val}.")
            return True

        result = await self.text(prompt, validate=_validate)
        return float(result)

    # Toggle is just a constrained select; keeping it here gives apps a small
    # semantic API instead of repeating string comparisons.
    async def toggle(self, label: str = "Toggle", default: bool = False) -> bool:
        selection = await self.select(
            options=["On", "Off"],
            label=label,
            default="On" if default else "Off",
            cursor_color="accent",
        )
        return selection == "On"
