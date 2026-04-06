# Getting Started

This page gives you the shortest realistic path from install to a working Klix app.

If you want a more hands-on walkthrough, continue to [Quickstart](quickstart.md). If you want to understand the model first, read [Architecture](concepts/architecture.md).

## The Mental Model

Klix applications are built around a few core objects:

- `App` defines the application and owns the runtime
- `Session` represents one terminal instance
- `Command` objects define slash commands
- `session.ui` is where rendering and interactive widgets live

The default runtime loop is command-driven:

1. start the app
2. read a line of input
3. parse it as a slash command
4. run middleware
5. invoke the handler

That design is covered in [App](concepts/app.md), [Commands](concepts/commands.md), and [Router](concepts/router.md).

## Smallest Useful App

Create `main.py`:

```python
import klix

app = klix.App(
    name="mytool",
    version="0.1.0",
    description="A simple Klix app",
)

@app.on("start")
def on_start(session: klix.Session):
    session.ui.print("Ready.", color="accent", bold=True)

@app.command("/hello", help="Say hello")
def hello(session: klix.Session):
    session.ui.print("Hello from Klix.", color="success")

if __name__ == "__main__":
    app.run()
```

Run it:

```bash
python main.py
```

Then type:

```text
/hello
```

## What Happened

- `App(...)` created the command registry and runtime configuration
- `@app.on("start")` registered a lifecycle hook
- `@app.command(...)` created and registered a `Command`
- `app.run()` started the event loop and interactive session

See:

- [App](concepts/app.md)
- [Events](concepts/events.md)
- [Commands](concepts/commands.md)

## Using The Scaffold Instead

If you want a generated starting point instead of writing the app by hand:

```bash
klix init mytool
cd mytool
pip install -e .
mytool
```

The generated project includes:

- a working `App`
- a typed state class
- one event handler
- one middleware example
- one command with `args_schema`

See [Building Your First CLI](guides/building-your-first-cli.md).

## Where To Go Next

- Learn the runtime model in [Architecture](concepts/architecture.md)
- Learn command design in [Adding Commands](guides/adding-commands.md)
- Learn UI rendering in [Creating UI](guides/creating-ui.md)
- Learn persistence in [Persistence](guides/persistence.md)
