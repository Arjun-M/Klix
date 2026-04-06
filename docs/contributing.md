# Contributing

Klix is small enough that individual changes can improve the framework quickly, but that also means each change has to respect the existing shape of the codebase. This guide explains how to work on the project without fighting that design.

## How To Run The Project Locally

Clone the repository, create a virtual environment, and install the package in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

Run the example apps:

```bash
python examples/minimal.py
python examples/full_demo.py
python examples/chat_ai.py
python examples/ui_showcase.py
```

Run the tests:

```bash
python -m pytest -q
```

## What A Good Contribution Looks Like

Good changes usually have these qualities:

- they solve one clear problem
- they fit the current architecture instead of bypassing it
- they keep the public API small
- they include tests or example coverage where practical
- they update documentation when behavior changes

Klix is intentionally not a giant framework. Additions should earn their weight.

## How To Add Features Correctly

When you add a feature, work from the framework layers outward:

1. decide whether it belongs in the core runtime, UI namespace, renderer, or an example
2. make the smallest change that fits that layer
3. keep the public API semantic and lightweight
4. validate behavior in a real example, not just in isolation

Examples:

- a new visual helper probably belongs under `session.ui.output`
- a new prompt interaction probably belongs under `session.ui.input`
- lifecycle behavior probably belongs in `App`, events, or middleware

If a feature requires reaching into many private attributes to work, the design probably needs another pass.

## Coding Guidelines

- Keep code readable and direct.
- Prefer typed, explicit interfaces over loose dictionaries.
- Reuse existing framework surfaces before creating new ones.
- Use semantic theme keys instead of hardcoded styling in reusable components.
- Do not introduce dependencies casually. Klix currently stays small on purpose.
- Keep fallback and CI behavior in mind when working on UI features.

## Testing Expectations

Not every change needs a large test suite, but it should be verifiable.

Typical validation steps:

- run `pytest`
- run the relevant example app
- verify interactive features in a real terminal when applicable

For UI-heavy work, examples are especially valuable because terminal behavior is hard to understand from unit tests alone.

## Documentation Expectations

If behavior changes, update the docs in `docs/`.

The goal of the documentation set is that a developer can use Klix without reading the source. Keep that standard in mind when you change:

- public API
- command flow
- persistence behavior
- component behavior

## Pull Requests And Suggestions

Pull requests, bug reports, design suggestions, and documentation improvements are all useful contributions.

Helpful pull requests usually include:

- a clear problem statement
- a focused change set
- notes on how the change was validated

If you are not sure whether a feature fits the project, opening an issue or discussion first is a good way to avoid wasted work.

## A Professional Baseline

Welcoming contributions does not mean lowering the bar. The framework is small enough that unclear abstractions, duplicate APIs, or loosely justified features can make it harder to maintain quickly.

Aim for:

- small changes
- clear reasoning
- honest docs
- practical examples

That is how Klix stays approachable as it grows.
