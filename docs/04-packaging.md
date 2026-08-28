# M4 · Ship your project as a package 🔵

> ⏱ 25 minutes · Route: Full, Fast

## 3 a.m. story

*`from src.features import build_features` works in your notebook. The same
line in CI raises `ModuleNotFoundError: No module named 'src'`. You add
`sys.path.append("../..")` at the top of six files. It works again — until
someone runs the script from a different directory.*

## What's actually going on

Python finds code on `sys.path`, and a notebook — or a script run as
`python path/to/file.py` — silently puts its own directory there. That's the
whole trick behind "it imports for me." pytest doesn't do this. A container
doesn't do this. CI checks out a clean tree and imports from wherever it
happens to launch, which is rarely the directory you were standing in.

`sys.path.append("../..")` is a patch on the symptom: it hard-codes an
assumption about where the file lives relative to the repo root, which breaks
the moment someone runs it from a different directory, a different OS, or a
Docker `WORKDIR`. The actual fix isn't a better path hack — it's to stop
relying on `sys.path` accidents at all, by making your project a real,
installed Python package. Once `churnkit` is installed, `import churnkit`
works identically from a notebook, a test, a cron job, or a container, because
it no longer depends on where you launched from.

This is not about publishing to PyPI. Nothing here requires a public index —
most ML packages never leave the company. "Pip-installable" here means
*deterministic imports*; shipping to an index is a side benefit you get for
free if you ever want it.

## 🍳 Recipe 1 — a minimal, modern `pyproject.toml`

