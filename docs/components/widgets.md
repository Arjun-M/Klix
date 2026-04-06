# Widgets

In Klix, “widgets” are the reusable output and interaction building blocks layered on top of the renderer and input engine. This page focuses on the stateful and higher-level pieces that are most useful when you build richer CLI flows.

For the raw component entry points, see [Input Components](input.md) and [Output Components](output.md).

## Spinner

Use `spinner(...)` when the user needs immediate feedback that something is happening.

```python
spinner = session.ui.output.spinner("Preparing release", color="accent")
spinner.start()
await asyncio.sleep(0.5)
spinner.update("Uploading artifacts")
await asyncio.sleep(0.5)
spinner.stop()
```

Why it exists:

- long operations feel broken without visible activity
- a spinner is lighter than a progress bar when total work is unknown

Internally:

- rich-capable terminals use a live status spinner
- fallback renderers print plain progress messages instead

## Progress Bar

Use `progress(...)` when work has a meaningful total.

```python
progress = session.ui.output.progress(total=5, label="Warmup", color="success")
progress.start()
for _ in range(5):
    await asyncio.sleep(0.2)
    progress.update(advance=1)
progress.stop()
```

You can also update by absolute completion or adjust the total dynamically.

## Panel, Card, And Table As Display Widgets

These are the display primitives most apps will use:

```python
session.ui.output.card(
    "Cards are just bordered content with a semantic name.",
    title="Card",
    border_color="info",
)

session.ui.output.table(
    headers=["Component", "State"],
    rows=[["spinner", "idle"], ["progress", "running"]],
)
```

They are simple on purpose. Klix expects apps to combine small widgets rather than rely on a giant declarative UI system.

## Interactive Selection Widgets

Although technically exposed through `session.ui.input`, selection widgets behave like interactive UI components:

- `select(...)`
- `multiselect(...)`
- `fuzzy(...)`
- `toggle(...)`

Use them when a command becomes more of a guided flow than a raw slash invocation.

```python
profile = await session.ui.input.select(
    ["Gemini", "Claude", "Klix", "Local"],
    label="Pick a profile",
)
```

## Building A Small Interactive Flow

```python
@app.command("/setup", help="Run interactive setup")
async def setup(session: klix.Session) -> None:
    profile = await session.ui.input.select(
        ["default", "performance", "debug"],
        label="Profile",
    )
    features = await session.ui.input.multiselect(
        ["logging", "metrics", "tracing"],
        label="Enable features",
    )

    spinner = session.ui.output.spinner("Applying configuration", color="accent")
    spinner.start()
    await asyncio.sleep(0.5)
    spinner.stop()

    session.ui.output.panel(
        f"Profile: {profile}\nFeatures: {', '.join(features) or 'none'}",
        title="Configuration Applied",
        border_color="success",
    )
```

## Terminal Behavior To Understand

Widgets in Klix are cooperative, not magical:

- they work within the prompt-driven model
- layout regions stay lightweight
- rich widgets degrade in fallback mode
- selection dialogs depend on an interactive terminal

That keeps the framework small, but it means you should design flows that are clear even without a fully dynamic screen.

## Common Mistakes

- Starting a spinner and forgetting to stop it.
- Using a progress bar when the total is unknown.
- Treating selection widgets as persistent screen elements instead of transient interactions.
- Overbuilding UI complexity that the coarse layout system is not meant to own.

## Related Reading

- [Examples: UI Showcase](../examples/full-demo.md)
- [Creating UI](../guides/creating-ui.md)
- [Layout](../concepts/layout.md)
