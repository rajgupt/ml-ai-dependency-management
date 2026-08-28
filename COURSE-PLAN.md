# Course Plan — *Dependency Management for ML & AI Projects: A Practitioner's Cookbook*

> Status: plan / curriculum design. Nothing has been built yet.
> Target format: GitBook-compatible Markdown in this repo → hosted book + downloadable PDF.

---

## 1. Course identity

| | |
|---|---|
| **Title** | Dependency Management for ML & AI Projects — A Practitioner's Cookbook |
| **Subtitle** | Stop shipping "works on my machine" models. |
| **Audience** | Working data scientists, ML engineers, MLOps/platform engineers. Mixed seniority (0–15 yrs). |
| **Prereqs** | Can write Python, has used `pip` and a notebook. No packaging knowledge assumed. |
| **Duration** | **≤ 3 hours** total. Core path ≈ 155 min; Lab 3 is a 25-min stretch/take-home. |
| **Format** | Self-paced, read-and-do. Every module ends in a copy-pasteable **Recipe Card**. |
| **Promise** | By the end you can bootstrap, package, lock and audit an ML project — and hand it to a colleague who reproduces it on the first try. |

### Design principles

1. **Cookbook, not textbook.** Theory only where it prevents a specific bug. Ratio target: ~25% concept / ~75% commands, diffs, and "what breaks if you don't".
2. **Every concept is introduced by a failure.** Each module opens with a 3–5 line *"3 a.m. story"* — a real symptom (`CUDA error: no kernel image`, `ModuleNotFoundError` only in CI, a metric that moved 0.4% after a rebuild). Then the fix.
3. **One tool spine.** `uv` is the default throughout so nobody spends the 3 hours comparing tools. Alternatives get one honest comparison table and a "when you actually need conda/pixi" decision tree.
4. **Copy-paste must work.** Every command block is tested in CI against a scratch container.
5. **Take-home value.** Course ends with a 1-page **Dependency Health Checklist** the student can run against their real repo on Monday.

### Handling mixed experience

Each recipe carries a level badge, and the ToC offers three routes:

- 🟢 **Everyone** — works on any project you touch.
- 🔵 **You own a repo** — packaging, CI, lock policy.
- 🔴 **You own the platform** — registries, base images, org-wide policy.

| Route | Who | Time | Path |
|---|---|---|---|
| **Full** | DS/MLE new to packaging | ~3 h | M0 → M8 + Labs 1–3 |
| **Fast** | Senior engineers | ~75 min | M2, M4, M6 + Lab 1 + Checklist |
| **Notebook-first** | Analysts / researchers | ~90 min | M0, M1, M2, Lab 1, M5, M7 |

---

## 2. Module map (with time budget)

### Part I — Foundations *(55 min)*

**M0 · Setup & the 5-minute win** — 10 min 🟢
Install `uv`. Run one command that creates a fully pinned, GPU-aware environment for a toy training script. The point is momentum: the student sees the payoff before any theory.
*Concepts:* what a "resolved environment" is; why speed changes behaviour (a 2-second install means you stop hoarding one giant env).

**M1 · Why ML dependencies break (the only theory module)** — 10 min 🟢
*Concepts:*
- **The four-layer stack**: GPU driver → system libs (CUDA runtime, glibc, BLAS, ffmpeg) → Python interpreter → Python packages. Most ML breakage lives *below* the layer pip controls. This single diagram is the spine of the whole course.
- **Abstract vs concrete dependencies** — loose ranges in `pyproject.toml` (what you *support*), exact pins in a lockfile (what you *ran*).
- **Application vs library policy** — apps pin hard, libraries stay permissive.
- **The diamond problem** & why resolvers fail; SemVer, and why the ML ecosystem routinely breaks it (a minor `transformers` bump changing outputs).
- Anti-pattern gallery: `pip freeze > requirements.txt`, `!pip install` in a cell, `latest` image tags, committing `.venv`, `sudo pip install`, mixing conda and pip carelessly.

