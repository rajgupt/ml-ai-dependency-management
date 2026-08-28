# 🧪 Lab 3 · Ship it and keep it alive 🔵🔴

> ⏱ 25 minutes for the **Core** path · **Stretch / take-home.** The core
> 3-hour path ends at [M8](../08-supply-chain.md); this lab is the one to do
> at your desk on Monday against your own repo. It is not on the clock the way
> Labs 1–2 are — do the Core steps in one sitting, and come back for the
> Optional ones whenever you actually need them.
>
> Needs: `uv`, Docker (Core), a GitHub repo (Optional Step 3). **No GPU** — you
> write and validate the GPU dependency *configuration* on a laptop, which is
> the part that actually goes wrong. Start in
> [`examples/lab3-ship/starter/`](../../examples/lab3-ship/starter/README.md).

## The brief

You start from the finished `churnkit` of [Lab 2](lab-2.md). It runs on your
laptop and nowhere else — no container, no CI, and (planted on purpose) a
dependency pinned a couple of major versions behind. This lab has four steps,
split into two lanes:

| Lane | Steps | Time | Why here |
|---|---|---|---|
| **Core — do these** | 2 (containers), 4 (upgrade ritual) | ~25 min | Self-contained, hands-on, the highest payoff per minute. |
| **Optional — go deeper** | 1 (GPU/CPU split), 3 (CI workflow) | whenever you have more time | Step 1 is a recipe to *read and understand* — most readers can't test the GPU side on a laptop anyway. Step 3 is a file you copy, push, and let run in the background. |

Steps 2 and 4 are independent of each other and of Steps 1 and 3 — do all
four in any order that fits your afternoon, or just the Core two.

---

## Core

### Step 2 — Two containers, one project

Two Dockerfiles, one `pyproject.toml`, one `uv.lock`. `Dockerfile.train`
installs the `gpu` extra (torch); `Dockerfile.serve` doesn't. Everything else
— base image, caching trick, `COPY` order — is identical on purpose, so
diffing the two files *is* the lesson:

```dockerfile
# Dockerfile.train
FROM python:3.12-slim@sha256:09f7da3bc104798d0afb40bc08d23ab2da20a76130cec1f2ef170848f5d85217 AS deps
COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /usr/local/bin/
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev --extra gpu

FROM deps AS build
COPY src/ src/
RUN uv sync --frozen --no-dev --extra gpu

FROM python:3.12-slim@sha256:09f7da3bc104798d0afb40bc08d23ab2da20a76130cec1f2ef170848f5d85217 AS train
WORKDIR /app
COPY --from=build /app/.venv .venv
COPY --from=build /app/src src
ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT ["churn-train"]
```

`Dockerfile.serve` is the same file with `--extra gpu` dropped from both
`RUN uv sync` lines and the final stage renamed `serve`. Full files:
[`Dockerfile.train`](../../examples/lab3-ship/solution/Dockerfile.train),
[`Dockerfile.serve`](../../examples/lab3-ship/solution/Dockerfile.serve).

**Base image pinned by digest, not tag.** `python:3.12-slim` is a moving
target; the digest above is that exact image, immutable, forever. You don't
need a local Docker daemon to resolve one — the registry API answers it
directly:

```bash
TOKEN=$(curl -s "https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/python:pull" | jq -r .token)
curl -s -H "Authorization: Bearer $TOKEN" \
  -H "Accept: application/vnd.oci.image.index.v1+json" \
  https://registry-1.docker.io/v2/library/python/manifests/3.12-slim -D - -o /dev/null \
  | grep -i docker-content-digest
```

```
docker-content-digest: sha256:09f7da3bc104798d0afb40bc08d23ab2da20a76130cec1f2ef170848f5d85217
```

That's the real digest for `python:3.12-slim` as of this writing (August
2026) — the same thing `docker pull python:3.12-slim && docker inspect
--format='{{index .RepoDigests 0}}' python:3.12-slim` gives you if you'd
rather use a daemon you already have running. Either way: resolve it once,
commit it like a lockfile, and re-resolve it on your own upgrade cadence — it
will not track base-image patches for you.

