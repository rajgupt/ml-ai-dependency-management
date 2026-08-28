# Recipe index 🟢

Every recipe in the book, on one page. This is the page to bookmark.

## Starting a project

| I want to… | Do this | Where |
|---|---|---|
| Start a new project | `uv init --python 3.12 <name>` | [M0](00-setup.md) |
| Add a dependency | `uv add <pkg>` | [M0](00-setup.md) |
| Add a dev-only tool | `uv add --group dev pytest` | [M2](02-uv.md) |
| Add an opt-in feature dep | `uv add --optional gpu "torch>=2.6"` | [M2](02-uv.md) |
| Run a linter without installing it | `uvx ruff check .` | [M2](02-uv.md) |

## Reproducing an environment

| I want to… | Do this | Where |
|---|---|---|
| Recreate the exact env | `uv sync --frozen` | [M2](02-uv.md) |
| Fail CI if the lock is stale | `uv sync --locked` | [M2](02-uv.md) |
| Hand a pip-only teammate an env | `uv export --no-hashes -o requirements.txt` | [M2](02-uv.md) |
| Emit a standard lockfile | `uv export --format pylock.toml -o pylock.toml` | [M2](02-uv.md) |

## Packaging

| I want to… | Do this | Where |
|---|---|---|
| Kill `sys.path.append` | `src/` layout + editable install | [M4](04-packaging.md) |
| Turn a script into a command | `[project.scripts]` | [M4](04-packaging.md) |
| Build a wheel | `uv build` | [M4](04-packaging.md) |

## GPUs and system libraries

| I want to… | Do this | Where |
|---|---|---|
| Pin a CUDA build of torch | `[[tool.uv.index]]` + `explicit = true` | [M6](06-gpu-and-system-deps.md) |
| One lock, CPU laptops + GPU cluster | environment markers on `torch` | [M6](06-gpu-and-system-deps.md) |
| Install ffmpeg / libGL | the decision tree | [M6](06-gpu-and-system-deps.md) |
| Small production image | multi-stage + `--no-dev` | [M6](06-gpu-and-system-deps.md) |

## Keeping it alive

| I want to… | Do this | Where |
|---|---|---|
| Record what a run used | the run manifest | [M7](07-reproducibility.md) |
| Make the notebook use the project env | register the venv kernel | [M7](07-reproducibility.md) |
| Check for known vulnerabilities | `uvx pip-audit` | [M8](08-supply-chain.md) |
| Upgrade one package safely | `uv lock --upgrade-package <pkg>` | [M8](08-supply-chain.md) |
| Generate an SBOM | `uvx --from cyclonedx-bom cyclonedx-py environment .venv` | [Lab 3](labs/lab-3.md) |
| Read a lock diff after an upgrade | `git diff uv.lock` | [Lab 3](labs/lab-3.md) |
| Pin a base image immutably | digest, not tag: `python:3.12-slim@sha256:…` | [Lab 3](labs/lab-3.md) |
