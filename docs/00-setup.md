# M0 · Setup & the 5-minute win 🟢

> ⏱ 10 minutes · Route: Full, Notebook-first

## 3 a.m. story

*You join a project. The README says `pip install -r requirements.txt`. Forty
minutes later pip is still resolving, then it fails on a package that needs a
C compiler you don't have. You haven't read a line of the model code yet.*

## What's actually going on

An "environment" is three things, not one: an interpreter, a set of installed
packages, and the system libraries those packages link against. `pip install
-r requirements.txt` only ever touches the middle one, which is why it stalls,
half-fails, and still doesn't reproduce anything. `requirements.txt` is a
wish, not a record — no hashes, no interpreter pin, no cross-platform
guarantee. Two people running the same file can end up with different
packages a month apart.

Two commands carry the rest of this course. **`uv sync`** makes your `.venv`
match the lockfile exactly — installs what's missing, removes what shouldn't
be there. **`uv run`** runs a command inside that environment, syncing first
if the lock has drifted, so you never hand-verify anything.

The speed matters more than it sounds like it should. When an install takes
2 seconds instead of 20 minutes, you stop hoarding one giant environment for
"everything" and start making a throwaway one per project, per experiment,
per PR. Speed changes behaviour before it changes anything else.

## 🍳 Recipe — your first reproducible environment

Install `uv`:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# or, if you already have pip
pip install uv
```

Then the 5-minute win:

```bash
uv init --python 3.12 demo && cd demo
uv add scikit-learn pandas
uv run python -c "import sklearn; print(sklearn.__version__)"
```

```
1.5.2
```

No `python -m venv`, no `source .venv/bin/activate`, no separate install step
you might forget. Look at what `uv` created:

```bash
ls -a
```

| File | What it is |
|---|---|
| `pyproject.toml` | What this project **supports** — you edit this |
| `uv.lock` | What you **actually ran** — exact versions, hashed, resolved for every platform. You don't edit this |
| `.python-version` | The interpreter you're pinned to. It's a dependency too |
| `.venv/` | The environment itself — disposable, rebuilt from the lock in seconds |

Commit the first three. Never the fourth:

```bash
git add pyproject.toml uv.lock .python-version
echo ".venv/" >> .gitignore
```

That's it — a colleague who clones this repo and runs `uv sync` gets the
exact environment you have, down to the hash.

## ⚠️ Sharp edges

- **Don't `pip install` into a uv-managed `.venv`.** It installs the package
  fine, but `pyproject.toml` and `uv.lock` never hear about it — the lock is
  now lying about what's installed. Use `uv add` instead; it updates both and
  the environment together.
- **Never commit `.venv`.** It's machine-specific (absolute paths, compiled
  extensions for your OS/arch) and can be hundreds of MB. Commit `uv.lock`
  instead — it's the portable version of the same information.
- **`uv run` re-syncing before it runs is a feature, not a delay.** The first
  run after a fresh clone takes a couple of seconds longer; every run after
  that you get for free, and you get the guarantee that what ran matches the
  lock.

## ✅ Check yourself

<details>
<summary>Which of the four files would you send a colleague so they get your exact environment?</summary>

`pyproject.toml`, `uv.lock`, and `.python-version` — never `.venv`. The first
two capture intent and resolution, the third pins the interpreter. Together
they're enough for `uv sync` to rebuild your environment byte-for-byte on a
machine that has never seen your repo.
</details>

<details>
<summary>What does <code>uv run pytest</code> do that <code>pytest</code> does not?</summary>

It checks the environment against the lock first — and syncs it if it's
stale — before running `pytest` inside it. Bare `pytest` just runs whatever
happens to be on your current `PATH`, which might be a different virtualenv,
a system install, or nothing at all.
</details>

## 📖 Go deeper

- [uv — Getting started](https://docs.astral.sh/uv/getting-started/)
- [Python Packaging User Guide — installing packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)
