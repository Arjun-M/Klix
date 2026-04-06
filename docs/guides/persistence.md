# Persistence

Klix can persist session state to disk. The implementation is intentionally lightweight: dataclass state becomes JSON, stored per session, and optionally migrated before reload.

This guide focuses on practical usage. For the underlying model, see [State](../concepts/state.md).

## Enable Persistence

Set `persist_session=True` when creating the app:

```python
app = klix.App(
    name="ReleaseTool",
    version="0.1.0",
    description="Deployment workflow helper",
    state_schema=ReleaseState,
    persist_session=True,
)
```

That tells the app to:

- create a `SessionStateManager`
- save the current session state on exit

## Where Files Are Stored

Klix writes state files to:

```text
~/.klix/sessions/<app-name>/<session-id>.json
```

Example:

```text
~/.klix/sessions/ReleaseTool/55fceba3-10da-4eb5-b3c2-18e76e7ef1e7.json
```

The app name becomes the directory name. Each session gets its own file.

## What Is Saved

The current implementation saves:

- `session_id`
- `version`
- serialized dataclass state
- basic metadata snapshot

The state payload comes from `dataclasses.asdict(state)`.

That means persisted state should stay simple and JSON-friendly.

## Loading A Session

The state manager can load a session when you provide a session identifier through app configuration or your own startup flow.

The important implementation detail is this:

- enabling persistence alone guarantees save-on-exit
- loading requires a known `session_id`

If your app wants “resume the latest session” behavior, you need to implement that policy yourself on top of the provided manager.

## Add A Migration Hook

When your state model changes, register a migration function:

```python
@app.on("state_migration")
def migrate_state(data: dict) -> dict:
    if "profile" in data and "active_profile" not in data:
        data["active_profile"] = data.pop("profile")

    data.setdefault("recent_runs", [])
    return data
```

Klix calls this hook before reconstructing the dataclass.

Why this matters:

- old session files do not have to break new releases
- migrations stay close to app code
- you can evolve your state model gradually

## Practical Example

```python
from dataclasses import dataclass, field

import klix


@dataclass
class ReleaseState(klix.SessionState):
    active_profile: str = "default"
    recent_runs: list[str] = field(default_factory=list)


app = klix.App(
    name="ReleaseTool",
    version="0.2.0",
    description="Deployment workflow helper",
    state_schema=ReleaseState,
    persist_session=True,
)


@app.on("state_migration")
def migrate_state(data: dict) -> dict:
    if "profile" in data and "active_profile" not in data:
        data["active_profile"] = data.pop("profile")
    data.setdefault("recent_runs", [])
    return data
```

## Limitations To Understand

- Version handling is minimal. The current state manager writes a version field, but migration decisions are still up to your hook.
- There is no built-in “list sessions” or “resume latest” command.
- Persistence is focused on dataclass state, not on full replayable transcripts.

Those constraints keep the framework small, but they are important when you plan a real tool.

## Common Mistakes

- Storing renderer or input engine objects in persisted state.
- Assuming persistence automatically restores previous sessions with no identifier.
- Writing migration hooks that mutate to a shape your dataclass still cannot accept.

## Related Reading

- [Working With State](working-with-state.md)
- [Reference: Config](../reference/config.md)
- [Examples: Full Demo](../examples/full-demo.md)
