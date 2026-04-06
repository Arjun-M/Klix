# Working With State

Klix encourages typed session state. Instead of passing dictionaries through your app, you define a state model once and then mutate it through the `Session`.

This guide covers the day-to-day patterns. For the persistence model, see [State](../concepts/state.md). For the session object itself, see [Session](../concepts/session.md).

## Define A Typed State Object

Use a dataclass that extends `SessionState`.

```python
from dataclasses import dataclass, field

import klix


@dataclass
class TodoState(klix.SessionState):
    items: list[str] = field(default_factory=list)
    current_filter: str = "all"
```

Attach it to the app:

```python
app = klix.App(
    name="TodoCLI",
    version="0.1.0",
    description="Task tracker",
    state_schema=TodoState,
)
```

Now every session gets a `TodoState` instance at `session.state`.

## Read And Mutate State In Commands

```python
@app.command("/add", help="Add an item")
def add(session: klix.Session) -> None:
    session.state.items.append("Write docs")
    session.ui.print("Added item.", color="success")


@app.command("/list", help="Show items")
def list_items(session: klix.Session) -> None:
    if not session.state.items:
        session.ui.print("No items yet.", color="muted")
        return

    for index, item in enumerate(session.state.items, start=1):
        session.ui.print(f"{index}. {item}", color="text")
```

There is no separate store abstraction in normal use. The `Session` is the state boundary.

## Use State For UI Synchronization

State becomes more useful when it drives layout and rendering:

```python
@app.on("start")
def on_start(session: klix.Session) -> None:
    session.ui.layout.header.set("TodoCLI", color="accent")
    session.ui.layout.status.set(
        left=f"items: {len(session.state.items)}",
        right=f"filter: {session.state.current_filter}",
        color="muted",
    )
    session.ui.layout.redraw_ui()
```

After mutations, update the layout again.

## Persist State Between Runs

Enable persistence on the app:

```python
app = klix.App(
    name="TodoCLI",
    version="0.1.0",
    description="Task tracker",
    state_schema=TodoState,
    persist_session=True,
)
```

Klix serializes dataclass state to JSON and stores it under:

```text
~/.klix/sessions/<app-name>/<session-id>.json
```

That persistence layer is intentionally simple:

- dataclass state only
- JSON serialization
- per-session file storage
- optional migration hook

See [Persistence](persistence.md) for the full workflow.

## Use A Migration Hook When State Changes

If you evolve the state shape, register a migration function:

```python
@app.on("state_migration")
def migrate_state(data: dict) -> dict:
    if "active_filter" in data and "current_filter" not in data:
        data["current_filter"] = data.pop("active_filter")
    return data
```

The state manager applies this hook before reconstructing the dataclass from saved JSON.

## Store Only Session-Scoped Data

Good state candidates:

- current user
- selected environment
- UI preferences
- recent operations
- cached form values

Bad state candidates:

- global module caches
- renderer instances
- input engine internals
- background task handles

Those belong elsewhere. `Session.state` should stay serializable and easy to reason about.

## Use Default Factories Carefully

Mutable defaults should use `field(default_factory=...)`:

```python
@dataclass
class BuildState(klix.SessionState):
    recent_builds: list[str] = field(default_factory=list)
```

Do not write:

```python
recent_builds: list[str] = []
```

That creates shared mutable state at the class level.

## Common Mistakes

- Treating state like an untyped bag. Typed fields are one of the main benefits of Klix.
- Storing objects that cannot be serialized if persistence is enabled.
- Forgetting that persistence is per session file, not a single global `latest.json`.
- Assuming persistence auto-loads without a session identifier. Save and load are separate concerns in the current implementation.

## Related Reading

- [Persistence](persistence.md)
- [Reference: Config](../reference/config.md)
- [Concepts: State](../concepts/state.md)
