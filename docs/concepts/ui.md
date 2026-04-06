# UI Namespace

`session.ui` is the main developer-facing UI surface in Klix. It combines printing, streaming, layout, input widgets, output widgets, and cursor helpers in one place.

See also:

- [Renderer](renderer.md)
- [Layout](layout.md)
- [Input Components](../components/input.md)
- [Output Components](../components/output.md)

## Why It Exists

Without `session.ui`, app code would need to know where every subsystem lives:

- renderer for printing
- layout engine for regions
- input engine for prompts
- widget packages for output helpers

That is too much plumbing for day-to-day handler code.

`session.ui` gives you a smaller, coherent surface.

## What Lives Under `session.ui`

Current members:

- `session.ui.print(...)`
- `session.ui.stream(...)`
- `session.ui.clear()`
- `session.ui.newline()`
- `session.ui.bell()`
- `session.ui.move_cursor(...)`
- `session.ui.input.*`
- `session.ui.output.*`
- `session.ui.layout.*`

## Basic Printing

```python
session.ui.print("Connected.", color="success", bold=True)
session.ui.print("Low priority detail", color="muted", dim=True)
```

## Streaming

```python
import asyncio

async def chunks():
    for part in ["Hello", " ", "world"]:
        yield part
        await asyncio.sleep(0.1)

await session.ui.stream(chunks(), color="text", end="\n")
```

This is how the chat-style example simulates streaming output. See [Gemini-Style CLI](../examples/gemini-style-cli.md).

## Input Components

```python
name = await session.ui.input.text("Name", placeholder="Type your name")
approved = await session.ui.input.confirm("Continue?", default=True)
choice = await session.ui.input.select(["prod", "staging", "dev"], label="Environment")
```

See [Input Components](../components/input.md).

## Output Components

```python
session.ui.output.panel("Deployment finished", title="Result", border_color="success")
session.ui.output.table(
    headers=["Name", "Status"],
    rows=[["api", "ready"], ["worker", "ready"]],
    header_color="accent",
)
```

See [Output Components](../components/output.md).

## Layout Access

```python
session.ui.layout.header.set("My Tool", color="accent")
session.ui.layout.status.set("Ready", "Use /help", color="muted")
session.ui.layout.redraw_ui()
```

## Realistic Example

```python
@app.command("/report", help="Show a report")
def report(session: klix.Session):
    session.ui.layout.status.set("Running", "/report", color="muted")
    session.ui.layout.redraw_ui()

    session.ui.output.panel(
        "Report generated successfully.",
        title="Summary",
        border_color="accent",
    )
    session.ui.output.table(
        headers=["Metric", "Value"],
        rows=[["jobs", "12"], ["errors", "0"]],
        header_color="accent",
        alignments=["left", "right"],
    )
```

## Pitfalls

### Jumping below `session.ui` too early

Most app code should start at `session.ui`. Reach for renderer or input engine internals only when you need behavior the higher-level API does not provide.

### Mixing layout assumptions with raw printing

The layout system is not a full retained renderer. Use it for structure, but remember that normal output still appends to the terminal.
