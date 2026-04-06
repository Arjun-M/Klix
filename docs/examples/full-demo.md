# Example: Full Demo

The repository’s `examples/full_demo.py` file is the broadest walkthrough of the framework. It pulls together most of the major features in one place.

Use it when you want to see how Klix behaves as a more complete application rather than a minimal sketch.

## What This Example Demonstrates

The full demo shows:

- typed session state with persistence enabled
- startup and shutdown events
- middleware that wraps command execution
- layout regions for header and status
- structured output widgets
- interactive input components
- background tasks
- a state migration hook

It is the closest thing in the repository to a framework tour by example.

## Why This Example Matters

A lot of Klix’s value is not in any single feature. It comes from how the pieces work together:

- the `App` creates the runtime
- the `Session` carries state and UI
- the router parses command input
- middleware wraps handlers
- events let you hook the lifecycle
- widgets make the CLI feel intentional instead of raw

`examples/full_demo.py` is where all of that becomes visible at once.

## Key Patterns To Notice

### Layout-first startup

The example clears the screen, sets a header and status line, redraws the layout, and then prints normal output. That is the right order when you want a polished startup experience.

See [Layout](../concepts/layout.md).

### Middleware for cross-cutting behavior

The example updates status before and after command execution in middleware rather than repeating that code in every handler.

See [Using Middleware](../guides/using-middleware.md).

### State migration for persisted apps

Because the app enables persistence, it also includes a migration hook. That is an important production habit even in a lightweight framework.

See [Persistence](../guides/persistence.md).

### Background work through the session

The demo uses session-managed tasks for work that should outlive a single handler call but still belong to the active session.

See [Session](../concepts/session.md).

## Practical Takeaways

If you are building a real internal CLI, this example is a better starting point than the minimal example because it already includes:

- status management
- persistence
- richer UI patterns
- more realistic command structure

The tradeoff is that it is a lot to absorb at once, so read it after the concept pages.

## Pitfalls It Helps You Avoid

- forgetting to redraw the layout after changing regions
- putting cross-cutting behavior into command handlers
- storing ad hoc global state outside the session
- treating rich output as the only supported path instead of accounting for fallback renderers

## Related Reading

- [State](../concepts/state.md)
- [Middleware](../concepts/middleware.md)
- [Components: Widgets](../components/widgets.md)
