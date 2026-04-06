# Events

Events are Klix's lifecycle and notification hook system. They are simpler than middleware and broader in scope.

See also:

- [App](app.md)
- [Middleware](middleware.md)
- [Handling Events](../guides/handling-events.md)
- [Event Reference](../reference/events.md)

## Why Events Exist

Some behavior should happen because something occurred, not because you are wrapping a command. Examples:

- app started
- app is exiting
- a line of input was received
- a command is about to dispatch
- an error occurred

That is what the event bus is for.

## Current Event Model

The event bus is:

- in-process
- ordered
- sync/async aware
- minimal by design

Listeners are stored per event name and run in registration order.

## Registering Events

```python
@app.on("start")
def on_start(session: klix.Session):
    session.ui.print("Started.", color="accent")
```

Async listeners work too:

```python
@app.on("start")
async def warmup(session: klix.Session):
    ...
```

## Events Actively Emitted Today

The current runtime emits these directly from `App.run()` or command dispatch:

- `start`
- `input`
- `command`
- `interrupt`
- `error`
- `exit`

Persistence also checks for `state_migration` handlers when loading persistent state.

## Events Named In The Spec But Not Fully Emitted Today

The framework design mentions events like:

- `resize`
- `focus`
- `blur`

Those names can be registered, but the current runtime loop does not actively emit them yet.

Documenting that clearly matters because it changes how you should use the API in production.

## Event Flow Example

For a command like `/deploy prod`, the runtime roughly does this:

1. emit `start` once at app startup
2. emit `input` with the raw line
3. parse the command
4. run middleware
5. emit `command` during dispatch
6. run the handler
7. emit `exit` on shutdown

## Realistic Example

```python
@app.on("start")
def on_start(session: klix.Session):
    session.ui.layout.header.set("Deploy CLI", color="accent")
    session.ui.layout.status.set("Ready", "Use /help", color="muted")
    session.ui.layout.redraw_ui()

@app.on("input")
def on_input(text: str, session: klix.Session):
    session.ui.print(f"received: {text}", color="muted", dim=True)

@app.on("command")
def on_command(cmd: klix.ParsedCommand, session: klix.Session):
    session.ui.layout.status.set("Running", cmd.name, color="muted")
    session.ui.layout.redraw_ui()

@app.on("exit")
def on_exit(session: klix.Session):
    session.ui.print("Shutting down.", color="muted")
```

## Events vs Middleware

If you need before/after command behavior, use middleware.

If you need notification-style hooks, use events.

A good rule:

- middleware changes flow
- events observe flow

## Pitfalls

### Assuming every spec event is emitted

Stick to the events currently emitted by the runtime unless you are deliberately extending the core.

### Putting business logic entirely in events

Events are useful for side effects, but core command behavior usually belongs in handlers or middleware.