**M2 · `uv` as your one tool** — 25 min 🟢🔵
*Concepts & recipes:*
- `uv init` / `add` / `remove` / `sync` / `run` / `lock`; the managed `.venv`; `uv python install` (interpreter is a dependency too).
- **Lockfiles that actually reproduce**: `uv.lock` (universal, cross-platform, hashed) vs `requirements.txt` vs **PEP 751 `pylock.toml`**. `uv sync --frozen` / `--locked` as the CI contract.
- **Dependency groups (PEP 735)** `[dependency-groups]` for `dev`/`docs`/`lint` vs **extras** (`[project.optional-dependencies]`) for `gpu`/`serve` that users install. Clear rule of thumb: *extras ship, groups don't.*
- Interop escape hatches: `uv export --format pylock.toml`, `uv export -o requirements.txt` for the colleague stuck on plain pip, `uv pip install` as a drop-in.
- `uv tool install` / `uvx` — stop polluting project envs with `ruff`, `pre-commit`, `jupyter`.
- Reading a resolution failure and fixing it (constraints, overrides, `--resolution lowest-direct`).

**M3 · 🧪 Lab 1 — "Zero to reproducible in ten commands"** — 20 min 🟢

### Part II — Make it yours *(60 min)*

**M4 · Ship your project as a package** — 25 min 🔵
*Concepts & recipes:*
- `pyproject.toml` anatomy (PEP 621), build backends (PEP 517/518) — recommend `hatchling`; why `setup.py` is legacy.
- **`src/` layout** and why it prevents the classic "imports in the notebook, `ModuleNotFoundError` in CI" shadowing bug.
- Editable installs (`uv sync` does it; `pip install -e .` equivalent) — the end of `sys.path.append("../..")`.
- **Entry points / console scripts**: turn `python scripts/train_v3_final_FINAL.py` into `mlproj train --config configs/base.yaml`.
- Wheels vs sdists; `uv build`; version single-sourcing; when to publish to an internal index vs install from git.
- Splitting a repo: `src/pkg/` (library) + `configs/` + `notebooks/` + `tests/`; optional `uv` **workspaces** for a monorepo of related packages. 🔴

**M5 · 🧪 Lab 2 — "Notebook → installable package"** — 20 min 🟢🔵

