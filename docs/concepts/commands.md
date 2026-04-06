# Commands

Commands are the primary interaction model in the default Klix runtime. A command is an object with a name, optional aliases, optional argument schema, and a handler.

See also:

- [App](app.md)
- [Router](router.md)
- [Command Reference](../reference/commands.md)
- [Adding Commands](../guides/adding-commands.md)

## Why Commands Exist

Command objects give Klix a stable thing to register, route, validate, autocomplete, and document.

If commands were only decorators with implicit behavior, features like help generation and alias handling would be harder to keep consistent.

## Two Ways To Define Commands

### Decorator style

```python
import klix

app = klix.App(name="mytool")

@app.command("/hello", help="Say hello")
def hello(session: klix.Session):
    session.ui.print("Hello.", color="success")
```

### Explicit object style

```python
from pydantic import BaseModel
import klix

class DeployArgs(BaseModel):
    env: str

def deploy(args: DeployArgs, session: klix.Session):
    session.ui.print(f"Deploying {args.env}")

deploy_command = klix.Command(
    name="/deploy",
    help="Deploy an environment",
    args_schema=DeployArgs,
    handler=deploy,
)

app.register(deploy_command)
```

The implementation stores the same `Command` object either way.

## Command Shape

Current command fields:

- `name`
- `handler`
- `help`
- `aliases`
- `args_schema`

`args_schema` is optional. If you omit it, the handler only needs a `session`.

## Handlers With Schema Arguments

When `args_schema` is present, Klix validates input first and passes the resulting model instance into the handler:

```python
from pydantic import BaseModel

class CreateArgs(BaseModel):
    name: str
    force: bool = False

@app.command("/create", help="Create an item", args_schema=CreateArgs)
def create(args: CreateArgs, session: klix.Session):
    session.ui.print(f"name={args.name}, force={args.force}")
```

## Aliases

Aliases are stored in the same lookup table as canonical names:

```python
@app.command("/deploy", aliases=["/d"], help="Deploy the app")
def deploy(session: klix.Session):
    session.ui.print("Deploying")
```

The router normalizes aliases back to the canonical command name before middleware and handlers see them. That means middleware can check `ctx.command.name == "/deploy"` even if the user typed `/d`.

## Help Generation

The current `HelpGenerator` builds help text from registered command objects:

```python
session.ui.print(app.generate_help(), color="dim")
```

This is why clear `help=` text matters.

## Realistic Example

```python
from dataclasses import dataclass
from pydantic import BaseModel
import klix

@dataclass
class ReleaseState(klix.SessionState):
    releases: int = 0

class ReleaseArgs(BaseModel):
    environment: str
    tag: str = "latest"
    force: bool = False

app = klix.App(name="releasectl", state_schema=ReleaseState)

@app.command("/release", aliases=["/r"], args_schema=ReleaseArgs, help="Create a release")
def release(args: ReleaseArgs, session: klix.Session):
    session.state.releases += 1
    session.ui.output.panel(
        f"Release #{session.state.releases}\n"
        f"environment={args.environment}\n"
        f"tag={args.tag}\n"
        f"force={args.force}",
        title="Release Started",
        border_color="accent",
    )
```

## Current Limitations

### Parser simplicity

Commands are parsed by splitting on whitespace and identifying `-x` and `--flag` prefixes. There is no shell-quote aware parsing in the current implementation.

### Dispatch style

The default runtime expects slash-command input. Plain text only works automatically if you build a custom loop, as shown in [Gemini-Style CLI](../examples/gemini-style-cli.md).

## Common Mistakes

### Using spaces that rely on shell quoting

This will not behave like a full shell parser. Prefer simple tokens or build explicit parsing rules in your handler.

### Checking aliases in middleware

Check canonical command names after parsing, not raw alias strings.

### Forgetting help text

If you skip `help=...`, generated help output becomes less useful very quickly.
