# App

`App` is the center of a Klix application. It is where you register commands, middleware, completers, and event handlers, and it is the object that starts the runtime.

See also:

- [Architecture](architecture.md)
- [Commands](commands.md)
- [Middleware](middleware.md)
- [Events](events.md)
- [Config Reference](../reference/config.md)

## Why `App` Exists

Without a central object, a CLI framework tends to spread behavior across globals and ad hoc registries. Klix keeps those concerns in one place:

- runtime configuration
- command registry
- lifecycle hooks
- router access
- persistence wiring
- input/output startup

That makes apps easier to reason about and easier to scaffold with `klix init`.

## Basic Usage

```python
import klix
from dataclasses import dataclass

@dataclass
class MyState(klix.SessionState):
    counter: int = 0

app = klix.App(
    name="mytool",
    version="1.0.0",
    description="A sample tool",
    state_schema=MyState,
    persist_session=True,
)
```

## What `App` Owns Internally

The current implementation stores:

- `_commands`
- `_middlewares`
- `_event_bus`
- `_router`
- `_custom_completers`
- `_state_manager`
- `_help_generator`

You normally interact with those through decorators or public methods:

- `app.command(...)`
- `app.on(...)`
- `app.middleware`
- `app.completer(...)`
- `app.generate_help()`
- `app.run()`

## Registration APIs

### Command registration

```python
@app.command("/deploy", help="Deploy the current branch")
def deploy(session: klix.Session):
    session.ui.print("Deploying...")
```

This decorator builds a `Command` object under the hood. See [Commands](commands.md).

### Event registration

```python
@app.on("start")
def on_start(session: klix.Session):
    session.ui.print("Ready.", color="accent")
```

See [Events](events.md).

### Middleware registration

```python
@app.middleware
async def log(ctx: klix.MiddlewareContext, next: klix.NextFn):
    print("before")
    await next(ctx)
    print("after")
```

See [Middleware](middleware.md).

### Completer registration

```python
@app.completer("/deploy")
def deploy_completer(text: str, session: klix.Session) -> list[str]:
    return ["prod", "staging", "dev"]
```

See [Autocomplete](../guides/autocomplete.md).

## What `run()` Actually Does

At a high level, `run()`:

1. parses global CLI args through `CLIArgsParser`
2. creates a session and terminal metadata
3. creates the completer
4. picks a renderer via compatibility detection
5. attaches `session.ui` and `session.input_engine`
6. emits `start`
7. loops on prompt input
8. parses slash commands
9. builds and executes middleware chain
10. emits `exit` and saves persistent state

That flow matters because it defines which extension points are active when.

For example:

- middleware only runs for parsed commands
- `input` events happen before routing
- the `command` event is emitted during dispatch

## Realistic Example

```python
import time
import klix
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class DeployState(klix.SessionState):
    authenticated: bool = False

class DeployArgs(BaseModel):
    env: str
    force: bool = False

app = klix.App(name="deployctl", state_schema=DeployState)

@app.on("start")
def on_start(session: klix.Session):
    session.ui.layout.header.set("Deploy Control", color="accent")
    session.ui.layout.status.set("Ready", "Use /help", color="muted")
    session.ui.layout.redraw_ui()

@app.middleware
async def timing(ctx: klix.MiddlewareContext, next: klix.NextFn):
    start = time.time()
    await next(ctx)
    ctx.session.ui.print(f"{time.time() - start:.2f}s", color="muted", dim=True)

@app.command("/deploy", args_schema=DeployArgs, help="Deploy an environment")
def deploy(args: DeployArgs, session: klix.Session):
    session.ui.output.panel(
        f"Deploying to {args.env} (force={args.force})",
        title="Deployment",
        border_color="accent",
    )

if __name__ == "__main__":
    app.run()
```

## Pitfalls

### Confusing `App` registration time with runtime

Decorators register behavior when the module is imported. They do not run during command dispatch.

### Expecting non-command text to dispatch automatically

The default `App.run()` loop assumes command-style input. If you want free-form chat text, build a custom loop around the same primitives. See [Gemini-Style CLI](../examples/gemini-style-cli.md).

### Treating private attributes as stable API

The implementation exposes enough internals to support advanced examples, but `_commands`, `_router`, and similar members should be treated as implementation details unless the public surface is insufficient for your use case.
