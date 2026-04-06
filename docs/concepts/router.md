# Router

The router is responsible for turning raw slash-command text into structured command data and validating arguments against schemas.

See also:

- [Commands](commands.md)
- [Middleware](middleware.md)
- [Adding Commands](../guides/adding-commands.md)

## Why The Router Exists

Handlers should not need to re-parse command text manually. The router gives the rest of the framework one consistent parsed representation:

- command name
- positional values
- flags
- raw text

That representation is `ParsedCommand`.

## How Parsing Works Today

The current parser:

- splits the line on whitespace
- treats the first token as the command name
- resolves aliases to the canonical command name
- treats `--flag value` or `-f value` as flag/value pairs
- treats standalone flags as boolean `True`
- collects everything else as positional args

Example:

```text
/deploy prod --force
```

Becomes:

```python
ParsedCommand(
    name="/deploy",
    positional=["prod"],
    flags={"force": True},
    raw="/deploy prod --force",
)
```

## Validation

If a command defines `args_schema`, the router maps the parsed values into that schema:

```python
from pydantic import BaseModel

class DeployArgs(BaseModel):
    env: str
    force: bool = False
```

For `/deploy prod --force`, validation produces:

```python
DeployArgs(env="prod", force=True)
```

## Positional Mapping Rules

Positional args are assigned to schema fields that are still missing after flags are applied, in schema declaration order.

That makes simple commands ergonomic, but it is also one of the places where the router stays intentionally simple.

## Current Limitations

### No shell-quote aware parsing

This is the big one. The router splits on whitespace, so:

```text
/say hello world
```

becomes two positionals, not one quoted string.

### No nested command language

There is no built-in subcommand tree parser.

### Flag parsing is basic

Flags are good enough for common `--name value` and `--flag` cases, but not for complex CLI grammar.

## Realistic Example

```python
from pydantic import BaseModel

class RunArgs(BaseModel):
    task: str
    retries: int = 0
    dry_run: bool = False

@app.command("/run", args_schema=RunArgs, help="Run a task")
def run(args: RunArgs, session: klix.Session):
    session.ui.output.json(
        {
            "task": args.task,
            "retries": args.retries,
            "dry_run": args.dry_run,
        }
    )
```

Input:

```text
/run build --retries 2 --dry_run
```

## Pitfalls

### Designing commands that depend on advanced shell syntax

If your UX depends on quoting, embedded whitespace, or repeated flag groups, the current router will be too small for that design.

### Forgetting canonical names in middleware

Parsed commands use the canonical name after alias resolution.

### Treating parser simplicity as a bug instead of a design constraint

Klix is not trying to replace a full shell parser. Keep commands readable and direct.
