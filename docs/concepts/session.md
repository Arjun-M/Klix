# Session

`Session` is the per-terminal runtime object in Klix. If `App` is the application definition, `Session` is the active instance.

See also:

- [App](app.md)
- [State](state.md)
- [UI Namespace](ui.md)
- [Persistence](../guides/persistence.md)

## Why `Session` Exists

A framework like Klix needs a place to hold runtime state that is not global:

- current application state
- metadata about the terminal
- runtime UI handles
- input history
- background tasks

That is what `Session` does.

## What Lives On A Session

The current implementation exposes these important attributes:

- `session.id`
- `session.state`
- `session.metadata`
- `session.history`
- `session.ui`
- `session.input_engine`

`session.ui` and `session.input_engine` are attached during startup. They are `None` until the runtime has been built.

## Typed State

The most common reason to use `Session` is typed state access:

```python
from dataclasses import dataclass
import klix

@dataclass
class MyState(klix.SessionState):
    logged_in: bool = False
    username: str = ""

app = klix.App(name="mytool", state_schema=MyState)

@app.command("/login", help="Log in")
def login(session: klix.Session):
    session.state.logged_in = True
    session.state.username = "alice"
```

See [Working with State](../guides/working-with-state.md).

## Terminal Metadata

Klix captures a small `TerminalMetadata` object on startup. It currently contains:

- `env`
- `width`
- `height`
- `start_time`
- `term_program`
- `interactive`

Example:

```python
@app.command("/env", help="Show terminal metadata")
def env(session: klix.Session):
    session.ui.output.json(
        {
            "interactive": session.metadata.interactive,
            "term_program": session.metadata.term_program,
            "size": [session.metadata.width, session.metadata.height],
        }
    )
```

## Background Tasks

`Session.create_task()` lets you schedule session-scoped async work:

```python
import asyncio

@app.command("/watch", help="Run a background watcher")
async def watch(session: klix.Session):
    async def worker():
        for i in range(3):
            await asyncio.sleep(1)
            session.ui.print(f"tick {i + 1}", dim=True)

    session.create_task(worker())
```

Klix tracks these tasks and waits on them during shutdown.

## How It Fits The Architecture

Every handler and middleware function gets a `Session` because it is the shortest path to the active runtime:

- state
- UI
- metadata
- background tasks

That keeps function signatures simple without forcing global variables.

## Common Mistakes

### Using `session.ui` before startup

If you instantiate a `Session` yourself outside the normal `App.run()` path, you are responsible for attaching `session.ui` and `session.input_engine`.

### Putting app definition into session state

State should hold runtime data, not command definitions, renderer objects, or application configuration that already lives on `App`.

### Assuming `session.history` is fully managed everywhere

`session.history` is the live per-session command history backing the input engine.

That means:

- Up/Down arrow navigation reads from it
- duplicate consecutive commands are skipped
- `AppConfig(max_history_size=...)` trims it automatically

The field is still just a Python list, so if you mutate it directly, do it deliberately.
