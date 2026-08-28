# M0 · Setup & the 5-minute win 🟢

> ⏱ 10 minutes · Route: Full, Notebook-first

## 3 a.m. story

*You join a project. The README says `pip install -r requirements.txt`. Forty
minutes later pip is still resolving, then it fails on a package that needs a
C compiler you don't have. You haven't read a line of the model code yet.*

## What's actually going on

<!-- WRITE: ~150 words.
     - "Environment" = interpreter + installed packages + the system libs they link against.
     - requirements.txt is a wish, not a record: no hashes, no interpreter pin, no cross-platform guarantee.
     - Introduce the two commands that carry the whole course: `uv sync` (make my env match the lock)
       and `uv run` (run this inside that env, and check it's current first).
     - Make the speed point: when installs take 2 seconds instead of 20 minutes, you stop hoarding
       one giant environment and start making one per project. Speed changes behaviour. -->

## 🍳 Recipe — your first reproducible environment

<!-- WRITE: install uv (all 3 platforms), then:
     uv init --python 3.12 demo && cd demo
     uv add scikit-learn pandas
     uv run python -c "import sklearn; print(sklearn.__version__)"
     Show the four files uv created and say what each is for:
       pyproject.toml (what I support) / uv.lock (what I ran) / .python-version / .venv
     End with: `git add pyproject.toml uv.lock .python-version` and note .venv is NOT committed. -->

## ⚠️ Sharp edges

<!-- WRITE:
     - Do not `pip install` into a uv-managed .venv; the lock stops being true. Use `uv add`.
     - Never commit .venv (it's machine-specific and huge). Do commit uv.lock.
     - `uv run` re-syncs before running. That is a feature, not a delay. -->

## ✅ Check yourself

<!-- WRITE: 2 questions + <details> answers.
     Q1: Which of the four files would you send a colleague so they get your exact environment?
     Q2: What does `uv run pytest` do that `pytest` does not? -->

## 📖 Go deeper

- [uv — Getting started](https://docs.astral.sh/uv/getting-started/)
- [Python Packaging User Guide — installing packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)
