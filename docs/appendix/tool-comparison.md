# Tool comparison 🟢

This book commits to `uv` so you don't spend your three hours tool-shopping.
Here is the honest comparison, once, so the commitment is informed.

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

For layers 3–4 — the interpreter and Python packages — `uv` is the fastest
option, it's one tool instead of three, and its lock is universal across
platforms. That covers most ML projects most of the time, which is why this
book teaches it as the default and nothing else.

The moment you need a *system* library that isn't a wheel — GDAL, an
MKL-linked build, a CUDA toolkit without root access — reach for `pixi`, or
conda plus `conda-lock`. Accept going in that you now have two dependency
systems, and both need to be locked, not just one of them.

Docker isn't competing with any row in this table — it's the layer below all
of them. Even a project that gets `uv` perfectly right still ships inside a
container, because a container is the only thing that also pins the OS and
system libraries.

None of this is a permanent marriage. `uv` reads a standard `pyproject.toml`,
and `uv pip` speaks pip's command line, so migrating in or out is cheap. And
if your team has a working Poetry repo, don't rewrite it to take this
course — take the concepts (lockfiles, groups vs extras, the four layers)
and keep the tool that's already working.