**The dependency layer is copied and installed *before* source.**
`COPY pyproject.toml uv.lock ./` then `uv sync --frozen --no-install-project`
installs every dependency but skips the project itself (`--no-install-project`
— there's no `src/` yet). Docker caches layers by their inputs, so as long as
`pyproject.toml`/`uv.lock` don't change, that layer is reused untouched no
matter how many times `src/` changes. Only the `build` stage — the one that
copies `src/` — reruns on a code edit, and it's fast because dependencies are
already sitting in the venv. Get the `COPY` order backwards and every commit
invalidates every layer.

```bash
docker build -f Dockerfile.train -t churnkit:train .
docker build -f Dockerfile.serve -t churnkit:serve .
docker images churnkit
```

> ⏱ **Slow the first time, that's normal.** `docker build` for
> `Dockerfile.train` pulls the base image plus torch and its CUDA libraries
> (multiple GB — see the size note below) on a cold cache; `Dockerfile.serve`
> is much faster since it skips torch entirely. Both are fast on every
> *subsequent* build — that's the whole point of the cached dependency layer.

The numbers below are representative, not a byte-for-byte capture from a
specific build machine — build both yourself and put your own `docker images`
output here for your repo. This project's `gpu` extra resolves plain,
un-indexed `torch` from PyPI (Step 1's pytorch.org index split isn't wired
into this checked-in `pyproject.toml` — see that section for why), and PyPI's
own Linux torch wheel today pulls in the full CUDA toolkit as a dependency
regardless of whether you asked for a specific backend. So expect the same
range [M6](../06-gpu-and-system-deps.md) already quotes for this pattern:

| Image | Contains | Typical size |
|---|---|---|
| `churnkit:train` | base + pandas/scikit-learn + torch + bundled CUDA libraries + `src/` | commonly 6–8 GB |
| `churnkit:serve` | base + pandas/scikit-learn + `src/` — no torch, no dev/notebook groups | commonly under 500 MB |

Pin torch to the `cpu` index from Step 1 for your *serving* image specifically
(never `cu128`) and that upper number drops by an order of magnitude — most
serving workloads don't need a GPU build of torch at all, only training does.

The gap is the whole argument for Step 2: every package in it is attack
surface and pull time you'd otherwise pay on every replica, for a serving
request that never touches torch.

`ENTRYPOINT ["churn-train"]` — not `["python", "src/cli.py"]` — is the
console script from [Lab 2](lab-2.md): it exists because the package is
installed, it's versioned with the image, and it doesn't care what `WORKDIR`
Docker left you in. (`churnkit` only ever grew a training script — a real
serving image would swap this line for `churn-serve`, `uvicorn`, or whatever
your inference entrypoint is. The pattern being taught here is the dependency
footprint, not the entrypoint name.)

**✅ Checkpoint:** `docker images churnkit` lists both tags, and `serve` is
visibly smaller than `train`. If they're the same size, `--extra gpu` didn't
actually get dropped from `Dockerfile.serve` — diff the two files again.

### Step 4 — The upgrade ritual, with a planted break

Open [`examples/lab3-ship/starter/`](../../examples/lab3-ship/starter). Its
`pyproject.toml` pins `scikit-learn>=1.3` — loose enough to look normal, and
nobody has re-locked since scikit-learn 1.3.2 was current. Train it:

```bash
cd examples/lab3-ship/starter
uv sync --locked
uv run churn-train --rows 8000
```

```
test AUC: 0.7473  ->  metrics.json
```

This is fully deterministic — synthetic data with a fixed seed, a fixed
`random_state` on the split and the model (see
[`src/churnkit/data.py`](../../examples/lab3-ship/solution/src/churnkit/data.py)
and [`model.py`](../../examples/lab3-ship/solution/src/churnkit/model.py)) — so you should
see **exactly** `0.7473`, not something close to it.

Now do the upgrade:

```bash
uv lock --upgrade-package scikit-learn
uv sync --locked
uv run pytest -q
uv run churn-train --rows 8000
```

```
5 passed in 1.4s
test AUC: 0.7506  ->  metrics.json
```

Tests pass. The AUC moved — deterministically, from exactly `0.7473` to
exactly `0.7506`, purely from upgrading one dependency scikit-learn allowed
you to upgrade all along. Nothing else changed: same data, same seed, same
`max_iter`. Before you shrug it off as noise, read the diff:

```bash
git diff uv.lock
```

```diff
 [[package]]
+name = "narwhals"
+version = "2.25.0"
+source = { registry = "https://pypi.org/simple" }
+...
+
+[[package]]
 name = "nbformat"
 ...

 [[package]]
 name = "scikit-learn"
-version = "1.3.2"
+version = "1.9.0"
 source = { registry = "https://pypi.org/simple" }
 dependencies = [
     { name = "joblib" },
+    { name = "narwhals" },
     { name = "numpy" },
     { name = "scipy" },
     { name = "threadpoolctl" },
 ]
```

Two things this diff is teaching you to read:

- **A new transitive dependency showed up** (`narwhals`, a dataframe
  compatibility shim scikit-learn now depends on) that nobody asked for by
  name. That's normal for a real upgrade and exactly why you review a lock
  diff instead of skimming a changelog.
- **The version jump is visible, but it wouldn't always be.** Here it's
  `1.3.2 -> 1.9.0` in plain sight. On a real project this is often a *minor*
  bump in your direct dependency (`scikit-learn>=1.5` looks the same before
  and after) while a transitive dependency underneath it takes a major jump —
  read the whole diff, not just the package you meant to touch.

The AUC move traces to `HistGradientBoostingClassifier` itself, not the data:
the synthetic customers are byte-identical under both scikit-learn versions
(numpy's random-generator stream is guaranteed stable across versions, and
this was checked directly — same seed, same rows, same hash, both before and
after). What changed is the tree-boosting implementation itself, across the
roughly two years and six scikit-learn releases between 1.3.2 and 1.9.0.

**Land the point:** SemVer covers API compatibility, not numerics. `pytest`
has no idea what AUC is; it saw `test_model_beats_a_coin_flip` pass and moved
on. A dependency bot that only checks "tests green" would merge this without
a human ever seeing `0.7473 -> 0.7506`. The fix is an eval-set regression gate
in CI — comparing against a recorded baseline, not just running `pytest` — so
a metric move gets a human's eyes before it ships, the same way a code review
does for logic.

**✅ Checkpoint:** you saw `0.7473` before, `0.7506` after, both tests-green.
If your numbers don't match exactly, `uv sync --locked` before training —
you're likely still on the pre-upgrade lock.

---

## Optional — go deeper

### Step 1 — One lockfile, CPU laptops and a GPU cluster

You won't run most of this end to end on a laptop — that's fine, that's the
point of `--dry-run`. Read the recipe, understand what it buys you, and keep
it for the day you actually own a GPU cluster.

Add torch behind the `gpu` extra with an explicit index per backend:

```toml
[project.optional-dependencies]
gpu = ["torch>=2.6"]

[[tool.uv.index]]
name = "pytorch-cpu"
url = "https://download.pytorch.org/whl/cpu"
explicit = true

[[tool.uv.index]]
name = "pytorch-cu128"
url = "https://download.pytorch.org/whl/cu128"
explicit = true

[tool.uv.sources]
torch = [
    { index = "pytorch-cpu", marker = "sys_platform == 'darwin' and platform_machine == 'arm64'" },
    { index = "pytorch-cu128", marker = "sys_platform == 'linux' and platform_machine == 'x86_64'" },
]
```

This is the exact recipe from [M6](../06-gpu-and-system-deps.md) — `explicit
= true` keeps each index scoped to the packages that name it, so uv doesn't
consult it for every dependency in your project. Run:

```bash
uv lock
```

> ⏱ **Slow the first time, that's normal.** Resolving this pulls metadata
> from `download.pytorch.org` for both backends, and if you `uv sync` the CPU
> path locally it downloads torch's CPU wheel — hundreds of MB. That's the
> network cost of the split, not a stuck command.

Then open `uv.lock` and find `torch` — **twice**. One entry sourced from the
`pytorch-cpu` index, one from `pytorch-cu128`, each with its own hashes. That
inspection is the actual payoff: one `uv lock` run, one file, and it already
contains the resolution for a machine you've never touched.

Validate the cluster path without a GPU or a multi-gigabyte download:

```bash
uv sync --extra gpu --python-platform linux --dry-run
```

Verified against uv 0.8.17: this exact flag combination is accepted and
performs a dry run of the `linux`/`cu128` resolution path without installing
anything — `uv sync --help` confirms both `--python-platform` and `--dry-run`
are current flags on this version. If you're on a newer uv and it's moved,
the intent to keep is "resolve for `linux`, don't install."

> ⚠️ **Sharp edge.** `download.pytorch.org` sits behind whatever network
> policy your machine or CI runner has. A locked-down corporate proxy or an
> air-gapped build box that only allowlists `pypi.org` will fail `uv lock`
> here with a connection error at the CONNECT stage — that's a network
> policy problem, not a broken recipe. (This is exactly what happened while
> building this course's own example repo — see
> [`examples/lab3-ship/solution/README.md`](../../examples/lab3-ship/solution/README.md)
> for the full story, and why the checked-in example doesn't wire this recipe
> into its own lock.) If `uv lock` hangs or errors here, check that host is
> reachable before you assume the TOML is wrong.

### Step 3 — CI that catches the mistakes people actually make

Copy [`ci.yml`](../../examples/lab3-ship/solution/.github/workflows/ci.yml)
into your repo's `.github/workflows/`, push it, and go re-read the earlier
steps while GitHub Actions runs — this isn't something you sit and watch.

```yaml
name: ci

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - run: uv sync --locked

      - run: uv run pytest -q
      - run: uv run ruff check .
      - run: uvx pip-audit

      - name: Generate SBOM
        run: |
          uvx --from cyclonedx-bom cyclonedx-py environment .venv \
            --pyproject pyproject.toml -o sbom.json
      - uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.json
```

> ⏱ **Slow the first time, that's normal.** `enable-cache: true` restores
> uv's cache on later runs, but the *first* run on a fresh repo installs
> everything cold — a minute or two is normal for a project this size, longer
> once torch is in the picture.

`uv sync --locked` is the step worth breaking on purpose before you trust it.
Edit a dependency into `pyproject.toml` without re-locking and run it:

```bash
uv sync --locked
```

```
Resolved 87 packages in 291ms
The lockfile at `uv.lock` needs to be updated, but `--locked` was provided. To update the lockfile, run `uv lock`.
```

That's the real, captured error — `--locked` fails immediately instead of
quietly installing an environment that doesn't match `pyproject.toml`. This
is the single most common team mistake `--locked` exists to catch: someone
edits `pyproject.toml`, forgets `uv lock`, and every teammate who pulls gets
a working `uv sync --frozen` that's silently missing a package. Run
`uv lock` and rerun to confirm it goes green, then revert the experiment.

`uvx pip-audit` and the SBOM step both ran clean against this project as
written — `pip-audit` reported "No known vulnerabilities found," and
`cyclonedx-py environment` produced a valid CycloneDX JSON document listing
every installed package with its PyPI metadata. Neither needs a lockfile
change to work; both read whatever's actually installed.

**✅ Checkpoint:** push the workflow, then deliberately edit
`pyproject.toml` without locking on a branch — the `uv sync --locked` step
should go red, exactly like the terminal output above.

---

## ✅ You should be able to answer

<details>
<summary>Why does <code>COPY src/</code> come after the dependency sync in the Dockerfile?</summary>

Docker caches layers by their inputs. `COPY pyproject.toml uv.lock ./` then
`uv sync --frozen --no-install-project` only changes when those two files
change, so as long as your dependencies are stable, that layer is reused on
every build no matter how many times `src/` changes. Put `COPY src/` first
and Docker invalidates the dependency layer on every source edit — a full
re-resolve and re-download on every commit instead of a build that reuses
everything but the last few seconds of work.
</details>

<details>
<summary>Your bot bumps a dependency, CI is green, AUC dropped 0.006. Merge or not — and what would you have needed to answer that in under a minute?</summary>

Not automatically — a passing `pytest` only proves the code still runs, not
that the model is still as good; SemVer and green tests don't cover numerics
(that's the whole lesson of Step 4). To answer this in under a minute rather
than re-running an investigation from scratch, you need the run manifest from
[M7](../07-reproducibility.md) — lock hash, git SHA, data version and a
*recorded baseline AUC* emitted with every training run — plus an eval-set
regression gate in CI that fails the build itself when a metric move exceeds
a threshold, so "AUC dropped 0.006" is a red check you see before merge, not
a discovery three weeks later.
</details>

## 📖 Go deeper

- [uv — Using uv with PyTorch](https://docs.astral.sh/uv/guides/integration/pytorch/)
- [uv — Docker integration](https://docs.astral.sh/uv/guides/integration/docker/)
- [uv — GitHub Actions integration](https://docs.astral.sh/uv/guides/integration/github/)
- [CycloneDX Python](https://github.com/CycloneDX/cyclonedx-python)
