# Middleware Reference

Middleware in Klix wraps command execution after parsing and before the handler runs.

For design guidance, see [Using Middleware](../guides/using-middleware.md). This page focuses on the exact runtime contract.

## Registration

Register middleware with `@app.middleware`:

```python
@app.middleware
async def log(ctx: klix.MiddlewareContext, next: klix.NextFn) -> None:
    ctx.session.ui.print(f"running {ctx.command.name}", color="muted")
    await next(ctx)
```

## `MiddlewareContext`

Fields:

- `raw_input`: the original command text
- `session`: the active `Session`
- `command`: the parsed `ParsedCommand`
- `cancelled`: boolean signal to stop execution

`command` is available before middleware runs. That is an important part of the current architecture.

## `NextFn`

`next` is the continuation that advances the chain.

If middleware should allow the command to continue, it must call:

```python
await next(ctx)
```

If middleware should stop the command, it can:

- return early
- set `ctx.cancelled = True`
- optionally print an error or warning message

## Execution Order

Middleware runs in registration order.

Given:

```python
@app.middleware
async def a(ctx, next): ...


@app.middleware
async def b(ctx, next): ...
```

The effective nesting is:

```text
a(b(handler))
```

## Sync Middleware

The middleware chain expects async callables. In practice, define middleware as `async def` even if it only does synchronous work.

## Typical Patterns

### Logging

```python
@app.middleware
async def audit(ctx, next):
    ctx.session.ui.print(f"[audit] {ctx.raw_input}", color="muted")
    await next(ctx)
```

### Authorization

```python
@app.middleware
async def require_login(ctx, next):
    if ctx.command.name == "/deploy" and not ctx.session.state.logged_in:
        ctx.cancelled = True
        ctx.session.ui.print("Please log in first.", color="error")
        return
    await next(ctx)
```

### Status updates

```python
@app.middleware
async def status(ctx, next):
    ctx.session.ui.layout.status.set("busy", ctx.command.name, color="muted")
    ctx.session.ui.layout.redraw_ui()
    try:
        await next(ctx)
    finally:
        ctx.session.ui.layout.status.set("ready", "", color="muted")
        ctx.session.ui.layout.redraw_ui()
```

## Current Scope

Middleware applies to command execution. It is not a general-purpose pipeline for every keystroke or every UI action in the framework.

If you build a custom loop, you can still reuse the middleware chain directly, as the chat example does.

## Common Mistakes

- Forgetting `await next(ctx)`.
- Assuming middleware sees non-command text in the default app loop.
- Catching errors and swallowing them without logging or re-raising.

## Related Reading

- [Reference: Commands](commands.md)
- [Examples: Gemini-Style CLI](../examples/gemini-style-cli.md)
- [Concepts: Middleware](../concepts/middleware.md)
