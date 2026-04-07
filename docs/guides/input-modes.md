# Input Modes

Klix supports a small set of input modes through `InputMode`. They are used by the prompt engine and by higher-level input components.

For engine details, see [Input Engine](../concepts/input-engine.md). For the UI surface, see [UI](../concepts/ui.md).

## The Available Modes

The enum currently includes:

- `COMMAND`
- `MULTILINE`
- `SELECT`
- `SEARCH`
- `CONFIRM`
- `PASSWORD`
- `INTERRUPT`

These modes influence how the prompt session behaves:

- whether multiline input is allowed
- whether text is masked
- whether a yes/no answer is normalized to boolean

## The Default App Experience

The standard `App.run()` loop uses `COMMAND` mode for each prompt:

```python
session.input_engine.set_mode(klix.InputMode.COMMAND)
raw_input = await session.input_engine.prompt_async("> ")
```

That fits slash-command driven tools well.

## Switch Modes Explicitly

You can change the mode before calling the prompt engine directly:

```python
session.input_engine.set_mode(klix.InputMode.COMMAND)
note = await session.input_engine.prompt_async("Note: ")
```

Or let the higher-level helpers do it for you:

```python
note = await session.ui.input.text("Note")
password = await session.ui.input.secret("Password")
confirm = await session.ui.input.confirm("Proceed?", default=True)
```

Those helpers temporarily select the appropriate mode and manage the prompt details for you.

## Multiline Input

Use `MULTILINE` when you want a block of text:

```python
session.input_engine.set_mode(klix.InputMode.MULTILINE)
body = await session.input_engine.prompt_async("Body: ")
```

In interactive terminals:

- `Enter` submits the full block
- `Shift+Enter` inserts a newline only when the terminal exposes it distinctly
- `Escape` + `Enter` is the portable newline path Klix supports everywhere
- `Ctrl+J` also inserts a newline in terminals that emit line-feed directly

In CI or non-interactive mode, the fallback behavior is much simpler and reads a line from standard input.

## Confirm Mode

`CONFIRM` is special because the input engine normalizes the result to a boolean:

```python
session.input_engine.set_mode(klix.InputMode.CONFIRM)
approved = await session.input_engine.prompt_async("Proceed? [y/n]: ")
```

That low-level path is what the higher-level confirm component builds on.

## Password Mode

`PASSWORD` masks input through prompt-toolkit:

```python
session.input_engine.set_mode(klix.InputMode.PASSWORD)
secret = await session.input_engine.prompt_async("Password: ")
```

The higher-level `session.ui.input.secret(...)` helper also avoids storing the result in input history.

## When To Use Direct Engine Access

Use the raw engine only when:

- you need a custom prompt flow that the built-in components do not cover
- you are building an example or framework extension
- you want total control over prompt text and mode switching

For normal app code, prefer `session.ui.input.*`.

## Common Mistakes

- Assuming mode switching changes command routing. It only changes prompt behavior; your app loop still decides what input means.
- Expecting multiline editing in CI mode. The fallback path is intentionally simple.
- Forgetting to restore a previous mode if you manage prompt engine state manually in complex code.

## Related Reading

- [Autocomplete](autocomplete.md)
- [Components: Input](../components/input.md)
- [Examples: Gemini-Style CLI](../examples/gemini-style-cli.md)
