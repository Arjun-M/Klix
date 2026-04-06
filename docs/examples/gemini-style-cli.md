# Example: AI Chat-Style CLI

The repository includes a chat-style demo at `examples/chat_ai.py`. It is the closest example to an AI assistant interface built with Klix primitives.

This page uses “Gemini-style” as a UX description, not as a model integration. The example is a local demo UI with fake assistant logic. It does not call external APIs.

## What This Example Demonstrates

The chat demo shows how to build a more conversational terminal experience with:

- normal text input as messages
- slash commands for control actions
- streamed assistant output
- a lightweight layout with header and status
- a custom loop built on Klix internals

That last point matters. The standard `App.run()` loop is command-oriented. This example shows how to bend the framework toward free-form chat while still using the same session, UI, middleware, and renderer layers.

## Why A Custom Loop Is Needed

The default app loop assumes slash commands are what should be parsed and routed. For a chat app, you usually want:

- plain text to become a message
- slash commands to remain available for actions like `/help` and `/clear`

`examples/chat_ai.py` handles that by:

1. creating a session manually
2. using the same `KlixCompleter`, renderer, input engine, and UI namespace as `App`
3. routing slash commands through the router and middleware
4. treating non-command input as chat text

This is a good example of Klix as a framework rather than just a prebuilt loop.

## Streaming Output

One of the most useful patterns in the example is streamed assistant text:

```python
session.ui.layout.main.print("Assistant: ", color="info", bold=True, end="")
await session.ui.stream(chunks(), color="text", end="\n\n")
```

This creates the feeling of live generation without building a real model backend.

See [Creating UI](../guides/creating-ui.md) for the general streaming pattern.

## Layout Pattern

The example uses Klix layout in the intended way:

- header for app identity
- status line for model/theme/detail
- main transcript for conversation history

It avoids trying to make the whole transcript a retained widget tree, which fits the current layout engine well.

## Fake Assistant Logic

The assistant behavior is intentionally simple:

- canned intelligent-looking phrasing
- question detection
- string transformations
- light topic-specific branching

That keeps the example focused on UX and flow rather than network integration.

## Commands In A Chat App

The demo keeps a few slash commands:

- `/help`
- `/clear`
- `/theme`
- `/exit`

This is a useful pattern for conversational CLIs in general. Plain text handles the primary experience; slash commands handle control and utility behavior.

## What To Learn From This Example

- You can use Klix without `app.run()` when the interaction model demands it.
- The session and UI objects are reusable outside the default loop.
- Middleware still adds value in custom flows.
- Streaming and layout are enough to make a terminal app feel polished.

## Common Pitfalls

- Assuming the default app loop can be used unchanged for free-form chat.
- Building a chat transcript entirely in layout state instead of printing to the main region.
- Forgetting that command parsing is still slash-based even inside a custom loop.

## Related Reading

- [Architecture](../concepts/architecture.md)
- [Input Engine](../concepts/input-engine.md)
- [UI](../concepts/ui.md)
