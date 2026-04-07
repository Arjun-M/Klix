# Theming

Klix uses a small semantic theme surface so applications can stay readable without coupling themselves to a specific renderer implementation.

This guide explains how to define a theme, how widgets consume it, and where the boundaries are. For the renderer layer, see [Renderer](../concepts/renderer.md).

## ThemeConfig

The theme model is `ThemeConfig`.

Current fields are:

- `accent`
- `background`
- `text`
- `input_background`
- `input_text_color`
- `muted`
- `info`
- `border`
- `cursor`
- `success`
- `warning`
- `error`

You can pass a theme when creating the app:

```python
app = klix.App(
    name="DocsTool",
    version="0.1.0",
    description="Theme example",
    state_schema=DocsState,
    theme=klix.ThemeConfig(
        accent="#6EA8FE",
        text="#F7F9FC",
        muted="#7C8698",
        info="#8AB4F8",
        border="#2D3B55",
        success="#7BD88F",
        warning="#F6C177",
        error="#FF7B72",
        input_background="#171B24",
        input_text_color="#F7F9FC",
    ),
)
```

`input_background` is optional. If you leave it unset, Klix keeps the default prompt styling.

## Why Semantic Colors Matter

A command should say:

```python
session.ui.print("Saved successfully.", color="success")
```

not:

```python
session.ui.print("Saved successfully.", color="#22c55e")
```

Why:

- renderers can translate semantic names however they need to
- theme changes stay centralized
- fallback renderers degrade more cleanly

## Use Theme Keys Across Output

Panels:

```python
session.ui.output.panel(
    "Deployment finished.",
    title="Status",
    border_color="success",
    title_color="accent",
)
```

Tables:

```python
session.ui.output.table(
    headers=["Step", "State"],
    rows=[["build", "done"], ["deploy", "running"]],
    header_color="accent",
    border_color="border",
)
```

Layout:

```python
session.ui.layout.header.set("OpsTool", color="accent")
session.ui.layout.status.set("ready", "prod", color="muted")
```

Input bar:

```python
app = klix.App(
    name="OpsTool",
    theme=klix.ThemeConfig(
        input_background="#171B24",
        input_text_color="#F7F9FC",
    ),
)
```

In capable terminals, Klix applies that background to the active input area through prompt_toolkit styling while keeping cursor and selection behavior intact.

## Mock Theme Switching

The chat example in the repository shows the usual pattern: mutate the live renderer theme and redraw.

```python
def set_theme(session: klix.Session) -> None:
    theme = session.ui.renderer.theme
    theme.accent = "#2B6CB0"
    theme.text = "#1F2937"
    theme.muted = "#6B7280"
```

Then redraw any layout regions or output that should reflect the change.

This is intentionally simple. Klix does not implement a more elaborate theme manager.

## What Fallback Renderers Do

The rich renderer uses colors and rich widgets when possible. The fallback and CI renderers reduce that formatting to plain text output.

That means a theme should improve the experience in capable terminals, but your app should still read well without heavy styling.

## Common Mistakes

- Passing arbitrary color names that are not in the theme config. Some widgets resolve unknown colors directly, but semantic keys are the safer path.
- Building meaning into raw color values instead of labels and copy.
- Expecting a theme update to automatically repaint all previous output. Existing printed lines stay as they were; redraw affects layout and future output.
- Assuming `input_background` affects fallback or CI prompts the same way. Rich prompt styling is only available in interactive prompt_toolkit mode.

## Related Reading

- [Creating UI](creating-ui.md)
- [Components: Output](../components/output.md)
- [Reference: Config](../reference/config.md)
