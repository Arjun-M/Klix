# Contributing to Klix

Thanks for taking the time to contribute. Klix is intentionally small, so well-scoped improvements can have a clear impact quickly. The goal is to keep the framework practical, readable, and easy to build on.

## What Klix Is Trying To Be

Klix is a Python framework for building interactive CLI applications. It is not trying to become a giant terminal platform or a kitchen-sink dependency tree.

Good contributions usually make one of these areas better:

- framework ergonomics
- reliability
- documentation
- examples
- packaging and release quality

## Local Setup

Clone the repository and create a virtual environment:

```bash
git clone <repo-url>
cd klix
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

If you want a clean dev environment with test tooling available:

```bash
python -m pip install -e .
python -m pip install pytest
```

## Running Tests

Run the test suite from the repository root:

```bash
python -m pytest -q
```

Before opening a pull request, also sanity-check the shipped examples:

```bash
python examples/minimal.py
python examples/full_demo.py
python examples/chat_ai.py
python examples/ui_showcase.py
```

For non-interactive smoke checks, piping `/exit` is usually enough:

```bash
printf '/exit\n' | python examples/minimal.py
printf '/exit\n' | python examples/full_demo.py
printf '/exit\n' | python examples/chat_ai.py
```

## Project Structure

High-level layout:

- `klix/`: framework source code
- `klix/cli/`: scaffold CLI entry point
- `klix/input/`: prompt engine and interactive input components
- `klix/output/`: renderers, theme model, and output widgets
- `klix/layout/`: lightweight persistent layout regions and redraw support
- `examples/`: runnable example apps
- `tests/`: test suite
- `docs/`: end-user and developer documentation

If you are changing behavior, read the relevant concept docs first so code and docs stay aligned.

## Coding Guidelines

- Keep changes small and explicit.
- Prefer typed interfaces over loosely structured dictionaries.
- Reuse existing framework surfaces before inventing new ones.
- Preserve the separation between app/runtime, input, output, router, and layout layers.
- Keep terminal fallback behavior in mind. Rich output is preferred, but not guaranteed.
- Avoid adding dependencies unless there is a strong reason and clear framework-level value.
- Do not introduce magic behavior that makes the framework harder to reason about.

## Documentation Expectations

If you change public behavior, update the docs in `docs/` and any relevant examples.

A developer should be able to use Klix without reading source code. That means documentation is part of the product, not an afterthought.

## Working On Features

When adding or adjusting framework behavior:

1. understand which layer owns the problem
2. make the smallest change that fits that layer
3. validate the change with tests or example runs
4. document any user-visible behavior change

Examples:

- UI widgets belong under `session.ui.output` or `session.ui.input`
- lifecycle behavior belongs in `App`, middleware, or events
- parsing behavior belongs in the router, not in random handlers

## Pull Requests

Pull requests are easiest to review when they are focused.

A good PR usually includes:

- a clear problem statement
- a small, coherent diff
- notes on how the change was validated
- docs or examples updated when needed

If a change is large or cuts across multiple layers, opening an issue or discussion first is usually the better path.

## Ideas For Useful Contributions

- improve docs clarity or coverage
- tighten tests around router, middleware, or persistence behavior
- improve example apps
- clean up rough edges in packaging or release quality
- fix compatibility issues across terminals and fallback renderers

## Respectful Collaboration

Please keep discussions respectful, direct, and inclusive.

That means:

- assume good intent
- critique ideas and implementations, not people
- keep feedback specific and actionable
- make space for contributors with different levels of framework context

Klix should be straightforward to work on and straightforward to discuss.
