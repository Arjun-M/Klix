# Error Reference

Klix defines a small set of framework-level exceptions. Most apps do not need to raise all of them directly, but understanding what they mean helps when you build custom flows or debugging tools.

## `KlixError`

Base class for framework exceptions.

If you need to catch “framework-specific” errors broadly, catch this type.

## `CommandNotFoundError`

Raised when the router cannot resolve the first token to a registered command or alias.

Typical cause:

- user typed an unknown slash command

The default app loop catches this and prints an error line.

## `ArgValidationError`

Raised when parsed arguments do not satisfy the command schema.

Constructor fields:

- `field`
- `message`

String form:

```text
Validation failed for field '<field>': <message>
```

Use this when you need structured command argument failure reporting.

## `InputCancelledError`

Raised when an interactive input component is cancelled rather than completed.

Most common sources:

- `select(...)`
- `multiselect(...)`
- `fuzzy(...)`

If cancellation is part of your normal UX, catch it and respond cleanly.

## `SessionStateError`

Used for session state and persistence-related failures.

This is the right category when serialization, reconstruction, or state integrity fails.

## `MiddlewareAbortError`

Represents middleware-aborted execution. The current middleware pattern usually relies on `ctx.cancelled` and early returns instead of explicitly raising this, but the type exists in the public error surface.

## `RenderError`

Used for rendering failures or renderer-specific issues.

## `CompatibilityError`

Used when terminal or environment compatibility checks fail.

This is more relevant to renderer-selection and environment adaptation code than to normal app handlers.

## Practical Error Handling Pattern

```python
from klix import InputCancelledError


@app.command("/wizard", help="Run interactive setup")
async def wizard(session: klix.Session) -> None:
    try:
        choice = await session.ui.input.select(
            ["staging", "production"],
            label="Choose target",
        )
    except InputCancelledError:
        session.ui.print("Setup cancelled.", color="warning")
        return

    session.ui.print(f"Selected {choice}", color="success")
```

## Common Mistakes

- Catching raw `Exception` everywhere instead of handling framework-level failures deliberately.
- Treating `CommandNotFoundError` as a fatal application error in custom loops.
- Forgetting that cancellation is not necessarily an error from the user’s perspective.

## Related Reading

- [Reference: Commands](commands.md)
- [Reference: Middleware](middleware.md)
- [FAQ](../faq.md)
