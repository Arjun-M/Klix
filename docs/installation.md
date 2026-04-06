# Installation

Klix is a normal Python package with a small runtime dependency set:

- `prompt_toolkit`
- `rich`
- `pydantic`

See also [Getting Started](getting-started.md) and [Quickstart](quickstart.md).

## Requirements

- Python 3.9+
- A terminal with standard input/output for interactive use

## Install From The Repository

For local development:

```bash
git clone <repo-url>
cd klix
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

That gives you:

- the `klix` Python package
- the `klix` scaffold command

## Verify The Install

Run:

```bash
klix
```

You should see:

```text
Usage: klix init <name>
```

Then generate a starter app:

```bash
klix init mytool
cd mytool
pip install -e .
mytool
```

See [Quickstart](quickstart.md) for the next step.

## Installing In A Clean Environment

If you want to verify the full install path from scratch:

```bash
python -m venv /tmp/klix-venv
source /tmp/klix-venv/bin/activate
pip install -e /path/to/klix
klix init demo
```

This is useful when you are changing packaging metadata. See [Contributing](contributing.md).

## What Gets Installed

The package includes:

- the top-level framework package `klix`
- subpackages for input, output, layout, and CLI tooling
- the `klix` console entry point defined in `pyproject.toml`

The implementation currently packages framework code, not documentation or examples as runtime dependencies.

## Common Mistakes

### Running without editable install

If you are working from the repo and examples cannot import `klix`, make sure you ran:

```bash
pip install -e .
```

### Using a non-interactive environment for interactive demos

Some examples depend on prompt-driven interaction. If you pipe input or run inside CI, Klix will fall back to simpler stdin behavior. That is useful for tests, but selector dialogs and richer interactions are best tried in a real terminal. See [Input Components](components/input.md).

### Expecting `pip install klix` from PyPI here

This repository is the source tree. The docs in this folder describe the current repo state, not a separately published release pipeline.