Everything a build tool and an installer need to know about your project goes
in one file, `pyproject.toml`, per [PEP 621](https://peps.python.org/pep-0621/):

```toml
[project]
name = "churnkit"
version = "0.1.0"
description = "A notebook, refactored into an installable package."
readme = "README.md"
requires-python = ">=3.12"
dependencies = [
    "pandas>=2.2",
    "scikit-learn>=1.5",
]

[project.scripts]
churn-train = "churnkit.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/churnkit"]
```

`[project]` is metadata any tool can read: name, version, the Python you
require, the dependencies you need. It's the same table whether you build
with hatchling, setuptools, PDM or Flit — that's the point of PEP 621, it
ends every backend inventing its own metadata format.

`[build-system]` is [PEP 517](https://peps.python.org/pep-0517/) +
[PEP 518](https://peps.python.org/pep-0518/): your project declares *how to
build itself* — which backend, from which packages — and the installer stops
guessing. `uv build`, `pip install`, and CI all read this block and call the
same backend the same way.

We recommend **hatchling**: fast, zero-config for a standard `src/` layout,
no compiled build step to debug. `setup.py` is legacy — it's an executable
Python file that *is* the build system, which is exactly the kind of
unpredictable, imperative step PEP 517 was created to remove. If you're
carrying a `setup.py`, the `[build-system]` block above replaces it. You do
not need one for a pure-Python package like `churnkit`.

## 🍳 Recipe 2 — the `src/` layout, and why it fixes the story above

```
flat layout                   src/ layout
------------                   ------------
churnkit/                      src/
├── data.py                    │   └── churnkit/
├── features.py                │       ├── data.py
├── model.py                   │       ├── features.py
└── cli.py                     │       ├── model.py
tests/                         │       └── cli.py
└── test_features.py           tests/
pyproject.toml                 │   └── test_features.py
                                pyproject.toml
```

In the flat layout, `churnkit/` sits right next to `tests/` and next to
whatever directory you run Python from. Python adds the current working
directory to `sys.path`, so `import churnkit` succeeds *whether or not the
package is actually installed*. Your tests pass, you commit, and the bug
ships — because the thing that made it pass locally (your working directory)
isn't true in CI, in a container, or on a colleague's machine.

Move the package under `src/`, and that accident is gone. `src/churnkit` is
not on `sys.path` just because you're in the repo root. The *only* way
`import churnkit` succeeds now is if the package has genuinely been
installed — which converts a class of silent, environment-dependent bugs into
one loud, immediate `ModuleNotFoundError` the first time you forget to
install. You want that failure on your laptop, today, not in production.

## 🍳 Recipe 3 — editable installs

```bash
uv sync
```

`uv sync` installs your project itself, in **editable** mode, alongside its
dependencies — no separate step. (Working from plain pip: the equivalent is
`pip install -e .`.)

Editable means a *link*, not a copy. `site-packages` gets a pointer back to
`src/churnkit`, so editing `features.py` and re-running `uv run churn-train`
picks up the change immediately — no reinstall, no rebuild.

The deliverable of this recipe is one `grep`:

```bash
grep -rn "sys.path" src tests
```

If that's empty, you're done. Every `sys.path.append` in the repo exists to
work around an uninstalled package; once the package is actually installed,
none of them do anything except hide the next environment bug.

## 🍳 Recipe 4 — entry points: stop running scripts by path

```toml
[project.scripts]
churn-train = "churnkit.cli:main"
```

```bash
uv run churn-train --rows 8000
```

This turns `python scripts/train_v3_final_FINAL.py` — a path, a guess at
which Python, a guess at which environment — into `churn-train`, a command
that exists once `churnkit` is installed, anywhere, the same way, every time.

It matters beyond aesthetics. The entry point is versioned *with the
package*: `churnkit==0.3.1` and `churnkit==0.4.0` can point `churn-train` at
different code, and whichever version is installed is the one that runs. It
works from any working directory, so it doesn't care whether it's invoked
from a shell, a `Makefile`, a scheduler, or a Dockerfile `CMD` — which is
exactly what should be calling it. `mlproj train --config configs/base.yaml`
is the same idea for a project named `mlproj`: a package with a stable CLI
surface, not a directory of scripts with version numbers in the filename.

## 🍳 Recipe 5 — build and hand it over

```bash
uv build
```

```
Building source distribution...
Building wheel from source distribution...
Successfully built dist/churnkit-0.1.0.tar.gz and dist/churnkit-0.1.0-py3-none-any.whl
```

Two artifacts, two jobs:

- **wheel** (`.whl`) — pre-built, ready to unpack straight into `site-packages`.
  This is what installers want and what `uv`/`pip` fetch by default.
- **sdist** (`.tar.gz`) — the source, plus the metadata to build a wheel from
  it. Needed for platforms with no matching wheel, or packages with a
  compiled extension that must build on the target machine.

Prove the wheel is real by installing it somewhere with no relationship to
your source tree:

```bash
cd /tmp && uv venv proof && uv pip install --python proof dist/churnkit-0.1.0-py3-none-any.whl
./proof/bin/churn-train --rows 2000
```

If `churn-train` runs from a directory that has never heard of your repo,
the packaging is real, not an artifact of your editable install.

Where it goes next depends on who needs it. Inside an org, push wheels to an
internal index (Artifactory, a private PyPI, a cloud artifact registry) and
`uv add` picks them up like any public package. For a one-off or a
fast-moving internal library not worth an index yet, install straight from
git — but pin a commit SHA, never a branch:

```bash
uv add "git+https://github.com/yourorg/churnkit@a1b2c3d"
```

A branch reference means the same `pyproject.toml` resolves to different code
next week. A SHA is a lock, not a wish.

## 🍳 Recipe 6 — repo layout that scales 🔴

For one package, this is the whole repo:

```
.
├── pyproject.toml
├── src/churnkit/       # the library
├── configs/            # yaml/toml run configs, not code
├── notebooks/          # exploration only — nothing imports from here
└── tests/
```

`configs/` stays out of `src/` on purpose: configuration changes per run,
code doesn't, and mixing them makes both harder to review. `notebooks/`
imports the installed package (Recipe 3) and produces nothing anything else
depends on.

When one repo grows into *several* related packages — a shared feature
library plus two model services that both depend on it — reach for a **uv
workspace** before you reach for three separate repos and a private index.
A workspace is one lockfile covering multiple packages, each still
independently versioned and buildable:

```toml
# root pyproject.toml
[tool.uv.workspace]
members = ["packages/*"]
```

```
.
├── pyproject.toml          # [tool.uv.workspace]
├── uv.lock                 # one lock, every member
└── packages/
    ├── churn-features/     # shared library
    ├── churn-train/        # depends on churn-features
    └── churn-serve/        # depends on churn-features
```

`churn-train` and `churn-serve` declare `churn-features` as a normal
dependency; `uv` resolves it from the workspace member instead of an index,
and one `uv lock` keeps all three consistent. You get independent packages
without independent, driftable lockfiles.

## ⚠️ Sharp edges

- **Hyphens vs underscores.** A distribution named `churn-kit` imports as
  `churn_kit` — Python identifiers can't contain hyphens. `uv init` and
  hatchling infer this, but set both explicitly (`name = "churn-kit"` in
  `[project]`, `packages = ["src/churn_kit"]` in the hatch table) once your
  package name and directory name diverge, so the inference has nothing to
  guess wrong.
- **`tests/` ships inside the wheel by accident more often than you'd think.**
  With a `src/` layout and `packages = ["src/churnkit"]` this isn't an issue —
  only what's under `src/` is included — but double-check `tar tf
  dist/*.tar.gz` if you switch backends or layouts.
- **Single-source your version.** Don't write `0.3.1` in both `pyproject.toml`
  and a `churnkit/__init__.py` — they will drift. Either hand-edit one place
  and read it from the other (`importlib.metadata.version("churnkit")` at
  runtime), or let hatchling read it from a file (`[tool.hatch.version]
  path = "src/churnkit/__init__.py"`). Two sources of truth for a version
  number is worse than one, even a manual one.
- **Data files are not included by default.** A wheel ships importable
  Python, not `configs/base.yaml` or a model card sitting next to it. If code
  genuinely needs to load a file at import time, declare it explicitly
  (`[tool.hatch.build.targets.wheel.force-include]` or package-data
  equivalent) — otherwise keep it outside the package and pass a path in.

## ✅ Check yourself

<details>
<summary>Why does the <code>src/</code> layout catch import bugs that a flat layout hides?</summary>

In a flat layout, the package directory sits next to your tests and your
current working directory, and Python adds that directory to `sys.path`
automatically — so `import churnkit` succeeds whether or not the package is
actually installed. Tests then pass for a reason that doesn't hold in CI, in
a container, or on a colleague's machine. Under `src/`, the package isn't
reachable by accident: the only way the import works is if it's really
installed, so a packaging mistake fails immediately, on your laptop, instead
of silently in production.
</details>

<details>
<summary>You need <code>configs/base.yaml</code> at runtime in a container. Package data, or a mounted file?</summary>

A mounted file (or a file baked into the image outside the package), not
package data. Configuration changes per environment and per run — that's the
whole point of having it — while the wheel's contents should be identical
across every deploy. Bundling `configs/` as package data means a config
change forces a version bump and a rebuild just to change a threshold.
Package data is for files the code cannot run without and that never vary,
like a schema or a small lookup table; a training config is neither.
</details>

## 📖 Go deeper

- [Python Packaging User Guide — packaging projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/)
- [PEP 621 — project metadata in `pyproject.toml`](https://peps.python.org/pep-0621/)
