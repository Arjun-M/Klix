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
```

## How It Works Internally

The current layout engine is intentionally coarse, but sticky header support is built in:

- region objects store desired content
- `header.set(...)` and `status.set(...)` trigger an immediate redraw
- when a header is active, main output is replayed underneath it
- the header stays at the top instead of scrolling away with later output

This is still not a full retained dashboard renderer, but it is enough for a persistent top banner plus normal command output.

## What This Means In Practice

Layout works well for:

- startup banners
- sticky top-of-screen info
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

`header.set(...)` is enough to activate the sticky top region. You do not need to call `redraw_ui()` manually for normal usage anymore.

### Main

```python
session.ui.layout.main.print("Hello")
await session.ui.layout.main.stream(generator)
```

### Split Layout (Optional)

Call `session.ui.layout.split(direction="horizontal", ratio=0.5)` to activate a dual-panel view. The `left` and `right` regions accept independent output once split is on:

```python
session.ui.layout.split(direction="horizontal", ratio=0.4)
session.ui.layout.left.print("Primary log", color="text")
session.ui.layout.right.print("Secondary status", color="muted")
```

`session.ui.layout.disable_split()` returns to the single-column experience.

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
    session.ui.print("Use /release to start.", color="accent")

@app.command("/release", help="Start a release")
def release(session: klix.Session):
    session.ui.layout.status.set("Running", "/release", color="muted")
    session.ui.output.panel("Release in progress", title="Release", border_color="accent")
```

## Pitfalls

### Expecting `main` content to behave like a full-screen dashboard

Klix keeps enough buffered output to preserve the sticky header experience, but it is still not a general-purpose retained TUI surface.

### Manually forcing `redraw_ui()` everywhere

Header and status updates already repaint immediately. Reach for `redraw_ui()` only when you are extending layout behavior directly.

### Building a full dashboard on this layer

The current layout code is better for structured command UIs than for constantly updating dashboards.
