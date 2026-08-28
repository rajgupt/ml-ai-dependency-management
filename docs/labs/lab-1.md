# 🧪 Lab 1 · Zero to reproducible in ten commands 🟢

> ⏱ 20 minutes · Needs: `uv`, a terminal. No GPU, no downloads beyond PyPI.
> Start in [`examples/lab1-bootstrap/starter/`](https://github.com/rajgupt/ml-ai-dependency-management/tree/master/examples/lab1-bootstrap/starter)

## The brief

You've been handed `train.py`. It imports `pandas` and `scikit-learn`. There is
no environment, no lockfile, and no pinned Python version — which is to say,
it's most repos.

By the end of this lab you will have destroyed your environment on purpose and
rebuilt it byte-for-byte, and you'll have two export formats ready for the
teammate who refuses to stop using `pip`.

## Step 1 — Create the project

```bash
cd examples/lab1-bootstrap/starter
uv init --bare --python 3.12
uv python pin 3.12
```

`--bare` because `train.py` already exists and we don't want uv's sample code.
Look at what appeared:

```bash
ls -a
cat pyproject.toml
```

- **`pyproject.toml`** — what this project *supports*. You edit this. Note that
  `uv init` already wrote `requires-python = ">=3.12"` from the `--python` flag.
- **`.python-version`** — written by `uv python pin`, and the reason for the
  second command. The interpreter is a dependency too, and it is the one teams
  most often leave unpinned. `requires-python` says which versions are *allowed*;
  `.python-version` says which one you actually use.

Nothing is installed yet. That's correct.

## Step 2 — Add the runtime dependencies

```bash
uv add "pandas>=2.2" "scikit-learn>=1.5"
```

Two new things exist now: a `.venv/` (your environment) and a **`uv.lock`**
(what you *actually got*). Open the lock and skim it — every package, its exact
version, and a hash, for every platform this project supports. That file is the
answer to "but it works on my machine".

> **Ranges, not pins.** We asked for `>=2.2`, not `==2.2.3`. The range says what
> you support; the lock says what you ran. You need both — [M1](../01-why-it-breaks.md).

## Step 3 — Add dev-only tooling

```bash
uv add --group dev pytest ruff
```

Note `--group`, not a plain `add`. This lands in `[dependency-groups]`
(PEP 735), which means it is *invisible to anyone who installs your project*.
Your production image will never see pytest.

Compare the two tables in `pyproject.toml`:

```toml
dependencies = ["pandas>=2.2", "scikit-learn>=1.5"]   # ships

[dependency-groups]
dev = ["pytest>=8.0", "ruff>=0.6"]                    # never ships
```

**Extras ship, groups don't.** That one line resolves most of the confusion
people have about where to put a dependency.

## Step 4 — Run the thing

```bash
uv run python train.py
```

```
test AUC: 0.7531  ->  metrics.json
```

You never activated a virtualenv. `uv run` checked the lock was current, synced
if it wasn't, and ran inside the project environment. Getting out of the habit
of `source .venv/bin/activate` is most of what makes this stick.

## Step 5 — Record what you're about to destroy

```bash
uv pip freeze | sort > /tmp/before.txt
```

## Step 6 — Destroy it

```bash
rm -rf .venv
uv run python train.py
```

Same AUC. uv rebuilt the environment from the lock before running, and it took
about a second.

## Step 7 — Prove it's identical

```bash
uv pip freeze | sort > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt && echo "identical"
```

Empty diff. This is the whole point of the lab: **`uv.lock` + `uv sync` is a
reproducible environment, and it costs you nothing at runtime.**

Now try the two flags CI cares about:

```bash
uv sync --frozen    # install from the lock, never re-resolve
uv sync --locked    # fail loudly if the lock is stale
```

Use `--locked` in CI. It catches the single most common team mistake: editing
`pyproject.toml` and forgetting to re-lock.

## Step 8 — The cliffhanger

There's a test file sitting in `tests/`. Run it.

```bash
uv run pytest
```

```
E   ModuleNotFoundError: No module named 'train'
```

Pytest can't import `train.py`, even though it's *right there*. This is not a
pytest problem and the fix is **not** `sys.path.append("..")`. Your project
isn't installable, so nothing can import it by name — and the same failure is
waiting for you in CI and in your Docker image.

That's [Lab 2](lab-2.md).

## Step 9 — Hand it to a colleague who won't use uv

```bash
uv export --format pylock.toml -o pylock.toml      # PEP 751, the new standard
uv export --no-hashes --no-dev -o requirements.txt # the universal fallback
```

Note `--no-dev`: the export is what production installs, so pytest and ruff
must not appear. Open `requirements.txt` and check.

> ⚠️ These are **exports, not sources of truth**. Regenerate them; never
> hand-edit them. The moment someone edits `requirements.txt` directly, you have
> two conflicting answers to "what does this project need" — which is where you
> started.

## Step 10 — Commit the right things

```bash
cat > .gitignore <<'GITIGNORE'
.venv/
__pycache__/
metrics.json
GITIGNORE

git add pyproject.toml uv.lock .python-version .gitignore train.py tests/
git status
```

Committed: `pyproject.toml`, `uv.lock`, `.python-version`.
Not committed: `.venv/`.

**The lockfile is code.** Review it in PRs — [M8](../08-supply-chain.md) shows
what to look for in a lock diff.

## ✅ You should now be able to answer

<details>
<summary>Which files would you send a colleague so they reproduce your environment exactly?</summary>

`pyproject.toml`, `uv.lock` and `.python-version`. The first two are the
intent and the resolution; the third is the interpreter, which people forget
is a dependency until a project breaks on 3.13.
</details>

<details>
<summary>CI runs <code>uv sync --frozen</code>. A teammate adds a dependency to pyproject.toml and forgets <code>uv lock</code>. Does CI catch it?</summary>

No. `--frozen` installs from the lock without checking whether the lock matches
`pyproject.toml`, so CI happily builds an environment missing the new package —
and fails later, somewhere confusing. `--locked` fails immediately with a clear
message. Use `--locked` in CI, `--frozen` in your Dockerfile where the lock is
already known good.
</details>

<details>
<summary>You need <code>ruff</code>. Runtime dependency, dev group, or <code>uv tool</code>?</summary>

Dev group if the whole team must have the same version (usually what you want,
because a linter version bump changes CI results). `uv tool install ruff` /
`uvx ruff` if it's your personal preference and not project policy. Never a
runtime dependency — nobody running your model needs a linter.
</details>

## 📖 Go deeper

- [uv — Locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/)
- [PEP 735 — Dependency Groups](https://peps.python.org/pep-0735/)
