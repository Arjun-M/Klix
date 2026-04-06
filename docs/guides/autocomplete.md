# Autocomplete

Klix includes command and argument completion through `KlixCompleter`, built on top of prompt-toolkit.

This guide explains what you get automatically, how to add your own completions, and where the edges are. For the parser that consumes completed text, see [Router](../concepts/router.md).

## What Works Automatically

When the app starts, it creates a `KlixCompleter` with:

- all registered command names
- all registered aliases
- any custom completers you add

That means slash commands autocomplete out of the box.

If you register:

```python
@app.command("/deploy", aliases=["/ship"])
def deploy(session: klix.Session) -> None:
    ...
```

Typing `/de` or `/sh` will offer completions in an interactive terminal.

## Add Custom Argument Completion

Use the app helper for argument-specific completions:

```python
app.add_completer(
    "/deploy",
    lambda text, session: ["staging", "production", "preview"],
)
```

The callable receives:

- the current input text
- the active session

That gives you enough context to compute suggestions dynamically.

## Example: Environment-Aware Completion

```python
def environment_completer(text: str, session: klix.Session) -> list[str]:
    choices = ["staging", "production", "preview"]
    token = text.split()[-1] if text.split() else ""
    return [choice for choice in choices if choice.startswith(token)]


app.add_completer("/deploy", environment_completer)
```

Now typing:

```text
/deploy pr
```

can suggest `production` and `preview`.

## How Completion Is Chosen

At a high level:

1. If the first token looks like a command, Klix offers command and alias matches.
2. If there is a command-specific completer for that command, Klix also asks it for suggestions.
3. Suggestions are filtered against the current token.

This is intentionally simpler than a full shell completion engine. It works well for most app-level use cases.

## Fuzzy Matching

Command completion uses fuzzy matching behavior from prompt-toolkit where appropriate, so partial command prefixes work naturally.

The `session.ui.input.fuzzy(...)` widget is a separate feature. It provides an interactive selector for values during a command flow and does not replace prompt-level completion. See [Components: Input](../components/input.md).

## Practical Pattern

Autocomplete works best when combined with clear command design:

```python
@app.command("/logs", help="Show service logs")
def logs(session: klix.Session) -> None:
    ...


def logs_completer(text: str, session: klix.Session) -> list[str]:
    services = ["api", "worker", "scheduler"]
    token = text.split()[-1] if text.split() else ""
    return [service for service in services if service.startswith(token)]


app.add_completer("/logs", logs_completer)
```

That gives users both discovery and speed without making the parser more complex.

## Current Limitations

- Completion is not schema-driven. Klix does not inspect Pydantic fields to build suggestions automatically.
- The parser is still whitespace-based, so completion does not imply shell-like quoting support.
- CI and non-interactive environments do not expose the full prompt-toolkit completion experience.

## Common Mistakes

- Returning huge unfiltered suggestion lists. Filter against the active token when possible.
- Assuming custom completers run for aliases separately. They are attached to the registered command name you provide.
- Treating completion as validation. The router and schema validation still decide what is legal.

## Related Reading

- [Adding Commands](adding-commands.md)
- [Concepts: Router](../concepts/router.md)
- [Reference: API](../reference/api.md)
