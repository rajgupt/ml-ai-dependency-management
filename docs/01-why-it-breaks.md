# M1 · Why ML dependencies break 🟢

> ⏱ 10 minutes · Route: Full, Notebook-first
>
> This is the only theory module in the book. Everything after it is commands.

## 3 a.m. story

*The model trains fine on your laptop. On the training cluster it dies with
`CUDA error: no kernel image is available for execution on the device`. Same
`requirements.txt`. Same git SHA. Same `torch==2.6.0`.*

## What's actually going on

### The four-layer stack

<!-- WRITE: this diagram is the spine of the whole book. Reference docs/assets/four-layer-stack.svg.

     ┌─ Layer 4: Python packages      ← pip/uv controls this
     ├─ Layer 3: Python interpreter   ← uv controls this
     ├─ Layer 2: System libraries     ← CUDA runtime, glibc, BLAS, ffmpeg, libGL
     └─ Layer 1: Hardware & driver    ← nvidia driver, CPU arch

     The point, in one sentence: most ML dependency pain lives BELOW the layer pip controls,
     which is why "just pin your requirements" is advice that keeps failing you.
     Every later module says which layer it's operating on. -->

### Abstract vs concrete dependencies

<!-- WRITE: ~120 words + a two-column table.
     Abstract = "what I support", loose ranges, lives in pyproject.toml, for humans and resolvers.
     Concrete = "what I actually ran", exact versions + hashes, lives in uv.lock, for machines.
     You need BOTH. Most teams have only one, and it's the wrong one.
     Corollary — pinning policy:
       Applications/pipelines: loose ranges in pyproject, hard pins in the lock, deploy from lock.
       Libraries: loose ranges, no committed lock in the published artifact, test against a matrix. -->

### The diamond problem

<!-- WRITE: short worked example. A needs numpy<2, B needs numpy>=2, you need both.
     Explain what a resolver does, what "resolution impossible" means, and the three real fixes
     (upgrade A, drop B, or split into two environments). Forward-reference M2's constraints/overrides. -->

### SemVer, and why ML libraries ignore it

<!-- WRITE: ~100 words. A patch bump in transformers or a minor bump in scikit-learn can move your
     metrics without breaking any API. The contract you care about is numerical, and SemVer
     does not cover it. Consequence: for ML, "no API break" is not "safe to upgrade" —
     which is why M8's upgrade ritual runs an eval set, not just a test suite. -->

## ⚠️ The anti-pattern gallery

<!-- WRITE: a table. Each row = anti-pattern | why it feels fine | what it actually costs | the fix (link).
     - `pip freeze > requirements.txt`      → captures your junk, loses your intent, not cross-platform
     - `!pip install` inside a notebook cell → env drifts from the repo, invisible in review
     - `FROM python:3.12` / `:latest` tags   → base image changes under you
     - committing `.venv`                    → machine-specific, huge, still not reproducible
     - `sudo pip install`                    → one env for every project on the box
     - unpinned `transformers`               → silent metric drift
     - `sys.path.append("../..")`            → works in the notebook, dies in CI (fixed in M4) -->

## ✅ Check yourself

<!-- WRITE: Q1: Which layer does the CUDA story above fail at, and why can't a lockfile fix it alone?
           Q2: Your library depends on `pandas`. Do you pin `==2.2.3` in pyproject.toml? Why not? -->

## 📖 Go deeper

- Henry Schreiner — [*Should You Use Upper Bound Version Constraints?*](https://iscinumpy.dev/post/bound-version-constraints/)
- [PEP 508 — dependency specification](https://peps.python.org/pep-0508/)
- [The Turing Way — Reproducible Research](https://book.the-turing-way.org/reproducible-research/reproducible-research)
