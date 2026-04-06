# State

Klix encourages typed session state instead of a global mutable dictionary.

See also:

- [Session](session.md)
- [App](app.md)
- [Working with State](../guides/working-with-state.md)
- [Persistence](../guides/persistence.md)

## Why State Exists

A CLI app almost always needs to remember things across commands:

- authentication status
- selected environment
- counters
- cached choices
- UI preferences

Klix stores that on `session.state`.

## Typed State

The current pattern is to subclass `SessionState`, usually with a dataclass:

```python
from dataclasses import dataclass
import klix

@dataclass
class ToolState(klix.SessionState):
    authenticated: bool = False
    profile: str = "default"
    runs: int = 0

app = klix.App(name="tool", state_schema=ToolState)
```

Then use it in handlers:

```python
@app.command("/login", help="Log in")
def login(session: klix.Session):
    session.state.authenticated = True
    session.state.runs += 1
```

## Why Typed State Is Better Than A Dict Here

- attribute access is clearer
- editors can autocomplete fields
- the state shape stays visible in one place
- persistence code can reason about dataclass state directly

## How State Is Created

When a session starts, Klix asks `SessionStateManager` for the state instance. That manager:

- instantiates your `state_schema`
- optionally loads a saved file
- optionally applies a `state_migration` hook

See [Persistence](../guides/persistence.md).

## Realistic Example

```python
from dataclasses import dataclass, field

@dataclass
class DeployState(klix.SessionState):
    authenticated: bool = False
    history: list[str] = field(default_factory=list)
    theme: str = "default"

@app.command("/record", help="Record a value")
def record(session: klix.Session):
    session.state.history.append("deploy")
    session.ui.output.json({"history": session.state.history})
```

## State Migration

The current persistence manager checks for a `state_migration` event when loading:

```python
@app.on("state_migration")
def migrate(old_version: int, raw_state: dict) -> dict:
    if old_version < 2 and "user_name" in raw_state:
        raw_state["username"] = raw_state.pop("user_name")
    return raw_state
```

Current notes:

- the version is currently always written as `1`
- migration handling is synchronous in the current implementation

That is important if you plan long-lived persisted state.

## Pitfalls

### Using mutable defaults without `field(default_factory=...)`

For lists and dicts, use dataclass factories:

```python
from dataclasses import dataclass, field

@dataclass
class GoodState(klix.SessionState):
    items: list[str] = field(default_factory=list)
```

### Storing non-serializable runtime objects

If you turn on persistence, state should stay JSON-friendly or at least easily transformed by your own conventions.

### Expecting app-wide shared state

Klix state is session-scoped, not process-global shared state.
