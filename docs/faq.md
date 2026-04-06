# FAQ

## Is Klix command-first or chat-first?

Command-first by default.

The built-in `App.run()` loop is built around slash commands. You can build chat-style flows on top of the same primitives, but that usually means writing a custom loop like `examples/chat_ai.py`.

See [Examples: Gemini-Style CLI](examples/gemini-style-cli.md).

## Why does the router not support shell-style quoting?

Because the current parser is intentionally simple. It splits on whitespace and hands typed validation to Pydantic. That keeps the routing layer small and predictable, but it also means quoted strings with spaces are not treated specially.

See [Router](concepts/router.md).

## Does Klix support subcommands?

Not as a first-class nested command tree.

The common pattern is to model subcommand-like behavior inside a single command’s argument schema or handler logic.

See [Adding Commands](guides/adding-commands.md).

## Why is there both middleware and events?

They solve different problems.

- middleware wraps command execution
- events observe lifecycle moments

If you need before/after behavior around a handler, use middleware. If you need startup, shutdown, or error hooks, use events.

See [Middleware](concepts/middleware.md) and [Events](concepts/events.md).

## Does Klix persist sessions automatically?

It can save state automatically when `persist_session=True`, but loading a prior session still requires a session identifier or custom resume logic. Save-on-exit and resume-on-start are related, but they are not the same feature.

See [Persistence](guides/persistence.md).

## Can I build a full-screen TUI with Klix?

You can build polished terminal apps with headers, status lines, widgets, and interactive prompts, but Klix is not a full retained-mode TUI framework. The layout system is intentionally coarse and works best for lightweight structure.

See [Layout](concepts/layout.md).

## Why is there no default `--help`?

The process-level parser is created with `add_help=False`. The current design expects command help to be handled at the app level, usually through a `/help` command and the built-in help generator.

See [Reference: Config](reference/config.md).

## Are rich widgets required?

No.

Klix prefers rich when the terminal supports it, but it ships fallback and CI renderers so apps still run in simpler environments. The visual result is reduced, but the app should remain usable.

See [Renderer](concepts/renderer.md).

## What should I put in `session.state`?

Put typed, session-scoped, serializable application state there:

- selected profile
- recent actions
- user preferences
- in-progress workflow data

Do not put renderer objects, prompt sessions, or random global caches there.

See [Working With State](guides/working-with-state.md).

## How should I think about `session.ui`?

As the main application-facing terminal API.

It is the place where input, output, layout, and streaming come together. Most app code should work through `session.ui` rather than importing lower-level renderer or input pieces directly.

See [UI](concepts/ui.md).

## What are the biggest current limitations?

The main ones are:

- command parsing is intentionally simple
- layout is lightweight, not full retained-mode UI
- persistence is basic and session-file oriented
- autocomplete is helpful but not schema-driven

These are tradeoffs, not accidents. Klix is trying to stay small and practical.

## What should I read first if I am new?

This order works well:

1. [Index](index.md)
2. [Installation](installation.md)
3. [Quickstart](quickstart.md)
4. [Architecture](concepts/architecture.md)
5. [Building Your First CLI](guides/building-your-first-cli.md)