**M6 · Hard mode: GPUs, CUDA and non-Python dependencies** — 25 min 🔵🔴
The module that makes the course ML-specific rather than generic Python.
*Concepts & recipes:*
- CUDA **driver vs runtime vs toolkit**; what `nvidia-smi` actually tells you; why `pip install torch` gives one teammate a 2 GB CPU build and another a broken CUDA build.
- **Wheel tags & environment markers** (PEP 508): `cp312-manylinux_x86_64` vs `macosx_arm64` — "installs on my Mac, fails on the cluster", explained in one table.
- Recipe: pin a torch variant with `[[tool.uv.index]] explicit = true` + `[tool.uv.sources]`, and a marker-split so laptops get CPU wheels and the cluster gets `cu128`. Note the sharp edge: `--torch-backend=auto` works with `uv pip …`, not with `uv add/lock/sync`.
- **Non-Python dependencies** (ffmpeg, libGL, tesseract, NCCL, MKL): decision tree → *system package* vs *conda/**pixi*** vs *deploy image*. One page, no religion.
- **Deploy-image recipe (concepts only, no Dockerfile):** install deps from the lockfile before the project source for a cached dependency layer (`uv sync --frozen --no-dev --no-install-project`), slim runtime image, separate **train vs serve** environments (your serving image should not contain Jupyter), base image pinned by digest not tag. 🔴

### Part III — Make it survive *(40 min + stretch lab)*

**M7 · Reproducibility beyond pip** — 15 min 🟢
*Concepts & recipes:*
- **The reproducibility ladder**: same lock → same env; same env + seed → *usually* same metrics. Honest treatment of nondeterminism (cuDNN kernel selection, atomics, TF32, thread counts, `torch.use_deterministic_algorithms`).
- **Models and data are dependencies too**: pin Hugging Face artifacts by commit SHA (`revision=`), never `main`; version datasets with DVC / lakeFS / object-store paths that include a hash; record the model registry version alongside the lockfile.
- **Notebook hygiene**: kernel ≠ project env (register the venv kernel), no `!pip install` in cells, `nbstripout` in pre-commit, `jupytext` for reviewable diffs, `papermill` for parameterized runs.
- **The run manifest**: lock hash + git SHA + data version + image digest, emitted with every training run. This is the single habit that makes an experiment reproducible six months later.

**M8 · Supply chain & upgrade hygiene** — 12 min 🟢🔵🔴
*Concepts & recipes:*
- ML-specific attack surface: **`pickle` / `torch.load` is arbitrary code execution** → prefer `safetensors`, use `weights_only=True`; a model download from a hub is untrusted code, not data.
- PyPI typosquatting and **dependency confusion** with internal package names; why `--index-strategy` and explicit index pinning matter for private registries. 🔴
- Auditing: `pip-audit` / `uv pip audit`, OSV, hash-pinned installs, **SBOM** generation (CycloneDX) for the model service.
- **Upgrade ritual**: Renovate/Dependabot on a schedule, `uv lock --upgrade-package X`, review the lock diff like code, canary env + eval-set regression check before merging a `transformers` bump.
- Pinning policy: when upper bounds help and when they poison the ecosystem (linked debate, both sides).

**M9 · 🧪 Lab 3 (stretch / take-home) — "Ship it and keep it alive"** — 25 min 🔵🔴

**M10 · Recipe index + Dependency Health Checklist** — 3 min 🟢
Every recipe card collected on one page + a scored checklist to run against a real repo.

**Core total: 155 min. With Lab 3: 180 min.**

---

## 3. The three tutorials

Each lab: a starting repo branch, a 20-line brief, checkpoints with expected output, a "break it on purpose" step, and a solution branch.

### 🧪 Lab 1 — Zero to reproducible in ten commands *(20 min, 🟢)*
Build a churn-prediction project from empty directory.
1. `uv init`, `uv add scikit-learn pandas`, `uv add --group dev pytest ruff`.
2. Run a training script via `uv run`.
3. **Break it**: `rm -rf .venv`, then `uv sync` → identical environment; diff `uv pip freeze` before/after to prove it.
4. **Hand-off**: `uv export --format pylock.toml` and `uv export -o requirements.txt` for a pip-only teammate.
5. Add a `--group dev` tool and see why it never reaches production.
*Learner walks away with:* a working reproducible loop and the `sync`/`lock` mental model.

### 🧪 Lab 2 — Notebook → installable package *(20 min, 🟢🔵)*
Given `notebooks/churn_messy.ipynb` (with `sys.path` hacks, `!pip install`, hidden state):
1. Extract logic into `src/churnkit/{data,features,train}.py`.
2. Write `pyproject.toml` with `hatchling`, deps, a `dev` group, and a `[gpu]` extra.
3. Add `[project.scripts] churn-train = "churnkit.cli:main"`; run `uv run churn-train`.
4. Point the notebook at the installed package (register the kernel, delete the `sys.path` hack), add `nbstripout`.
5. `uv build`, then install the wheel into a throwaway env and import it — proof the packaging is real.
*Learner walks away with:* the pip-installable project pattern, ready to copy onto their own repo.

### 🧪 Lab 3 — Ship it and keep it alive *(25 min, stretch, 🔵🔴)*
1. Add `torch` with a CPU/GPU index split so laptop and cluster resolve differently from **one** lockfile.
2. GitHub Actions: cached `uv sync --locked` (fails the build if the lock is stale) + `pytest` + `pip-audit` + CycloneDX SBOM upload.
3. Run `uv lock --upgrade-package scikit-learn`, read the lock diff, and fix the deliberately planted breakage.
*Learner walks away with:* a CI template and the upgrade ritual.

---

## 4. Book production: hosting + PDF

**Source of truth:** Markdown in this repo with a GitBook-style `SUMMARY.md`, so the content is portable across GitBook, HonKit and MkDocs.

**Recommended pipeline**
- **Hosting:** GitBook.com **Git Sync** against `master` — the reader-facing site gets GitBook's own PDF export for free, and authors keep writing in the repo.
- **PDF in CI (offline fallback / release asset):** [HonKit](https://github.com/honkit/honkit) (maintained fork of GitBook Legacy, same `SUMMARY.md` + `book.json`), whose Docker image `ghcr.io/honkit/honkit` already bundles the PDF toolchain. A GitHub Action builds `dependency-cookbook.pdf` and attaches it to each release.
- **Fallback option** if GitBook.com is not available: MkDocs Material + `mkdocs-with-pdf`. Same Markdown, different `SUMMARY`→`nav` mapping. Decide before authoring starts; the `SUMMARY.md` structure keeps both doors open.

**CI checks on every PR:** link check, `uv`-based execution of every fenced command block in a scratch container (this is what keeps the cookbook honest), spell check, PDF build.

### Proposed repo layout

```
.
├── README.md
├── COURSE-PLAN.md            ← this file
├── book.json                 ← HonKit config (title, plugins, pdf options)
├── SUMMARY.md                ← GitBook/HonKit table of contents
├── docs/
│   ├── 00-setup.md … 10-recipe-index.md
│   ├── labs/{lab-1,lab-2,lab-3}.md
│   ├── appendix/{cheatsheet,checklist,glossary,further-reading,tool-comparison}.md
│   └── assets/               ← four-layer diagram, wheel-tag table, decision trees
├── examples/
│   ├── lab1-bootstrap/{starter,solution}/
│   ├── lab2-package/{starter,solution}/
│   └── lab3-ship/{starter,solution}/
└── .github/workflows/{book.yml,test-examples.yml}
```

### Draft `SUMMARY.md`

```markdown
# Summary
* [Read me first](README.md)
* Part I — Foundations
  * [M0 · Setup & the 5-minute win](docs/00-setup.md)
  * [M1 · Why ML dependencies break](docs/01-why-it-breaks.md)
  * [M2 · uv as your one tool](docs/02-uv.md)
  * [🧪 Lab 1 · Zero to reproducible](docs/labs/lab-1.md)
* Part II — Make it yours
  * [M4 · Ship your project as a package](docs/04-packaging.md)
  * [🧪 Lab 2 · Notebook → package](docs/labs/lab-2.md)
  * [M6 · GPUs, CUDA & non-Python deps](docs/06-gpu-and-system-deps.md)
* Part III — Make it survive
  * [M7 · Reproducibility beyond pip](docs/07-reproducibility.md)
  * [M8 · Supply chain & upgrade hygiene](docs/08-supply-chain.md)
  * [🧪 Lab 3 · Ship it and keep it alive](docs/labs/lab-3.md)
* Appendix
  * [Recipe index](docs/10-recipe-index.md)
  * [Dependency Health Checklist](docs/appendix/checklist.md)
  * [uv cheat sheet](docs/appendix/cheatsheet.md)
  * [uv vs pip-tools vs Poetry vs conda vs pixi](docs/appendix/tool-comparison.md)
  * [Glossary](docs/appendix/glossary.md)
  * [Further reading](docs/appendix/further-reading.md)
```

### Page template (keeps every module engaging and uniform)

```
## 3 a.m. story          ← 4 lines, a real symptom
## What's actually going on   ← ≤ 200 words + one diagram
## 🍳 Recipe               ← numbered commands, copy-paste safe
## ⚠️ Sharp edges           ← the 2–3 ways this bites
## ✅ Check yourself        ← 2 questions, answers in a collapsible block
## 📖 Go deeper            ← 1–3 links, never more
```

---

## 5. Further reading (curated, ≤3 links per module)

**Tooling & standards**
- [uv documentation](https://docs.astral.sh/uv/) — projects, lockfiles, workspaces
- [Using uv with PyTorch](https://docs.astral.sh/uv/guides/integration/pytorch/) — the index/marker recipes
- [Python Packaging User Guide](https://packaging.python.org/) — the canonical packaging tutorial
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/) — best single reference for this audience
- [PEP 621](https://peps.python.org/pep-0621/) (project metadata), [PEP 517](https://peps.python.org/pep-0517/)/[518](https://peps.python.org/pep-0518/) (build backends), [PEP 508](https://peps.python.org/pep-0508/) (markers), [PEP 735](https://peps.python.org/pep-0735/) (dependency groups), [PEP 751](https://peps.python.org/pep-0751/) (`pylock.toml`)

**Opinion pieces worth the argument**
- Henry Schreiner, [*Should You Use Upper Bound Version Constraints?*](https://iscinumpy.dev/post/bound-version-constraints/)
- Brett Cannon, [*What's the deal with setuptools, setup.py…*](https://snarky.ca/what-the-heck-is-pyproject-toml/)
- Joel Grus, [*I Don't Like Notebooks*](https://www.youtube.com/watch?v=7jiPeIFXb6U) — used to frame M7, not to dunk on notebooks

**ML-specific**
- [The Turing Way — Reproducible Research](https://book.the-turing-way.org/)
- [NVIDIA Container Toolkit docs](https://docs.nvidia.com/datacenter/cloud-native/) — driver/runtime boundary
- [Hugging Face Hub: revisions & `safetensors`](https://huggingface.co/docs/hub/security-pickle) — pickle risk, stated by HF itself
- [DVC docs](https://dvc.org/doc) — data/model versioning
- [pixi](https://pixi.sh/) and [conda-lock](https://conda.github.io/conda-lock/) — for the non-Python-dependency escape hatch
- [pip-audit](https://github.com/pypa/pip-audit) · [OSV](https://osv.dev/) · [CycloneDX Python](https://github.com/CycloneDX/cyclonedx-python)

---

## 6. Build plan

| Phase | Output | Est. | Status |
|---|---|---|---|
| 1 | Repo scaffold: `SUMMARY.md`, `book.json`, empty module pages with the page template, CI skeleton | 0.5 d | **done** |
| 2 | Example repos for Labs 1–3 (starter + solution branches), tested end-to-end | 1.5 d | Labs 1–2 **done**, Lab 3 pending |
| 3 | Write Parts I–III against the labs (labs first, prose second — keeps it practical) | 3 d | outlines in place |
| 4 | Diagrams (four-layer stack, wheel tags, non-Python decision tree), checklist, cheat sheet | 1 d | not started |
| 5 | PDF pipeline + link/command CI, timing dry-run with 2 pilot readers | 0.5 d | CI **done**, dry-run pending |

**Definition of done:** a pilot reader with no packaging background finishes the core path in under 3 hours, and their own repo scores ≥ 8/12 on the Dependency Health Checklist afterwards.

## 7. Open decisions

1. **Host:** GitBook.com Git Sync (recommended) vs self-hosted HonKit only?
2. **Lab domain:** tabular churn model (fast, tiny deps) — recommended — vs a small LLM fine-tune (more relatable, much heavier downloads and GPU-dependent).
3. **Lab 3 GPU access:** assume none and teach the marker split as *configuration only* (recommended, keeps it laptop-runnable), or provide a Colab/cloud path?
4. **Windows/WSL support** in the labs: first-class or "use WSL"?
