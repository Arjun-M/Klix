# Renderer

The renderer is the output abstraction in Klix. It gives the rest of the framework a small semantic surface for printing and screen clearing without exposing rich-specific details everywhere.

See also:

- [UI Namespace](ui.md)
- [Output Components](../components/output.md)
- [Theming](../guides/theming.md)

## Why It Exists

Not every terminal environment is a good match for full rich output. Klix uses a renderer layer so the rest of the framework can say:

- print this text
- use this semantic color
- clear the screen

and let the renderer decide how to do that.

## Renderer Types

Current renderer classes:

- `RichRenderer`
- `FallbackRenderer`
- `CIRenderer`

The selection happens in `klix.compat.get_renderer()`.

## RichRenderer

This is the normal interactive path. It:

- creates a `rich.console.Console`
- resolves semantic theme names like `accent` and `error`
- prints styled output through rich

Example:

```python
session.ui.print("Saved.", color="success", bold=True)
```

If rich is active, that becomes styled output through the console.

## FallbackRenderer

Fallback mode prints plain text and clears with escape sequences. It is intentionally minimal.

Use it as the baseline behavior when:

- colors are not reliable
- the terminal is very limited
- you care more about robustness than presentation

## CIRenderer

`CIRenderer` currently inherits from `FallbackRenderer`. It exists as a distinct mode because CI and pipes are a meaningful behavior boundary in the framework.

In practice, CI mode affects both:

- output rendering
- input behavior

See [Input Engine](input-engine.md).

## Color Resolution

Renderers accept either:

- raw color values
- semantic names from `ThemeConfig`

For example:

```python
session.ui.print("Warning", color="warning")
session.ui.print("Custom", color="#FFAA00")
```

## Current Limitations

The renderer layer is intentionally narrow:

- it is not a full layout engine
- it does not own complex stateful screen management
- rich widgets are built above it in `session.ui.output`

That is a good thing. It keeps the boundary clean.

## Pitfalls

### Writing component code against `rich.console.Console` directly everywhere

If you skip the renderer surface entirely, your code becomes harder to run in fallback environments.

### Treating `CIRenderer` as just visual fallback

It is also a signal that input should become non-interactive.
