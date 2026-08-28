# Lab 1 · solution

```bash
uv sync --frozen
uv run python train.py     # test AUC: 0.7531
uv run ruff check .
```

`uv run pytest` fails here **on purpose** — see step 8 of the lab. It is the
cliffhanger into Lab 2.
