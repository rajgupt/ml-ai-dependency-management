# 🧪 Lab 3 · Ship it and keep it alive 🔵🔴

> ⏱ 25 minutes · **Stretch / take-home.** The core 3-hour path ends at
> [M8](../08-supply-chain.md); this lab is the one to do at your desk on Monday
> against your own repo.
>
> Needs: `uv`, Docker. **No GPU** — you write and validate the GPU dependency
> *configuration* on a laptop, which is the part that actually goes wrong.
>
> Status: **example repo not built yet** (see [COURSE-PLAN.md](https://github.com/rajgupt/ml-ai-dependency-management/blob/master/COURSE-PLAN.md) phase 2).
> This page is the brief; `examples/lab3-ship/` is coming.

## The brief

You start from the finished `churnkit` of [Lab 2](lab-2.md). It runs on your
laptop and nowhere else. By the end it runs on a GPU cluster, in a 400 MB
container, with CI that fails when the lock goes stale, an SBOM, and a working
upgrade ritual.

## Step 1 — One lockfile, CPU laptops and a GPU cluster

<!-- WRITE: the marker split from M6, applied.
     - Add torch behind the [gpu] extra.
     - Two explicit indexes (cpu, cu128) with `explicit = true`.
     - Markers: darwin/arm64 → cpu wheels; linux x86_64 → cu128.
     - `uv lock`, then inspect the lock to SEE both resolutions in one file.
       That inspection is the payoff — the reader should physically look at the
       two torch entries and realise the universal lock is doing real work.
     - Validate without a GPU: `uv sync --extra gpu --python-platform linux --dry-run`.
       Confirm this flag combination before publishing the lab. -->

## Step 2 — Two containers, one project

<!-- WRITE:
     - Dockerfile.train and Dockerfile.serve from one pyproject.
     - Base image pinned by digest.
     - The cache trick: `uv sync --frozen --no-install-project --no-dev` BEFORE
       `COPY src/`, so source edits don't rebuild the dependency layer.
     - `docker images` and put the two sizes in a table. The size delta between
       train (with torch + jupyter) and serve (neither) is the whole argument.
     - ENTRYPOINT ["churn-train"] — the console script from Lab 2. -->

## Step 3 — CI that catches the mistakes people actually make

<!-- WRITE: .github/workflows/ci.yml
     - astral-sh/setup-uv with cache enabled.
     - `uv sync --locked` — the step that fails when someone edits pyproject.toml
       and forgets to re-lock. Demonstrate the failure on purpose first.
     - `uv run pytest`, `uv run ruff check`.
     - `uvx pip-audit`.
     - CycloneDX SBOM, uploaded as an artifact.
     Keep the YAML under 40 lines; readers copy this one verbatim. -->

## Step 4 — The upgrade ritual, with a planted break

<!-- WRITE: the deliberately-broken step, and the most valuable 8 minutes of the course.
     - The starter pins an old dep whose newer version changes behaviour.
     - `uv lock --upgrade-package <pkg>`
     - `git diff uv.lock` — teach reading a lock diff: new transitive packages,
       a major bump hiding behind a minor one, a changed index source.
     - Tests pass. The eval-set AUC moved. Find out why.
     - Land M1's point: SemVer does not cover numerics, so "tests pass" is not
       "safe to merge" for an ML project. The eval gate is the fix. -->

## ✅ You should be able to answer

<!-- WRITE: Q1: Why does `COPY src/` come after the dependency sync in the Dockerfile?
           Q2: Your bot bumps a dep, CI is green, AUC dropped 0.006. Merge or not, and what
               would you have needed in place to answer that in under a minute?
               (Answer: the run manifest from M7 and a recorded baseline.) -->

## 📖 Go deeper

- [uv — Docker integration](https://docs.astral.sh/uv/guides/integration/docker/)
- [uv — GitHub Actions integration](https://docs.astral.sh/uv/guides/integration/github/)
- [CycloneDX Python](https://github.com/CycloneDX/cyclonedx-python)
