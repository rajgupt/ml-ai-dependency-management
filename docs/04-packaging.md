# M4 · Ship your project as a package 🔵

> ⏱ 25 minutes · Route: Full, Fast

## 3 a.m. story

*`from src.features import build_features` works in your notebook. The same
line in CI raises `ModuleNotFoundError: No module named 'src'`. You add
`sys.path.append("../..")` at the top of six files. It works again — until
someone runs the script from a different directory.*

## What's actually going on

<!-- WRITE: ~180 words.
     Python finds code on sys.path. A notebook silently puts its own directory there;
     pytest and a container do not. So "it imports" is an accident of where you launched from.
     The fix is not more sys.path hacks — it's to make your project a real, installed
     package, so it's importable from anywhere by name.
     Being pip-installable is not about publishing to PyPI. It's about making imports
     deterministic. Publishing is a side benefit. -->

## 🍳 Recipe 1 — a minimal, modern `pyproject.toml`

<!-- WRITE: full annotated example. PEP 621 metadata + hatchling backend.
     [build-system] requires/build-backend — explain PEP 517/518 in two sentences:
       your project declares how to build itself; the installer no longer guesses.
     Say clearly: setup.py is legacy. You do not need one. -->

## 🍳 Recipe 2 — the `src/` layout, and why it fixes the story above

<!-- WRITE: show flat layout vs src layout side by side.
     src/ layout makes the package NOT importable from the repo root by accident, so the
     only way your tests can import it is if it's actually installed. That converts a
     class of "works on my machine" bugs into an immediate, loud failure. -->

## 🍳 Recipe 3 — editable installs

<!-- WRITE: `uv sync` installs your project in editable mode automatically.
     Equivalent for pip users: `pip install -e .`
     What editable means: a link, not a copy — edit source, no reinstall.
     Delete every sys.path.append in the repo. That's the deliverable of this recipe. -->

## 🍳 Recipe 4 — entry points: stop running scripts by path

<!-- WRITE:
     [project.scripts]
     churn-train = "churnkit.cli:main"

     `python scripts/train_v3_final_FINAL.py` becomes `uv run churn-train --config configs/base.yaml`.
     Why it matters beyond aesthetics: the entry point is versioned with the package, works
     from any directory, and is what your Docker CMD and your scheduler should call. -->

## 🍳 Recipe 5 — build and hand it over

<!-- WRITE:
     uv build            → dist/*.whl and dist/*.tar.gz
     wheel vs sdist in three lines (wheel = pre-built, fast, what installers want).
     Installing into a throwaway env to prove it works.
     Where to put it: internal index / artifact registry vs `pip install git+ssh://...@<sha>`
     (pin the SHA, never a branch). -->

## 🍳 Recipe 6 — repo layout that scales 🔴

<!-- WRITE: src/pkg/ + configs/ + notebooks/ + tests/ + pyproject.toml at root.
     Then: when one repo holds several related packages (a shared feature library +
     two model services), uv workspaces — one lock, many packages. Keep it to ~150 words
     and one pyproject example; this is the 🔴 tail of the module. -->

## ⚠️ Sharp edges

<!-- WRITE:
     - A package name with a hyphen imports with an underscore. Set both explicitly.
     - Don't ship `tests/` inside the wheel unless you mean to.
     - Single-source your version (hatch `version.path` or `importlib.metadata`), never two places.
     - Data files (configs, model cards) are NOT included by default. Declare them or load
       them from outside the package. -->

## ✅ Check yourself

<!-- WRITE: Q1: Why does src/ layout catch import bugs that flat layout hides?
           Q2: You need `configs/base.yaml` at runtime in a container. Package data or mounted file? -->

## 📖 Go deeper

- [Python Packaging User Guide — packaging projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/)
- [PEP 621 — project metadata in `pyproject.toml`](https://peps.python.org/pep-0621/)
