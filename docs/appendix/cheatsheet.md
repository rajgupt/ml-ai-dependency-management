# uv cheat sheet 🟢

## Project

```bash
uv init --python 3.12 myproj      # new project
uv add pandas "scikit-learn>=1.5" # add runtime deps
uv add --group dev pytest ruff    # dev-only (PEP 735 group, never shipped)
uv add --optional gpu "torch>=2.6"# opt-in extra, ships with the package
uv remove pandas
uv lock                           # re-resolve
uv lock --upgrade-package pandas  # targeted bump
uv sync                           # env := lock
uv sync --frozen --no-dev         # production install, no re-resolve
uv sync --locked                  # CI: fail if lock is stale
uv run python train.py            # run inside the env
uv build                          # dist/*.whl + *.tar.gz
```

## Interpreters

```bash
uv python install 3.12
uv python list
uv python pin 3.12                # writes .python-version
```

## Tools (not project dependencies)

```bash
uvx ruff check .                  # run once, install nothing
uv tool install pre-commit
```

## Export / interop

```bash
uv export --no-hashes -o requirements.txt
uv export --format pylock.toml -o pylock.toml
uv pip install -r requirements.txt   # pip-compatible API (does NOT touch the lock)
uv pip list --outdated
```

## Torch

```bash
uv pip install torch --torch-backend=auto   # uv pip only — NOT uv add/lock/sync
```

## Diagnosing

```bash
uv tree                           # dependency tree
uv tree --package torch --invert  # who pulled this in?
uv lock --resolution lowest-direct  # are your declared floors real?
```
