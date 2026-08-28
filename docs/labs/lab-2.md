# 🧪 Lab 2 · Notebook → installable package 🟢🔵

> ⏱ 20 minutes · Needs: `uv`. No GPU.
> Start in [`examples/lab2-package/starter/`](../../examples/lab2-package/starter/README.md)
>
> 🪟 **Windows:** runs natively, no WSL. Command blocks are `bash`; a
> **PowerShell** block follows wherever the syntax differs. See
> [How to use this book](../how-to-use.md#windows-users).

## The brief

Open `notebooks/churn_messy.ipynb` and read it before you touch anything. It is
not a strawman — every bad habit in it is one somebody shipped:

```python
!pip install pandas scikit-learn numpy          # env drifts from the repo, invisible in review
sys.path.append("../..")                        # works from this directory only
sys.path.append("/Users/rgupta/work/churn/...") # works on one laptop only
```

…execution counts running `7, 2, 12, 3, 15, 4, 9, 16` (so the printed AUC
corresponds to no state you can reconstruct), two subtly different definitions
of the same feature (`calls_per_year` vs `calls_per_yr`), and `pickle.dump` at
the end — which [M8](../08-supply-chain.md) will have opinions about.

By the end of this lab, `import churnkit` will work from a notebook, from
pytest, from a container and from a colleague's laptop, and the
`ModuleNotFoundError` you hit in [Lab 1](lab-1.md) will be gone for good.

## Step 1 — Create the project skeleton

```bash
cd examples/lab2-package/starter
mkdir -p src/churnkit tests
uv init --bare --python 3.12
uv python pin 3.12
uv add "pandas>=2.2" "scikit-learn>=1.5"
uv add --group dev pytest ruff
uv add --group notebook ipykernel nbstripout
```

```powershell
# 🪟 PowerShell — only the mkdir line differs; the uv commands are identical
cd examples\lab2-package\starter
New-Item -ItemType Directory -Force src\churnkit, tests | Out-Null
uv init --bare --python 3.12
uv python pin 3.12
uv add "pandas>=2.2" "scikit-learn>=1.5"
uv add --group dev pytest ruff
uv add --group notebook ipykernel nbstripout
```

Two dev-ish groups, deliberately. `dev` is what CI installs; `notebook` is what
people running Jupyter need. Neither ships to production.

## Step 2 — Tell the build system this is a package

Add to `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/churnkit"]
```

`[build-system]` is [PEP 517/518](https://peps.python.org/pep-0517/): your
project declares how to build itself, and the installer stops guessing. You do
**not** need a `setup.py`. If you're carrying one, this replaces it.

## Step 3 — Move the logic out of the notebook

Split the notebook's code cells into four modules under `src/churnkit/`:

| Module | Takes | Gives back |
|---|---|---|
| `data.py` | row count, seed | a raw customer `DataFrame` |
| `features.py` | raw `DataFrame` | model-ready features |
| `model.py` | raw `DataFrame` | a fitted model + held-out AUC |
| `cli.py` | command-line args | writes `metrics.json`, prints the AUC |

Two rules while you move things:

1. **One definition wins.** The notebook has `calls_per_year` and
   `calls_per_yr`. Pick one, put it in `features.py`, delete the other. This
   duplication is the single most expensive habit in the starter notebook —
   it's how a notebook and a training job silently diverge.
2. **No I/O in `features.py`.** Feature code that reads files can't be tested.

> **Why `src/`?** Put the package at the repo root and Python will import it
> just because you happen to be standing in that directory — so your tests
> pass for a reason that won't hold in CI. Under `src/`, the *only* way to
> import `churnkit` is if it's genuinely installed. It converts a class of
> silent bugs into one loud failure, immediately. See [M4](../04-packaging.md).

## Step 4 — Add the console script

```toml
[project.scripts]
churn-train = "churnkit.cli:main"
```

Then:

```bash
uv sync
uv run churn-train --rows 8000
```

```
test AUC: 0.7506  ->  metrics.json
```

`uv sync` installed your project in **editable** mode — a link to `src/`, not a
copy. Edit `features.py` and re-run; no reinstall needed. (The pip equivalent is
`pip install -e .`.)

That command is now what your Dockerfile `CMD`, your Airflow operator and your
`Makefile` should call. Not a path to a `.py` file.

## Step 5 — Add an extra, and see the difference

```toml
[project.optional-dependencies]
gpu = ["torch>=2.6"]
```

```bash
uv lock
uv sync                  # torch is NOT installed
uv sync --extra gpu      # torch IS installed (~2 GB — skip if you'd rather not)
```

Now hold the three tables side by side:

| Table | Ships to users? | Installed by plain `uv sync`? | For |
|---|---|---|---|
| `dependencies` | yes | yes | what the package always needs |
| `[project.optional-dependencies]` (**extras**) | yes | no | features users opt into: `churnkit[gpu]` |
| `[dependency-groups]` (**groups**, PEP 735) | **no** | `dev` only | pytest, ruff, ipykernel |

**Extras ship, groups don't.** If you remember one thing from this lab, this is
more useful than the packaging.

## Step 6 — Write tests that import by name

```python
# tests/test_features.py
from churnkit import build_features, make_customers
from churnkit.features import TARGET


def test_target_is_never_a_feature():
    assert TARGET not in build_features(make_customers(200)).columns
```

```bash
uv run pytest -q
```

```
5 passed in 1.76s
```

Compare that with Lab 1's `ModuleNotFoundError`. Nothing about pytest changed.
The project became installable, so the import works — from anywhere.

Test the *feature contract*, not the metric: does the target leak into the
features, do the derived columns exist, does `build_features` mutate its input.
Those catch real bugs and don't flake when you retune the model.

## Step 7 — Point the notebook at the package

Register the project environment as a Jupyter kernel:

```bash
uv run --group notebook ipython kernel install --user --name=churnkit
```

Then in the notebook:

- delete both `sys.path.append` lines,
- delete the `!pip install` cell,
- replace the copied feature code with `from churnkit import build_features, make_customers, train`,
- select the **churnkit** kernel, and **Restart & Run All**.

> **The kernel is not the project environment.** A notebook connected to some
> other kernel will happily import a different version of everything you just
> pinned. This single step removes most "but it worked in my notebook".

Keep outputs out of git:

```bash
uv run nbstripout --install
```

Now notebook diffs are reviewable, and you stop committing data samples inside
cell outputs.

## Step 8 — Prove it's real

```bash
uv build
```

```
Successfully built dist/churnkit-0.1.0-py3-none-any.whl
```

Install the wheel somewhere with no relationship to your source tree:

```bash
cd /tmp && uv venv proof && uv pip install --python proof \
  /path/to/examples/lab2-package/starter/dist/churnkit-0.1.0-py3-none-any.whl
./proof/bin/churn-train --rows 2000
```

```powershell
# 🪟 PowerShell — note the Scripts\ path and .exe suffix
cd $env:TEMP
uv venv proof
uv pip install --python proof `
  C:\path\to\examples\lab2-package\starter\dist\churnkit-0.1.0-py3-none-any.whl
.\proof\Scripts\churn-train.exe --rows 2000
```

The console script runs, from a directory that has never heard of your repo.
That is what "pip installable" actually buys you.

Finally, the check that matters:

```bash
grep -rn "sys.path" src tests notebooks
```

```powershell
# 🪟 PowerShell
Select-String -Path src\*,tests\*,notebooks\* -Pattern "sys.path" -Recurse
```

Nothing. Compare against your `git diff` — you deleted three lines of
`sys.path` and got determinism in exchange.

## ✅ You should now be able to answer

<details>
<summary>Why does the <code>src/</code> layout catch import bugs that a flat layout hides?</summary>

In a flat layout the package directory sits next to your tests, and Python adds
the current directory to `sys.path`, so imports succeed whether or not the
package is installed. Your tests then pass for a reason that doesn't hold in CI,
in a container, or on a colleague's machine. `src/` removes that accident: the
package is unreachable unless it is really installed, so a packaging mistake
fails on your laptop instead of in production.
</details>

<details>
<summary><code>torch</code> for optional GPU inference — extra or dependency group?</summary>

An extra. Users of `churnkit` should be able to opt in with
`pip install churnkit[gpu]`, which means it has to ship with the package
metadata. Dependency groups are invisible to anyone who installs your package —
right for `pytest`, wrong for a feature.
</details>

<details>
<summary>Your Dockerfile needs to run training. What does it call, and what does it install?</summary>

It calls `churn-train` (the console script — version-controlled, works from any
working directory). It installs with `uv sync --frozen --no-dev`: from the
lock, no re-resolution, and without the `dev` group, so pytest and ruff never
reach the image. Extras are opt-in too, so the serving image can skip `[gpu]`
if it doesn't need it. See [M6](../06-gpu-and-system-deps.md).
</details>

## 📖 Go deeper

- [Python Packaging User Guide — packaging projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Scientific Python Development Guide — the `src` layout](https://learn.scientific-python.org/development/guides/packaging-simple/)
- [PEP 621 — project metadata](https://peps.python.org/pep-0621/)
