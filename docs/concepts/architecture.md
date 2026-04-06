# Architecture

Klix is organized around a small set of cooperating subsystems. The implementation is intentionally compact, so understanding the architecture is mostly about understanding the runtime flow.

See also:

- [App](app.md)
- [Session](session.md)
- [Router](router.md)
- [Input Engine](input-engine.md)
- [Renderer](renderer.md)
- [Layout](layout.md)
- [UI Namespace](ui.md)

## The Runtime Shape

At runtime, a typical Klix app looks like this:

1. `App` is created and registrations happen
2. `app.run()` parses top-level CLI flags
3. Klix creates a `Session`
4. Klix chooses a renderer and input engine
5. Klix emits the `start` event
6. Klix reads a line
7. Klix emits the `input` event
8. Klix parses the line through the router
9. Klix runs middleware
10. Klix invokes the command handler
11. Klix emits `exit` and saves state on shutdown

That flow is implemented in `klix/app.py`. See [App](app.md).

## Subsystems

### App

`App` is the composition root. It owns:

- command registry
- middleware list
- event bus
- router
- state manager
- completer registration
- the main run loop

### Session

`Session` is the per-terminal runtime object passed into handlers. It contains:

- typed app state
- metadata about the terminal
- input history
- UI access through `session.ui`
- a background task registry

### Router

The router is responsible for:

- mapping a raw slash-command line to `ParsedCommand`
- resolving aliases
- validating arguments against `args_schema`

The parser is intentionally simple. It is not a full shell parser. See [Router](router.md).

### Event Bus

The event bus is a small ordered dispatcher. It supports both sync and async handlers and is used for lifecycle and input-related hooks.

### Middleware

Middleware wraps command dispatch. It runs after parsing and before the final handler. That means middleware can inspect `ctx.command`.

### Input Engine

The input engine is the thin prompt layer over `prompt_toolkit`. It owns:

- input mode
- prompt history
- key bindings
- CI fallback behavior

### UI Namespace

`session.ui` is the developer-facing convenience surface. It binds together:

- renderer-backed print/stream helpers
- `session.ui.input`
- `session.ui.output`
- `session.ui.layout`
- cursor helpers

## Why The Architecture Looks Like This

Klix is trying to be a framework, not a single-purpose tool. That pushes the architecture toward separation:

- routing is separate from input reading
- middleware is separate from command logic
- session state is separate from app registration
- rendering is separate from UI widgets

This is what lets the same framework support:

- generated starter CLIs
- command-driven demos like [`examples/minimal.py`](../examples/minimal.md)
- more custom flows like the Gemini-style chat demo in [`examples/chat_ai.py`](../examples/gemini-style-cli.md)

## Current Implementation Boundaries

The docs in this folder reflect the current code, which includes some intentional simplifications:

- the layout system redraws coarsely instead of maintaining a fully persistent screen model
- the event system exists for many event names, but only some events are actively emitted by `App.run()`
- command parsing is token-based, not shell-quote aware
- persistence is file-based JSON with a simple version field

These are not hidden footnotes. They affect how you should build with Klix today. Read:

- [Layout](layout.md)
- [Events](events.md)
- [Persistence](../guides/persistence.md)
- [FAQ](../faq.md)

## Common Mistakes

### Treating Klix like a full-screen TUI framework

Klix has layout regions, but the current implementation is still closer to a smart command-line runtime than a fully managed alternate-screen UI.

### Expecting middleware for plain text in custom loops automatically

If you build a custom interaction loop outside `App.run()`, you need to explicitly route command lines through the router and middleware if you want that behavior. 

### Ignoring the simple parser

If your command syntax needs shell-level quoting rules, nested subcommands, or highly flexible parsing, you should design around the current parser limits or extend the routing approach deliberately.
