# Creating UI

Klix gives you one main UI surface: `session.ui`. It combines output helpers, input components, layout regions, and streaming support into a single namespace.

This guide focuses on building clean terminal interfaces with those primitives. For the API tour, see [UI](../concepts/ui.md). For the individual widget sets, see [Components: Input](../components/input.md) and [Components: Output](../components/output.md).

## Start With A Simple Screen

```python
@app.on("start")
def on_start(session: klix.Session) -> None:
    session.ui.clear()
    session.ui.layout.header.set("Deploy Tool", color="accent")
    session.ui.layout.status.set("ready", "Use /help", color="muted")
    session.ui.layout.redraw_ui()
    session.ui.print("Choose a command to begin.", color="text")
```

That gives you:

- a clear header
- a persistent status line
- scrollable command output in the main area

## Prefer Semantic Colors

Klix widgets and renderers accept semantic color names:

- `accent`
- `text`
- `muted`
- `info`
- `success`
- `warning`
- `error`
- `border`

Use those rather than hardcoded ANSI strings so your app respects the active theme. See [Theming](theming.md).

## Print Structured Output

For simple lines:

```python
session.ui.print("Deploy complete.", color="success", bold=True)
```

For richer display:

```python
session.ui.output.panel(
    "Everything needed for the release is ready.",
    title="Summary",
    border_color="success",
)

session.ui.output.table(
    headers=["Step", "Status"],
    rows=[
        ["build", "done"],
        ["tests", "done"],
        ["deploy", "pending"],
    ],
    header_color="accent",
)
```

## Use The Layout Sparingly

Klix layout is intentionally lightweight. The pattern that works best is:

- keep a static header
- keep a short status line
- print everything else into the main transcript area

Example:

```python
def set_status(session: klix.Session, detail: str) -> None:
    session.ui.layout.status.set(
        left="model: klix-1",
        right=detail,
        color="muted",
    )
    session.ui.layout.redraw_ui()
```

Avoid trying to build a fully retained multi-pane UI. Klix does not implement that level of terminal layout management today.

## Stream Output For Better Feedback

Streaming makes terminal apps feel more responsive.

```python
async def stream_reply(session: klix.Session) -> None:
    async def chunks():
        for piece in ["Thinking", ".", ".", "."]:
            yield piece
            await asyncio.sleep(0.1)

    session.ui.print("Assistant: ", color="info", bold=True, end="")
    await session.ui.stream(chunks(), color="text", end="\n")
```

This is the same core pattern used by the chat-style demo app.

## Collect Structured Input

`session.ui.input` gives you prompt-toolkit based components:

```python
name = await session.ui.input.text("Name", placeholder="Jane Doe")
approve = await session.ui.input.confirm("Deploy now?", default=True)
target = await session.ui.input.select(["staging", "production"], label="Target")
```

Use them when a command becomes form-like and plain slash arguments stop being pleasant.

## Build A Practical Screen

```python
@app.command("/release", help="Run a guided release flow")
async def release(session: klix.Session) -> None:
    version = await session.ui.input.text("Version", placeholder="1.2.3")
    target = await session.ui.input.select(
        ["staging", "production"],
        label="Environment",
    )
    confirm = await session.ui.input.confirm(
        f"Deploy {version} to {target}?",
        default=False,
    )

    if not confirm:
        session.ui.print("Release cancelled.", color="warning")
        return

    spinner = session.ui.output.spinner("Preparing release", color="accent")
    spinner.start()
    await asyncio.sleep(0.5)
    spinner.stop()

    session.ui.output.panel(
        f"Released {version} to {target}",
        title="Release Complete",
        border_color="success",
    )
```

## Common Mistakes

- Hardcoding visual styles instead of using theme keys.
- Forgetting to redraw header and status regions after updates.
- Trying to use layout regions for long transcripts instead of printing into the main area.
- Expecting printed output to remain perfectly isolated while a prompt is active. The UI namespace restores the prompt, but terminal UIs are still sequential by nature.

## Related Reading

- [Components: Input](../components/input.md)
- [Components: Output](../components/output.md)
- [Components: Widgets](../components/widgets.md)
- [Theming](theming.md)
