# Output Components

Klix exposes output helpers through `session.ui.output.*`. These helpers sit on top of the renderer layer and give you reusable terminal-friendly presentation primitives.

For the renderer internals, see [Renderer](../concepts/renderer.md). For layout regions, see [Layout](../concepts/layout.md).

## What Output Components Are For

Use output components when plain `print` lines start to feel too raw. They help you present:

- summaries
- reports
- structured data
- code snippets
- progress indicators

The current output surface includes:

- `table(...)`
- `panel(...)`
- `card(...)`
- `markdown(...)`
- `code(...)`
- `json(...)`
- `tree(...)`
- `diff(...)`
- `spinner(...)`
- `progress(...)`
- `group(...)`

## Tables

Tables are the main way to present rows and columns.

```python
session.ui.output.table(
    headers=["Service", "Status", "Latency"],
    rows=[
        ["api", "healthy", "42ms"],
        ["worker", "healthy", "18ms"],
        ["db", "degraded", "110ms"],
    ],
    header_color="accent",
    border_color="border",
    alignments=["left", "center", "right"],
)
```

They are intentionally lightweight. If you need deep per-cell formatting rules, build a custom rich renderable in app code and print it through the renderer.

## Panels And Cards

Panels are bordered containers. `card(...)` is the same primitive with a different semantic name.

```python
session.ui.output.panel(
    "Build complete. Ready to deploy.",
    title="Release Summary",
    border_color="success",
    title_color="accent",
)
```

Use them for:

- callouts
- confirmation summaries
- inline help
- grouped status messages

## Markdown And Code

These helpers lean on rich when available.

```python
session.ui.output.markdown("""
# Release Plan

- build
- test
- deploy
""")

session.ui.output.code("print('hello from klix')", lang="python")
```

![Markdown Rendering](../../images/markdown-rendering.png)
![Syntax Highlighted Code](../../images/syntax-highlighted-code.png)

Fallback renderers print plain text instead of rich formatting.

## JSON And Tree

These are useful when debugging or showing nested data.

```python
session.ui.output.json({"service": "api", "status": "healthy"})

session.ui.output.tree(
    {
        "release": {
            "build": "done",
            "deploy": ["staging", "production"],
        }
    },
    color="accent",
)
```

![JSON Output](../../images/deployment-result-json.png)
![Tree View](../../images/tree-view.png)

Use `json(...)` when exact structure matters. Use `tree(...)` when readability matters more than strict formatting.

## Diff Output

`diff(...)` shows a line-oriented difference between two strings.

```python
session.ui.output.diff(
    "version = 1\nstatus = pending",
    "version = 2\nstatus = complete",
)
```

![Diff View](../../images/diff-view.png)

It is intentionally simple and semantic:

- additions use success color
- removals use error color
- hint lines use warning color

It is not a full git-style patch renderer.

## Grouping Renderables

`group(...)` lets you print multiple rich renderables as one output unit when the rich console is available.

This is mostly useful in advanced app code that already creates rich objects directly.

## A Practical Report Screen

```python
@app.command("/report", help="Show release status")
def report(session: klix.Session) -> None:
    session.ui.output.panel(
        "Nightly release is healthy.",
        title="Overview",
        border_color="success",
    )
    session.ui.output.table(
        headers=["Step", "Status", "Duration"],
        rows=[
            ["build", "done", "2m 10s"],
            ["test", "done", "4m 05s"],
            ["deploy", "pending", "-"],
        ],
        header_color="accent",
        alignments=["left", "center", "right"],
    )
```

## Common Mistakes

- Overusing panels for everything. A screen full of boxes gets noisy fast.
- Expecting old output to repaint after a theme change.
- Treating fallback output as identical to rich output. It is functionally equivalent, not visually identical.

## Related Reading

- [Components: Widgets](widgets.md)
- [Creating UI](../guides/creating-ui.md)
- [Theming](../guides/theming.md)
