# Quickstart

This is a practical walkthrough that gets a real tool running with state, commands, middleware, and UI output.

If you have not installed Klix yet, start with [Installation](installation.md).

## Step 1: Create A Project

Use the built-in scaffold:

```bash
klix init notes
cd notes
```

You will get:

- `main.py`
- `pyproject.toml`
- `README.md`

Install it:

```bash
pip install -e .
```

Run it:

```bash
notes
```

## Step 2: Understand The Generated Shape

The generated file uses the same building blocks you will use everywhere:

- a typed session state class
- `app = klix.App(...)`
- a `start` event
- middleware
- one command

That makes it a good baseline for adding features.

## Step 3: Add A Real Command

Replace or extend the generated command with something closer to a real tool:

```python
import klix
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class NotesState(klix.SessionState):
    notes_created: int = 0

class AddArgs(BaseModel):
    title: str
    urgent: bool = False

app = klix.App(name="notes", state_schema=NotesState)

@app.command("/add", help="Add a note", args_schema=AddArgs)
def add_note(args: AddArgs, session: klix.Session):
    session.state.notes_created += 1
    session.ui.output.panel(
        f"Created note: {args.title}",
        title="Note Saved",
        border_color="success" if not args.urgent else "warning",
    )

if __name__ == "__main__":
    app.run()
```

Run:

```text
/add "buy milk" --urgent
```

In the current router implementation, argument parsing is token-based rather than shell-quote aware, so prefer simple tokens unless you add your own conventions. See [Router](concepts/router.md).

## Step 4: Add Middleware

Middleware is where you put cross-cutting logic:

```python
@app.middleware
async def timing(ctx: klix.MiddlewareContext, next: klix.NextFn):
    import time

    start = time.time()
    await next(ctx)
    session = ctx.session
    session.ui.print(f"{time.time() - start:.2f}s", color="muted", dim=True)
```

This runs around command dispatch, not around arbitrary text input. See [Using Middleware](guides/using-middleware.md).

## Step 5: Add A Start Banner

```python
@app.on("start")
def on_start(session: klix.Session):
    session.ui.layout.header.set("Notes CLI", color="accent")
    session.ui.layout.status.set("model: local", "ready", color="muted")
    session.ui.layout.redraw_ui()
    session.ui.print("Use /add to create notes.", color="accent")
```

This uses the current layout system. Read [Layout](concepts/layout.md) before depending on heavy redraw behavior.

## Step 6: Keep Going

Once this works, move to:

- [Adding Commands](guides/adding-commands.md)
- [Working with State](guides/working-with-state.md)
- [Creating UI](guides/creating-ui.md)
- [Theming](guides/theming.md)
