# Middleware

Middleware wraps command execution in Klix. It is where you put behavior that should happen around handlers instead of inside them.

See also:

- [App](app.md)
- [Commands](commands.md)
- [Events](events.md)
- [Using Middleware](../guides/using-middleware.md)
- [Middleware Reference](../reference/middleware.md)

## Why Middleware Exists

Handlers should usually focus on one command's job. Middleware exists for concerns like:

- logging
- timing
- authorization
- request shaping
- common error-related behavior

That keeps handlers smaller and easier to reuse.

## The Middleware Context

Current middleware receives:

- `ctx.raw_input`
- `ctx.session`
- `ctx.command`
- `ctx.cancelled`

The current implementation parses commands before middleware runs, so `ctx.command` is available for command-aware decisions.

## Basic Example

```python
import time

@app.middleware
async def timing(ctx: klix.MiddlewareContext, next: klix.NextFn):
    start = time.time()
    await next(ctx)
    ctx.session.ui.print(f"{time.time() - start:.2f}s", color="muted", dim=True)
```

## Short-Circuiting

Middleware can stop dispatch by not calling `next()`:

```python
@app.middleware
async def auth(ctx: klix.MiddlewareContext, next: klix.NextFn):
    if ctx.command and ctx.command.name == "/deploy" and not ctx.session.state.authenticated:
        ctx.session.ui.print("Authentication required.", color="error")
        ctx.cancelled = True
        return

    await next(ctx)
```

## Order

Middleware runs in registration order:

```python
@app.middleware
async def first(ctx, next):
    print("first before")
    await next(ctx)
    print("first after")

@app.middleware
async def second(ctx, next):
    print("second before")
    await next(ctx)
    print("second after")
```

Flow:

```text
first before
second before
handler
second after
first after
```

The chain is built in reverse internally so the final execution order matches registration order.

## Middleware vs Events

Use middleware when:

- you need to wrap command execution
- you need access to parsed command data
- you want before/after behavior around handlers

Use events when:

- you want lifecycle hooks
- you want general notification behavior
- you do not need to wrap the dispatch flow itself

See [Events](events.md).

## Realistic Example

```python
@app.middleware
async def status_updates(ctx: klix.MiddlewareContext, next: klix.NextFn):
    if ctx.command:
        ctx.session.ui.layout.status.set(
            left="Running",
            right=ctx.command.name,
            color="muted",
        )
        ctx.session.ui.layout.redraw_ui()

    await next(ctx)

    ctx.session.ui.layout.status.set("Ready", "idle", color="muted")
    ctx.session.ui.layout.redraw_ui()
```

## Pitfalls

### Mutating too much shared state

Middleware is powerful, so it is easy to make command behavior hard to follow by hiding too much logic there.

### Forgetting `await next(ctx)`

If you intended wrapping behavior and forget to call `next()`, the handler will never execute.

### Expecting middleware for custom plain-text loops

If you build your own input loop outside `App.run()`, you must explicitly build and call the middleware chain yourself if you want the same behavior.
