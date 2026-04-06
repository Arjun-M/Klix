# Example: Minimal

The repository’s `examples/minimal.py` file is the best place to start once you understand the core concepts. It shows a small but practical Klix app with commands, input helpers, output helpers, and custom completion.

Read it after [Quickstart](../quickstart.md) and [Building Your First CLI](../guides/building-your-first-cli.md).

## What This Example Demonstrates

The minimal example covers:

- typed session state
- simple commands
- argument validation with Pydantic
- interactive prompts
- rich output helpers
- custom autocomplete

That makes it a good reference for the “normal” Klix app shape.

## App Setup

The example defines a dataclass state model and attaches it to the app:

```python
@dataclass
class DemoState(klix.SessionState):
    last_prompt: str = ""
```

Then it creates:

```python
app = klix.App(
    name="Minimal",
    version="0.1.0",
    description="Small Klix example app.",
    state_schema=DemoState,
)
```

This is the standard entry point for nearly every Klix application.

## Command Examples

The example includes handlers that show several common patterns:

- plain session-only commands
- commands with typed arguments
- commands that ask follow-up questions interactively
- commands that render markdown or panels

That mix is useful because most real tools need all four.

## Interactive Input

One of the best parts of the minimal example is that it does not force everything through slash arguments. It uses `session.ui.input.*` for user-friendly prompts where that makes sense.

That is usually a better choice for:

- passwords
- yes/no approvals
- structured guided flows

See [Input Components](../components/input.md) for the full component list.

## Custom Completion

The example also adds a custom completer. This is the simplest way to improve usability for commands that take a predictable set of values.

That pattern is explained in [Autocomplete](../guides/autocomplete.md).

## What To Pay Attention To

When you read `examples/minimal.py`, focus on:

- how little code is required to register a command
- how session state is accessed directly
- how output helpers keep handlers readable
- how the example mixes command parsing and follow-up input cleanly

## Common Lessons From This Example

- Start with a small state model.
- Keep command handlers focused and short.
- Use validators and follow-up prompts where they improve the UX.
- Let `session.ui` be the main interface for terminal interaction.

## Related Reading

- [Commands](../concepts/commands.md)
- [Creating UI](../guides/creating-ui.md)
- [Reference: API](../reference/api.md)
