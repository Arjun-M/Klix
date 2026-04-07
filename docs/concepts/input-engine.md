# Input Engine

The input engine is Klix's thin wrapper around `prompt_toolkit`. It provides the prompt session, input modes, key bindings, and CI-safe fallback behavior.

See also:

- [UI Namespace](ui.md)
- [Input Modes](../guides/input-modes.md)
- [Input Components](../components/input.md)

## Why It Exists

Klix needs one place to own terminal input behavior so that:

- prompt history is consistent
- key bindings are centralized
- modes can influence prompt behavior
- CI and pipe mode can bypass interactive UI cleanly

Without that layer, every input component would need to reinvent prompt setup.

## What The Engine Handles

Current responsibilities:

- `PromptSession` setup
- session-backed command history
- current `InputMode`
- `Ctrl+L` binding
- multiline bindings
- password mode flagging
- optional clear-after-submit behavior
- optional themed prompt styling
- CI/non-TTY fallback via `stdin.readline()`

## CI And Non-Interactive Behavior

When Klix selects `CIRenderer`, the input engine avoids interactive prompt_toolkit use and reads lines from stdin instead.

That is why tests can do things like:

```bash
printf '/hello hi\n/exit\n' | python main.py
```

This is great for automation, but it also means some richer widgets are effectively interactive-only. See [Input Components](../components/input.md).

## Modes

The engine currently understands:

- `COMMAND`
- `MULTILINE`
- `SELECT`
- `SEARCH`
- `CONFIRM`
- `PASSWORD`
- `INTERRUPT`

In the current implementation, not every mode changes low-level prompt behavior equally. Some modes are primarily semantic signals used by higher-level components.

Examples:

- `PASSWORD` changes prompt masking
- `MULTILINE` changes Enter behavior
- `COMMAND` mode participates in session history navigation
- selector-style inputs are implemented through prompt_toolkit dialogs in `session.ui.input`, not directly through `prompt_async()`

## Realistic Example

```python
@app.command("/notes", help="Capture a multiline note")
async def notes(session: klix.Session):
    session.input_engine.set_mode(klix.InputMode.MULTILINE)
    text = await session.input_engine.prompt_async("Note > ")
    session.input_engine.set_mode(klix.InputMode.COMMAND)
    session.ui.output.panel(text, title="Captured Note", border_color="accent")
```

## Key Bindings

Current built-ins:

- `Ctrl+L` clears the screen
- Up/Down navigate session history through prompt_toolkit
- in multiline mode:
  - `Escape` + `Enter` inserts a newline
  - `Ctrl+J` inserts a newline in terminals that emit LF
  - `Enter` submits

When `AppConfig(clear_input_on_submit=True)` is enabled, the active prompt line is also erased after submit.

If `ThemeConfig(input_background=...)` is set, prompt_toolkit applies a themed input bar background in interactive terminals.

## Pitfalls

### Assuming every input component goes through `prompt_async()`

Simple prompts do. Richer selectors often build their own prompt_toolkit sessions or dialogs on top of the same engine-level context.

### Forgetting to reset mode

If you manually change modes in custom flows, return to `COMMAND` when you are done.

### Expecting rich dialogs in CI

CI fallback is intentionally plain.
