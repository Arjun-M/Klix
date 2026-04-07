# Configuration Reference

Klix has two main configuration layers:

- app configuration through `App` and `AppConfig`
- process arguments through `CLIArgsParser`

This page documents both.

## App Configuration

When you create an app:

```python
app = klix.App(
    name="OpsTool",
    version="1.0.0",
    description="Operations helper",
    state_schema=OpsState,
    persist_session=True,
    theme=klix.ThemeConfig(...),
)
```

You are effectively populating `AppConfig`.

Current high-level fields:

- `name`
- `version`
- `description`
- `theme`
- `config`
- `persist_session`
- `session_id`
- `state_schema`

## `name`

Used for:

- CLI program identity
- help output
- persistence directory naming
- terminal metadata

Choose something stable. Renaming the app changes where persisted sessions are stored.

## `version`

Used by:

- `--version` process argument
- startup displays if your app shows it
- metadata

## `description`

Used by:

- argument parser description
- your own help and documentation

## `state_schema`

Dataclass type used to construct `session.state`.

Example:

```python
@dataclass
class AppState(klix.SessionState):
    current_profile: str = "default"
```

## `persist_session`

Boolean toggle for session state persistence.

When enabled:

- the app constructs a `SessionStateManager`
- state is saved on exit

See [Persistence](../guides/persistence.md).

## `session_id`

Optional identifier used to load a persisted session file through the state manager.

If you want deterministic resumes, you need to provide or manage this value in your own app flow.

## `theme`

`ThemeConfig` instance controlling semantic colors.

See [Theming](../guides/theming.md).

Useful recent additions:

- `input_background`
- `input_text_color`

Example:

```python
theme=klix.ThemeConfig(
    accent="#4F8CFF",
    input_background="#171B24",
    input_text_color="#F5F7FA",
)
```

## `config`

`AppConfig` controls runtime prompt behavior that is not part of the semantic theme.

Current fields:

- `history_path`
- `log_path`
- `clear_input_on_submit`
- `max_history_size`

Example:

```python
config=klix.AppConfig(
    clear_input_on_submit=True,
    max_history_size=100,
)
```

`clear_input_on_submit` is opt-in and clears the visible prompt line after submit without affecting command execution.

`max_history_size` limits per-session command history used by Up/Down navigation.

## CLI Process Arguments

Klix wraps `argparse` in `CLIArgsParser`.

Built-in arguments:

- `-v`, `--version`
- `--config`
- `--debug`

Example:

```python
args = app._cli_args.parse_args()
```

The default `App` setup already creates this parser for you.

## About `--help`

The parser is currently created with `add_help=False`.

That means:

- `argparse` does not inject a default `--help`
- command help is expected to be handled at the app level, usually with a `/help` command

This is an intentional design choice in the current codebase, but it can surprise users who expect standard process-level help behavior.

## Adding Custom Process Arguments

`CLIArgsParser` exposes passthrough methods:

- `add_argument(...)`
- `add_argument_group(...)`

This is useful when your app needs startup flags before the interactive loop begins.

## Common Mistakes

- Confusing process arguments with slash commands. `--debug` is for process startup; `/debug` would be a command if you register it.
- Renaming the app after shipping persistence to users.
- Assuming persistence and session resume are the same thing.

## Related Reading

- [Installation](../installation.md)
- [Reference: API](api.md)
- [FAQ](../faq.md)
