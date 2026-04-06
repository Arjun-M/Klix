# Klix Documentation

Klix is a Python framework for building terminal-first CLI applications with a session model, command routing, middleware, lifecycle events, typed state, and a small UI layer built on top of `prompt_toolkit` and `rich`.

This documentation is written against the current implementation in this repository. It explains what Klix can do today, how the pieces fit together, and where the current boundaries are.

If you are new to Klix, use this path:

1. Read [Installation](installation.md)
2. Work through [Getting Started](getting-started.md)
3. Build the example in [Quickstart](quickstart.md)
4. Read [Architecture](concepts/architecture.md)
5. Use the focused guides in [Guides](guides/building-your-first-cli.md)

## Documentation Map

### Start here

- [Installation](installation.md)
- [Getting Started](getting-started.md)
- [Quickstart](quickstart.md)

### Core concepts

- [Architecture](concepts/architecture.md)
- [App](concepts/app.md)
- [Session](concepts/session.md)
- [Commands](concepts/commands.md)
- [Middleware](concepts/middleware.md)
- [Events](concepts/events.md)
- [State](concepts/state.md)
- [Router](concepts/router.md)
- [Input Engine](concepts/input-engine.md)
- [Renderer](concepts/renderer.md)
- [Layout](concepts/layout.md)
- [UI Namespace](concepts/ui.md)

### Practical guides

- [Building Your First CLI](guides/building-your-first-cli.md)
- [Adding Commands](guides/adding-commands.md)
- [Using Middleware](guides/using-middleware.md)
- [Handling Events](guides/handling-events.md)
- [Working with State](guides/working-with-state.md)
- [Creating UI](guides/creating-ui.md)
- [Input Modes](guides/input-modes.md)
- [Autocomplete](guides/autocomplete.md)
- [Persistence](guides/persistence.md)
- [Theming](guides/theming.md)

### Components

- [Input Components](components/input.md)
- [Output Components](components/output.md)
- [Widgets Reference](components/widgets.md)

### Example walkthroughs

- [Minimal Example](examples/minimal.md)
- [Full Demo](examples/full-demo.md)
- [Gemini-Style CLI](examples/gemini-style-cli.md)

### API reference

- [API Overview](reference/api.md)
- [Command Reference](reference/commands.md)
- [Event Reference](reference/events.md)
- [Middleware Reference](reference/middleware.md)
- [Error Reference](reference/errors.md)
- [Config Reference](reference/config.md)

### Project docs

- [Contributing](contributing.md)
- [FAQ](faq.md)

## What Klix Gives You

- A single `App` object that owns registration and runtime flow
- Per-session state through `Session`
- Slash-command parsing with schema validation
- Middleware around command execution
- Lifecycle and input events
- Rich text rendering and fallback rendering
- A UI namespace with input widgets and output widgets
- A basic region-based layout model
- A scaffold CLI through `klix init`

## What Klix Does Not Try To Be

Klix is not a general terminal emulator and it is not a full-screen TUI framework in the `textual` sense. The current implementation favors a simple interactive command loop with composable utilities over a heavy runtime model.

That matters when you read the rest of these docs:

- layout support exists, but redraw behavior is still coarse
- events exist, but only some are actively emitted by the current runtime
- persistence exists, but it is intentionally minimal
- widgets are reusable, but not every one is a complex full-screen experience

Those details are documented explicitly in [Architecture](concepts/architecture.md), [Layout](concepts/layout.md), and [FAQ](faq.md).
