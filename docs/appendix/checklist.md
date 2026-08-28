# Dependency Health Checklist 🟢

Run this against a repo you actually own. Score one point each. Take it to your
next team meeting.

## Foundations (4)

- [ ] `pyproject.toml` exists and declares dependencies with intentional ranges — not `pip freeze` output
- [ ] A lockfile (`uv.lock` / `pylock.toml` / hashed `requirements.txt`) is committed
- [ ] The Python version is pinned somewhere the tooling reads (`.python-version` or `requires-python`)
- [ ] `.venv` is in `.gitignore`, and nobody's environment is the source of truth

## Packaging (3)

- [ ] The project is installable (`uv sync` / `pip install -e .`) and uses a `src/` layout
- [ ] Zero occurrences of `sys.path.append` in the repo
- [ ] Entry points exist for the things you run often (`train`, `evaluate`, `serve`)

## ML specifics (3)

- [ ] GPU/CPU dependency variants are declared in config, not in a README instruction
- [ ] Model artifacts are pinned by revision/SHA, and datasets carry a recorded version
- [ ] Every training run emits a manifest (git SHA + lock hash + data version + image digest)

## Survival (2)

- [ ] CI installs with `--locked` and would fail on a stale lock
- [ ] Something (bot or calendar) forces a dependency review at least monthly, with an eval gate

**Score:** 0–4 you have a reproducibility problem you haven't hit yet · 5–8 normal, and worth
one focused afternoon · 9–12 you're fine, go help another team.
