# Klix Skill

Use this file as a fast-start guide for building CLI apps with Klix.

## What Klix Is

Klix is a Python framework for building interactive command-line applications. It gives you a structured app runtime, typed session state, command routing, prompt-based input, terminal UI helpers, middleware, and events.

Klix is for building apps, not for defining one-off scripts.

## Core Mental Model

### `App`

`App` is the composition root.

It owns:
- command registration
- middleware registration
- event handlers
- theme and config
- session startup and the main loop

Typical shape:

```python
app = klix.App(
    name="mytool",
    version="0.1.0",
    description="My CLI tool",
    state_schema=MyState,
)
```

### `Session`

`Session` is the per-run execution context.

It holds:
- `session.state`: typed session state
- `session.ui`: printing, widgets, layout, streaming, input helpers
- `session.metadata`: terminal/runtime metadata
- `session.input_engine`: lower-level prompt access when needed

If you are in a command handler, almost everything you need should come from the session.

### `Command`

Commands are slash-triggered actions such as `/help` or `/deploy`.

A command maps:
- name
- optional aliases
- optional typed args schema
- handler

Decorator form:

```python
@app.command("/deploy", help="Deploy the current build")
def deploy(session: klix.Session) -> None:
    ...
```

### Runtime Flow

In the standard app loop, the flow is:

```text
Input -> Router Parse -> Middleware -> Handler
```

More concretely:

1. the input engine reads a line
2. the router parses the slash command
3. middleware runs around the parsed command
4. the handler executes

Important: middleware sees `ctx.command` after parsing.

## Minimal Working Example

```python
from dataclasses import dataclass

import klix


@dataclass
class DemoState(klix.SessionState):
    runs: int = 0


app = klix.App(
    name="demo",
    version="0.1.0",
    description="Minimal Klix app",
    state_schema=DemoState,
)


@app.on("start")
def on_start(session: klix.Session) -> None:
    session.ui.print("Try /hello or /exit", color="muted")


@app.command("/hello", help="Say hello")
def hello(session: klix.Session) -> None:
    session.state.runs += 1
    session.ui.print(f"Hello. Run #{session.state.runs}", color="success")


if __name__ == "__main__":
    app.run()
```

Run it:

```bash
python main.py
```

## Common Patterns

### Add A Command

```python
@app.command("/status", help="Show health")
def status(session: klix.Session) -> None:
    session.ui.print("System healthy.", color="success")
```

### Add Typed Args With Pydantic

```python
from pydantic import BaseModel


class DeployArgs(BaseModel):
    environment: str
    force: bool = False


@app.command("/deploy", args_schema=DeployArgs, help="Deploy the app")
def deploy(args: DeployArgs, session: klix.Session) -> None:
    session.ui.print(
        f"Deploying to {args.environment} (force={args.force})",
        color="warning",
    )
```

Example input:

```text
/deploy production --force
```

### Use `session.state`

```python
from dataclasses import dataclass, field


@dataclass
class AppState(klix.SessionState):
    history: list[str] = field(default_factory=list)


@app.command("/remember")
def remember(session: klix.Session) -> None:
    session.state.history.append("something happened")
    session.ui.print("Saved to session state.")
```

Use session state for app data that belongs to the current run.

### Print Output

Plain output:

```python
session.ui.print("Saved.", color="success")
```

Panels and tables:

```python
session.ui.output.panel("Deployment complete", title="Status", border_color="success")

session.ui.output.table(
    headers=["Step", "Status"],
    rows=[["build", "done"], ["deploy", "running"]],
    header_color="accent",
)
```

### Collect Input

```python
name = await session.ui.input.text("Name")
approved = await session.ui.input.confirm("Continue?", default=True)
choice = await session.ui.input.select(["staging", "production"], label="Target")
```

Use these instead of rolling your own prompt flow unless you need something very custom.

### Use Layout For Lightweight Structure

