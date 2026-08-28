# Lab 3 · solution — `churnkit`, shipped

```bash
uv sync
uv run churn-train --rows 8000     # test AUC: 0.7506
uv run pytest -q                   # passes
uv run ruff check .                # passes
```

This is `churnkit` after all four steps of [Lab 3](../../../docs/labs/lab-3.md):

| Step | What's here |
|---|---|
| 1 · GPU/CPU split | Documented in the lab (Optional/go-deeper) — a real `[[tool.uv.index]]` + `[tool.uv.sources]` recipe you add to `pyproject.toml`. Not wired into this checked-in project; see the note at the bottom of this file for why. |
| 2 · Two containers | [`Dockerfile.train`](Dockerfile.train), [`Dockerfile.serve`](Dockerfile.serve) — one `pyproject.toml`, two images. |
| 3 · CI | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — copy this into your own repo's `.github/workflows/`. |
| 4 · Upgrade ritual | `scikit-learn>=1.5` here (upgraded). Compare against [`../starter`](../starter), which is still pinned to the old `1.3.2` on purpose — run the ritual yourself from there. |

## Why Step 1 isn't wired into this repo's own lock

`uv lock` for a real torch CPU/GPU split needs outbound access to
`download.pytorch.org`. That's normal on a laptop or in GitHub Actions, but
this course's own authoring/build sandbox runs behind a proxy that doesn't
allowlist that host (confirmed: a direct request gets a `403` at the CONNECT
tunnel). Rather than ship a lockfile nobody actually generated, the recipe
lives in the lab doc as real, copy-pasteable config — exactly what
[M6](../../../docs/06-gpu-and-system-deps.md) already teaches — and this
project keeps the plain `gpu = ["torch>=2.6"]` extra from Lab 2 so
`uv lock` / `uv sync --locked` stay genuinely runnable everywhere this repo
is built, including this course's own CI.
