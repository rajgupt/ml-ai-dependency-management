# Lab 2 · solution — `churnkit`

```bash
uv sync
uv run churn-train --rows 8000     # test AUC: 0.7506
uv run pytest -q                   # passes: the package is importable by name
uv build                           # dist/churnkit-0.1.0-py3-none-any.whl
```

Grep the whole tree for `sys.path` — there is nothing to find. That is the point.

The `gpu` extra is declared but not installed by `uv sync`. `uv sync --extra gpu`
pulls ~2 GB of torch; skip it unless you want to watch it happen.
