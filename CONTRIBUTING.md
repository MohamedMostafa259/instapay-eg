# Contributing

Thank you for considering contributing to **instapay-eg**!

## Quick Setup

```bash
# 1. Fork the repo on GitHub, then clone your fork:
git clone https://github.com/<your-username>/instapay-eg.git
cd instapay-eg

# 2. Install all dependencies (including dev):
uv sync --all-extras

# 3. Install pre-commit hooks:
uv run poe setup

# 4. Verify everything works:
uv run poe test
```

## Development Workflow

```bash
# Create a feature branch:
git checkout -b feat/my-feature

# Make your changes, then run the full check suite:
uv run poe check-all
uv run poe test

# Commit (pre-commit hooks run automatically):
git commit -m "add my feature"

# Push and open a PR:
git push origin feat/my-feature
```

## Running the Docs Locally

```bash
uv run poe docs
# Open http://127.0.0.1:8000 in your browser
```

## Code Standards

- **100% test coverage is required** - every line and branch must be covered.
- All functions must have **Google-style docstrings**.
- Use the **custom exception hierarchy** (`InstaPayError` and its subclasses) - never raise bare `ValueError` or `Exception`.
- Add entries to `CHANGELOG.md` under `[Unreleased]` for every user-facing change.

## Reporting Issues

Please use the [GitHub issue tracker](https://github.com/MohamedMostafa259/instapay-eg/issues).
For security vulnerabilities, see [SECURITY.md](../SECURITY.md).
