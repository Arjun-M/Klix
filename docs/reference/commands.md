# Command Reference

This page describes the command model as it exists in the current Klix implementation.

For tutorial-style usage, see [Adding Commands](../guides/adding-commands.md). For parser behavior, see [Router](../concepts/router.md).

## Registration

Register commands with `@app.command(...)`:

```python
@app.command("/status", help="Show current status")
def status(session: klix.Session) -> None:
    session.ui.print("Healthy.", color="success")
```

Arguments accepted by the decorator:

- `name`: required slash-prefixed command name
- `help`: optional help text
- `aliases`: optional list of alternate names
- `args_schema`: optional Pydantic model for typed arguments

## Handler Signatures

Supported handler shapes are:

```python
def handler(session: klix.Session) -> None:
    ...


def handler(args: SomeSchema, session: klix.Session) -> None:
    ...


async def handler(session: klix.Session) -> None:
    ...


async def handler(args: SomeSchema, session: klix.Session) -> None:
    ...
```

If an argument schema is present, Klix passes the parsed schema instance as the first argument.

## Aliases

Aliases register additional command names that resolve to the same `Command` object.

Example:

```python
@app.command("/deploy", aliases=["/ship"])
def deploy(session: klix.Session) -> None:
    ...
```

Autocomplete and help generation can include alias names.

## Argument Parsing Model

The command router uses a simple tokenization strategy:

- split input on whitespace
- first token is the command name
- remaining tokens become positionals or flags

Flags:

- `--flag value`
- `--boolean-flag`

Positionals are mapped in the schema field declaration order.

## Validation

Validation is delegated to Pydantic.

When validation fails, Klix raises `ArgValidationError` for field-level issues or surfaces the underlying parse failure through the command execution flow.

## Help Generation

`app.generate_help()` formats registered commands, aliases, and argument placeholders into a readable help listing.

Typical pattern:

```python
@app.command("/help", help="Show commands")
def help_cmd(session: klix.Session) -> None:
    session.ui.output.panel(app.generate_help(), title="Commands")
```

## Built-In Behavior

The main app loop treats these specially:

- `/exit`
- `/quit`

Those are handled by the loop itself to terminate the session cleanly.

`/help` is not built in as behavior. You should register it yourself if you want a help command.

## Current Limitations

- no nested subcommand router
- no shell-quote aware parser
- no schema-driven autocomplete generation
- no built-in command groups beyond naming conventions

These are design constraints, not bugs. Klix keeps the routing layer intentionally small.

## Common Mistakes

- Forgetting the slash prefix.
- Expecting quoted strings with spaces to parse as one argument.
- Using aliases that conflict with another command’s primary name.
- Hiding essential usage details in code instead of `help` text.

## Related Reading

- [Reference: API](api.md)
- [Reference: Middleware](middleware.md)
- [FAQ](../faq.md)
