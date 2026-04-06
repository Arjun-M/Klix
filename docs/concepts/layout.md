# Layout

Klix has a small region-based layout layer for header, main content, and status output.

See also:

- [UI Namespace](ui.md)
- [Creating UI](../guides/creating-ui.md)
- [Full Demo](../examples/full-demo.md)

## Why Layout Exists

Even command-driven tools benefit from a bit of structure:

- a banner at the top
- a status line
- normal output in the middle

Klix keeps that in a dedicated layout subsystem so app code can talk about regions instead of manually reprinting everything.

## Current Regions

The implementation provides:

- `session.ui.layout.header`
- `session.ui.layout.main`
- `session.ui.layout.status`

Example:

```python
session.ui.layout.header.set("Deploy CLI", color="accent")
session.ui.layout.status.set("Ready", "Use /help", color="muted")
session.ui.layout.redraw_ui()
```

## How It Works Internally

The current layout engine is intentionally coarse:

- region objects store desired content
- `trigger_redraw()` marks the layout dirty
- `redraw_ui()` clears the screen and redraws header/status if needed
- main output still flows through normal `print()` calls

This is important: Klix does not currently maintain a full persistent screen buffer for all content.

## What This Means In Practice

Layout works well for:

- startup banners
- status summaries
- simple region updates

It is less ideal for:

- complex full-screen dashboards
- heavy incremental repainting
- strict bottom-anchored input layouts

Use the layout system, but use it with realistic expectations.

## Region APIs

### Header

```python
session.ui.layout.header.set("My Tool", color="accent")
session.ui.layout.header.clear()
```

### Main

```python
session.ui.layout.main.print("Hello")
await session.ui.layout.main.stream(generator)
```

### Status

```python
session.ui.layout.status.set("Ready", "v1.0.0", color="muted")
session.ui.layout.status.clear()
```

## Realistic Example

```python
@app.on("start")
def on_start(session: klix.Session):
    session.ui.layout.header.set("Release Console", color="accent")
    session.ui.layout.status.set("Ready", "no active task", color="muted")
    session.ui.layout.redraw_ui()
    session.ui.print("Use /release to start.", color="accent")

@app.command("/release", help="Start a release")
def release(session: klix.Session):
    session.ui.layout.status.set("Running", "/release", color="muted")
    session.ui.layout.redraw_ui()
    session.ui.output.panel("Release in progress", title="Release", border_color="accent")
```

## Pitfalls

### Expecting `main` content to be fully rehydrated on redraw

The current engine redraws header and status, not a full retained transcript.

### Calling `set()` without `redraw_ui()`

Region updates mark the layout dirty, but if your flow depends on immediate repaint, call `redraw_ui()` explicitly.

### Building a full dashboard on this layer

The current layout code is better for structured command UIs than for constantly updating dashboards.
