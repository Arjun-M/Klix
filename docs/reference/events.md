# Event Reference

Klix uses a simple ordered event bus. This page lists the lifecycle events that the current runtime emits and explains the expected handler shapes.

For guide-level examples, see [Handling Events](../guides/handling-events.md).

## Registering A Listener

```python
@app.on("start")
def on_start(session: klix.Session) -> None:
    session.ui.print("Ready.", color="accent")
```

Listeners can be sync or async.

## Events Emitted By The Main App Loop

### `start`

Emitted after the session, renderer, input engine, and UI are ready.

Typical handler arguments:

```python
def on_start(session: klix.Session) -> None:
    ...
```

Use it for:

- initial layout setup
- welcome messages
- startup summaries

### `input`

Emitted when raw input is received from the prompt loop.

Handler shape:

```python
def on_input(text: str, session: klix.Session) -> None:
    ...
```

Use it for:

- counters
- logging
- telemetry

### `command`

Emitted when a command has been parsed and is about to execute.

Handler shape:

```python
def on_command(cmd: klix.ParsedCommand, session: klix.Session) -> None:
    ...
```

Use it when you want visibility into command execution without middleware wrapping.

### `interrupt`

Emitted when the prompt loop catches `KeyboardInterrupt`.

Handler shape:

```python
def on_interrupt(session: klix.Session) -> None:
    ...
```

### `error`

Emitted when command execution raises an exception.

Handler shape:

```python
def on_error(error: Exception, session: klix.Session) -> None:
    ...
```

### `exit`

Emitted when the app is shutting down.

Handler shape:

```python
def on_exit(session: klix.Session) -> None:
    ...
```

## App-Specific Hooks

Some app code also uses named hooks such as `state_migration`. These are not emitted by the general command loop in the same way, but they are still registered through the same event system and consumed by other framework components.

That means the bus is generic even though the main loop only emits a small set of lifecycle events.

## Ordering

Listeners run in registration order.

If you register:

```python
@app.on("start")
def a(session): ...


@app.on("start")
def b(session): ...
```

`a` runs before `b`.

## Async Behavior

Async listeners are awaited in sequence. Klix does not fan them out in parallel.

That makes behavior predictable, but it also means a slow listener delays later listeners.

## Current Non-Emitted Names

You may see event names such as `resize`, `focus`, or `blur` mentioned in conceptual material. The event bus can represent them, but the current shipped app loop does not emit them automatically.

## Common Mistakes

- Using events when middleware would be a better fit for wrapping command execution.
- Doing heavy blocking work in sync listeners.
- Assuming every named event in the bus model is emitted by default.

## Related Reading

- [Reference: Middleware](middleware.md)
- [Concepts: Events](../concepts/events.md)
- [FAQ](../faq.md)
