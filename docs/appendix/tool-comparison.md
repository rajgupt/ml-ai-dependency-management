# Tool comparison 🟢

This book commits to `uv` so you don't spend your three hours tool-shopping.
Here is the honest comparison, once, so the commitment is informed.

<!-- WRITE: fill the table with a fair assessment. Columns:
     Tool | Solves which layers | Lockfile | Non-Python deps | Best when -->

| Tool | Layers it owns | Lockfile | Non-Python deps | Reach for it when |
|---|---|---|---|---|
| **uv** | interpreter + packages (3–4) | `uv.lock`, universal + hashed | no | Default. Almost always. |
| **pip + venv** | packages (4) | none (needs pip-tools) | no | A tiny script, or a locked-down box |
| **pip-tools** | packages (4) | `requirements.txt` + hashes, per-platform | no | You must stay on pip-native tooling |
| **Poetry** | packages (4) | `poetry.lock` | no | Existing Poetry repo, working fine |
| **conda / mamba** | packages + system libs (2–4) | via `conda-lock` | **yes** | You need MKL/GDAL/CUDA toolkit without root |
| **pixi** | packages + system libs (2–4) | `pixi.lock`, built in | **yes** | conda-forge deps *and* a modern lock/workflow |
| **Docker** | everything (1–4, pinned) | image digest | **yes** | Deploying. Always, eventually. |

## The honest summary

<!-- WRITE: ~150 words.
     - uv for layers 3–4: fastest, one tool, universal lock. This is most ML projects.
     - The moment you need conda-forge system libraries (GDAL, MKL-linked builds, a CUDA
       toolkit without root), reach for pixi (or conda + conda-lock) — and accept that you now
       have two dependency systems and must lock both.
     - Docker isn't an alternative, it's the layer below. Even a perfect uv project ships in one.
     - Migration is cheap: uv reads pyproject.toml, and `uv pip` speaks pip. You are not marrying it.
     - Don't rewrite a working Poetry repo for this course. Take the concepts, keep the tool. -->