```python
session.ui.layout.header.set("My Tool", color="accent")
session.ui.layout.status.set("ready", "Use /help", color="muted")
session.ui.layout.redraw_ui()
```

Use layout for header and status regions. Print long-running output into the main area.

### Split-Pane Layout (Advanced)

Klix supports a dual-panel view within the main area:

```python
# Activate split (horizontal by default, 50/50 ratio)
session.ui.layout.split(direction="horizontal", ratio=0.4)

# Print to specific panels
session.ui.layout.left.print("Navigation", color="accent")
session.ui.layout.right.print("Editor Content", color="text")

# Disable and return to single-column
session.ui.layout.disable_split()
```

## Key APIs

### `app.command(...)`

Registers a slash command.

Common arguments:
- `name`
- `help`
- `aliases`
- `args_schema`

### `session.ui.*`

Main app-facing terminal API.

Useful entry points:
- `session.ui.print(...)`
- `session.ui.clear()`
- `session.ui.stream(...)`
- `session.ui.output.table(...)`
- `session.ui.output.panel(...)`
- `session.ui.output.spinner(...)`
- `session.ui.input.text(...)`
- `session.ui.input.confirm(...)`
- `session.ui.input.select(...)`
- `session.ui.layout.header.set(...)`
- `session.ui.layout.status.set(...)`
- `session.ui.layout.redraw_ui()`

### Middleware

```python
@app.middleware
async def logging(ctx: klix.MiddlewareContext, next: klix.NextFn) -> None:
    ctx.session.ui.print(f"running {ctx.command.name}", color="muted")
    await next(ctx)
```

Use middleware for:
- logging
- auth checks
- timing
- status updates

### Events

```python
@app.on("start")
def on_start(session: klix.Session) -> None:
    ...


@app.on("exit")
def on_exit(session: klix.Session) -> None:
    ...
```

Common event names used by the runtime:
- `start`
- `input`
- `command`
- `interrupt`
- `error`
- `exit`

## Rules For Using Klix

- Do not use process-global mutable state for app behavior.
- Put per-run data in `session.state`.
- Prefer typed arguments with Pydantic for command inputs.
- Treat `session.ui` as the main interaction surface.
- Respect the session model: one run, one session, one state object.
- Keep command handlers focused on the task they perform.
- Use middleware for cross-cutting concerns, not command-specific logic.

## Do / Don't

### Do

- Define a typed state model with a dataclass.
- Keep commands small and explicit.
- Use semantic colors like `success`, `warning`, and `accent`.
- Use `session.ui.input.*` for guided flows.
- Use layout for header and status only.
- Add `help` text to every public command.

### Don't

- Do not store renderer or input objects in session state.
- Do not parse command text manually inside normal handlers if `args_schema` can do it.
- Do not rely on global variables for authenticated user, mode, or history.
- Do not assume shell-style quoting support in command parsing.
- Do not overbuild the layout system into a full-screen retained TUI.

## Common Mistakes

- Forgetting the leading slash for routed commands.
- Expecting plain text to become a command in the default app loop.
- Updating layout regions without calling `redraw_ui()`.
- Using mutable defaults in state dataclasses without `default_factory`.
- Treating cancellation from interactive selectors as impossible.

## When To Reach Lower-Level APIs

Use lower-level pieces only when needed:
- `session.input_engine` for custom prompt flows
- internal router or event bus usage for advanced custom loops
- custom renderer interaction only when UI helpers are not enough

For most apps, stay with:
- `App`
- `Session`
- command handlers
- `session.ui`
- middleware
- events

## Fast Build Checklist

When an AI agent needs to ship a Klix app quickly:

1. define a `SessionState` dataclass
2. create `klix.App(...)`
3. add a `start` event for welcome output
4. add slash commands with `@app.command`
5. use Pydantic schemas for command args
6. print through `session.ui`
7. use `session.ui.input.*` for guided interaction
8. use middleware for logs/auth/status
9. run with `app.run()`

That is enough to build a solid CLI without needing the internals.
