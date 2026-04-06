# API Reference

This page summarizes the public API that Klix exports from `klix.__init__`.

For conceptual explanations, start with [Architecture](../concepts/architecture.md). For usage-oriented walkthroughs, see the pages under [Guides](../getting-started.md).

## Core Types

### `App`

The main framework entry point.

Use it to:

- register commands
- register middleware
- register lifecycle event handlers
- configure theme and persistence
- start the runtime loop

Common methods and decorators:

- `command(...)`
- `middleware(...)`
- `on(...)`
- `add_completer(...)`
- `generate_help()`
- `run()`

See [App](../concepts/app.md).

### `AppConfig`

Dataclass carrying high-level app configuration fields such as:

- `name`
- `version`
- `description`
- `theme`
- `persist_session`
- `session_id`
- `state_schema`

See [Reference: Config](config.md).

### `Session`

The per-run execution context.

Important attributes:

- `id`
- `state`
- `metadata`
- `ui`
- `input_engine`
- `history`

Important method:

- `create_task(coro)`

See [Session](../concepts/session.md).

### `SessionState`

Base dataclass-like marker used for typed session state. Extend it with your own dataclass model.

### `TerminalMetadata`

Structured snapshot of terminal-related metadata created when the session starts.

Fields include:

- `platform`
- `python_version`
- `terminal`
- `terminal_size`
- `is_tty`
- `cwd`

## Commands And Routing

### `Command`

Registration-time container for:

- command name
- handler
- help text
- aliases
- optional argument schema

### `ParsedCommand`

Result of routing and argument validation.

Fields:

- `name`
- `args`
- `raw_input`

See [Reference: Commands](commands.md).

## Middleware

### `MiddlewareContext`

Carries the active command execution context through middleware.

Fields:

- `raw_input`
- `session`
- `command`
- `cancelled`

### `NextFn`

Callable type for the middleware continuation.

See [Reference: Middleware](middleware.md).

## UI And Rendering

### `ThemeConfig`

Semantic color configuration used by renderers and widgets.

### `CursorControl`

Small helper for terminal cursor operations used by the UI and layout system.

### `InputMode`

Prompt behavior enum used by the input engine and input components.

Values:

- `COMMAND`
- `TEXT`
- `MULTILINE`
- `CONFIRM`
- `PASSWORD`

### `HelpGenerator`

Utility that formats registered commands into a help string.

### `CLIArgsParser`

Wrapper around `argparse.ArgumentParser` used for app-level CLI flags like `--version`, `--config`, and `--debug`.

## Persistence

### `SessionStateManager`

Handles serialization and storage of session state when persistence is enabled.

## Error Types

Klix exports:

- `KlixError`
- `CommandNotFoundError`
- `ArgValidationError`
- `InputCancelledError`
- `SessionStateError`
- `MiddlewareAbortError`
- `RenderError`
- `CompatibilityError`

See [Reference: Errors](errors.md).

## Example Import Block

```python
import klix


@dataclass
class DemoState(klix.SessionState):
    counter: int = 0


app = klix.App(
    name="Demo",
    version="0.1.0",
    description="API reference example",
    state_schema=DemoState,
)
```

## Common Mistakes

- Importing internal modules directly when the public API already exports what you need.
- Treating internal helpers like `_router` and `_event_bus` as stable public APIs. They are useful in advanced examples, but they are not the main supported surface.
- Assuming everything in the package is exported from `klix.__init__`. Check the list above first.

## Related Reading

- [Reference: Config](config.md)
- [Reference: Errors](errors.md)
- [Examples: Minimal](../examples/minimal.md)
