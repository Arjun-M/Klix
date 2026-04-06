# Using Middleware

Middleware lets you run logic around command execution without repeating the same code in every handler.

Use it for:

- logging
- authorization checks
- metrics
- temporary status updates
- command timing

For the architectural view, see [Middleware](../concepts/middleware.md). For the full request flow, see [Architecture](../concepts/architecture.md).

## The Middleware Shape

Klix middleware receives a `MiddlewareContext` and a `next` function:

```python
@app.middleware
async def log_commands(ctx: klix.MiddlewareContext, next: klix.NextFn) -> None:
    ctx.session.ui.print(f"[log] {ctx.command.name}", color="muted")
    await next(ctx)
```

The important detail is that `ctx.command` is already populated before middleware runs.

The runtime order is:

1. input is read
2. input is parsed into a command
3. middleware chain runs
4. the final handler is invoked

## Logging Middleware

This is the simplest useful pattern:

```python
@app.middleware
async def audit(ctx: klix.MiddlewareContext, next: klix.NextFn) -> None:
    ctx.session.ui.print(
        f"[audit] running {ctx.command.name} from raw input: {ctx.raw_input}",
        color="muted",
    )
    await next(ctx)
```

Why this belongs in middleware:

- every command gets it automatically
- command handlers stay focused on business behavior
- changing log format later is easy

## Authorization Middleware

Middleware is a good place to stop a command before the handler runs.

```python
@app.middleware
async def require_login(ctx: klix.MiddlewareContext, next: klix.NextFn) -> None:
    protected = {"/deploy", "/delete"}

    if ctx.command.name in protected and not ctx.session.state.logged_in:
        ctx.cancelled = True
        ctx.session.ui.print("Please log in first.", color="error")
        return

    await next(ctx)
```

Setting `ctx.cancelled = True` is the built-in signal that the chain should stop.

## Status Line Middleware

This pattern works well when you use layout regions:

```python
@app.middleware
async def status(ctx: klix.MiddlewareContext, next: klix.NextFn) -> None:
    ctx.session.ui.layout.status.set(
        left="busy",
        right=f"running {ctx.command.name}",
        color="muted",
    )
    ctx.session.ui.layout.redraw_ui()

    try:
        await next(ctx)
    finally:
        ctx.session.ui.layout.status.set("ready", "", color="muted")
        ctx.session.ui.layout.redraw_ui()
```

The `finally` block matters. Without it, an exception can leave the status bar in a stale state.

## Timing Middleware

```python
import time


@app.middleware
async def measure(ctx: klix.MiddlewareContext, next: klix.NextFn) -> None:
    started = time.perf_counter()
    try:
        await next(ctx)
    finally:
        elapsed_ms = (time.perf_counter() - started) * 1000
        ctx.session.ui.print(
            f"{ctx.command.name} finished in {elapsed_ms:.1f}ms",
            color="muted",
        )
```

This is more reliable than timing inside each command because it wraps the whole handler consistently.

## Ordering Matters

Middleware runs in registration order.

```python
@app.middleware
async def auth(ctx, next):
    ...


@app.middleware
async def metrics(ctx, next):
    ...
```

That means `auth` runs before `metrics`, and `metrics` wraps the handler only after `auth` passes control to it.

Think of it as nested wrappers:

```text
auth(metrics(handler))
```

## What Middleware Should Not Do

Avoid using middleware for:

- command-specific business logic
- heavy rendering that only one command needs
- parsing free-form text that is not a command

If the behavior only belongs to one handler, keep it in the handler.

## Common Mistakes

- Assuming middleware sees plain user text before routing. It only runs for successfully parsed commands in the main app loop.
- Forgetting to call `await next(ctx)` when you intend execution to continue.
- Swallowing exceptions silently. If you catch an error, either surface it or re-raise it.
- Updating layout regions without calling `redraw_ui()`.

## Related Reading

- [Handling Events](handling-events.md)
- [Creating UI](creating-ui.md)
- [Reference: Middleware](../reference/middleware.md)
