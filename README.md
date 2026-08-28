# Dependency Management for ML & AI Projects

### A practitioner's cookbook

Your model trains on your laptop. It fails on the cluster with the same
lockfile, the same git SHA and the same `torch==2.6.0`. Your notebook imports a
module that CI swears doesn't exist. A metric moved 0.6% and nobody can say
which of 214 packages did it.

This book fixes those, in under three hours, with commands you can paste.

---

## What you get

- **8 short modules**, one theory chapter, everything else recipes
- **3 hands-on labs** with starter and solution repos that actually run
- A **[Dependency Health Checklist](docs/appendix/checklist.md)** to score your own repo on Monday
- A **[recipe index](docs/10-recipe-index.md)** and a **[uv cheat sheet](docs/appendix/cheatsheet.md)** to keep

## Who it's for

Working data scientists, ML engineers and MLOps/platform folks. You can write
Python and you've used `pip` and a notebook. No packaging knowledge assumed —
and three routes through the book so a senior engineer isn't stuck reading M0.

**[Start here → How to use this book](docs/how-to-use.md)**

## The through-line

Most "dependency management" advice is written for web services, where the
dependency tree is the whole problem. In ML it's the *top layer* of four:

```
Layer 4  Python packages       ← pip and uv control this
Layer 3  Python interpreter    ← uv controls this
Layer 2  System libraries      ← CUDA runtime, glibc, BLAS, ffmpeg
Layer 1  Hardware and driver   ← nvidia driver, CPU architecture
```

Most ML breakage lives below the layer pip controls. That's why "just pin your
requirements" keeps failing you, and it's the idea every module hangs off.

## The labs

| Lab | You build | Time |
|---|---|---|
| [1 · Zero to reproducible](docs/labs/lab-1.md) | A locked environment you destroy and rebuild byte-for-byte | 20 min |
| [2 · Notebook → package](docs/labs/lab-2.md) | A messy notebook refactored into a pip-installable package | 20 min |
| [3 · Ship it and keep it alive](docs/labs/lab-3.md) | GPU/CPU split from one lockfile, CI, an upgrade that breaks | 25 min |

Code lives in [`examples/`](examples/lab1-bootstrap/starter/README.md). Every solution is built and run in CI, so
the commands in this book are not aspirational.

---

## Status

Under construction. [`COURSE-PLAN.md`](COURSE-PLAN.md) is the curriculum design.

| Piece | State |
|---|---|
| Curriculum, timings, reading list | done |
| Book scaffold, `SUMMARY.md`, PDF pipeline | done |
| Labs 1 & 2 — briefs and working example repos | done |
| Lab 3 — brief written, example repo | brief only |
| Modules M0–M8 — outlines in place, prose | outlines only |

## Building the book locally

```bash
npx honkit serve          # http://localhost:4000
npx honkit pdf . book.pdf # needs the honkit docker image or calibre
```

CI builds both on every push and attaches the PDF to each release.
