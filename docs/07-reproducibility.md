# M7 · Reproducibility beyond pip 🟢

> ⏱ 15 minutes · **Optional deep-dive** — not on the core path
>
> Read this when you need an experiment to reproduce months later — pinning
> models and data, the run manifest, and honest limits on determinism.

## 3 a.m. story

*A reviewer asks you to reproduce the AUC from a model you trained in March.
The lockfile restores perfectly. The number comes back 0.834 instead of 0.841.
Nothing in the dependency tree changed — but the model card you fine-tuned from
now points at a different commit on the Hub, and the training table gained
40,000 rows.*

## What's actually going on

### The reproducibility ladder

`uv.lock` gets you further than most teams think, and less far than the
optimistic ones hope. Be precise about which rung you're actually on:

| Rung | You control | You get | Guarantee |
|---|---|---|---|
| 1 | Same lock | Same environment | Guaranteed |
| 2 | + same code (git SHA) | Same code path | Guaranteed |
| 3 | + same data version | Same inputs | Your job, not pip's |
| 4 | + same seeds | Same result, CPU | Usually |
| 5 | + same GPU/driver/flags | Same result, GPU | Only with effort |

Rungs 1–2 are what [M1](01-why-it-breaks.md) and [M2](02-uv.md) already gave
you: `uv.lock` plus a commit pins every Python package and the interpreter.
Rung 3 is not a `uv` problem — nothing in the lockfile says which rows of
`train.csv` you used. That's the next section.

Rung 4 is where "usually" starts doing a lot of work. Setting seeds gets you
the same result *on the same hardware, same backend, same everything else* —
which is a narrower claim than it sounds.

Rung 5 is where most teams should stop trying. cuDNN picks a convolution
algorithm per-shape by autotuning, and that choice isn't guaranteed stable
across runs or driver versions. Floating-point addition isn't associative, so
when a reduction runs across a different number of threads or in a different
launch order, atomics reorder it and the last bit flips. TF32 on Ampere-and-later
GPUs silently reduces matmul precision unless you turn it off. Thread counts
change reduction order on CPU too. You can buy back most of this:

```python
import torch

torch.manual_seed(0)
torch.use_deterministic_algorithms(True)
torch.backends.cudnn.benchmark = False
torch.backends.cuda.matmul.allow_tf32 = False
```

`use_deterministic_algorithms(True)` costs you speed — deterministic kernels
are often slower than autotuned ones — and for a handful of ops it doesn't
buy determinism at all; it raises `RuntimeError` instead, because no
deterministic implementation exists yet. That's a feature, not a bug: it
tells you exactly where your "reproducible" run was silently rounding.

**The honest takeaway:** aim for rungs 1–4 on every run — they're cheap and
you should never be without them. Pay for rung 5 only when you actually need
bit-for-bit GPU reproducibility (a regulated audit, a bug you're bisecting),
not as a default, because the training-speed cost is real and most
comparisons only need "close enough to trust the eval," not identical bits.

### Models and data are dependencies too

Your lockfile pins every package that trains the model. It says nothing about
*what* you trained it on or *which* pretrained weights you started from — and
those move at least as often as a PyPI package does.

- **Hugging Face artifacts.** `from_pretrained("org/model")` resolves to
  whatever `main` currently points at. That's the model equivalent of
  `pip install torch` with no version — it will train something today and
  something else in March. Pin the commit SHA instead:

  ```python
  from transformers import AutoModel

  model = AutoModel.from_pretrained(
      "org/model",
      revision="8f3b2c1a9d4e7f60b1c2d3e4f5a6b7c8d9e0f1a2",  # never "main"
  )
  ```

  `revision=` accepts a branch or tag too, but only a full commit SHA is
  actually pinned — branches and tags move under you exactly like `main`
  does.

- **Datasets.** A training run should be able to name the exact data it saw,
  the same way `uv.lock` names the exact packages. DVC, lakeFS, or an
  object-store path that embeds a content hash (`s3://bucket/train/<sha256>.parquet`)
  all satisfy this. The tool matters less than the property: the version is
  *recorded*, not remembered by whoever ran the job.

- **Model registry entries.** If you register trained models (MLflow, W&B
  Artifacts, an internal registry), log that version number next to the lock
  hash in the same place — see the run manifest below. "Which lock built
  this?" and "which weights did it start from?" should be answerable from one
  file, not from someone's memory of which Tuesday this was.

## 🍳 Recipe 1 — the run manifest

This is the single highest-value habit in this module. Every training run —
not just the ones you think you'll need to reproduce, because you never know
in advance which one that'll be — should emit a small JSON file next to its
output:

```python
# manifest.py
import json
import subprocess
import sys
from pathlib import Path

import torch


def git_sha(dirty_ok: bool = True) -> str:
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], text=True).strip())
    if dirty and not dirty_ok:
        raise RuntimeError("refusing to train from a dirty working tree")
    return sha + ("-dirty" if dirty else "")


def lock_hash() -> str:
    import hashlib

    return hashlib.sha256(Path("uv.lock").read_bytes()).hexdigest()[:16]


def write_manifest(path: str, *, data_version: str, seed: int, metrics: dict) -> None:
    manifest = {
        "git_sha": git_sha(),
        "lock_hash": lock_hash(),
        "python_version": sys.version.split()[0],
        "data_version": data_version,               # e.g. DVC rev or object-store hash
        "image_digest": Path("/etc/image-digest").read_text().strip()
        if Path("/etc/image-digest").exists()
        else None,
        "seed": seed,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
        "cuda_runtime": torch.version.cuda,  # what torch was built against, not the driver
        "key_packages": {
            "torch": torch.__version__,
        },
        "metrics": metrics,
    }
    Path(path).write_text(json.dumps(manifest, indent=2))
```

```python
# in train.py, after training
write_manifest(
    "runs/2026-08-28-churn/manifest.json",
    data_version="s3://bucket/train/9f8e7d6c.parquet",
    seed=0,
    metrics={"auc": 0.841},
)
```

Bake the image digest in at build time (`ENV IMAGE_DIGEST=...` written by CI,
or read it from wherever your orchestrator exposes it) so the manifest is
complete without a network call. Six months from now, when someone asks you
to reproduce this run, this file is the difference between "reproduce it" and
"retrain it and hope."

## 🍳 Recipe 2 — notebook hygiene

Notebooks aren't the reproducibility problem. *Hidden state and hidden
installs* are — a notebook just makes both easy to accumulate without
noticing.

**The kernel is not the project env.** Jupyter will happily run your notebook
against whatever kernel was last selected, which is very often not your
project's `.venv`. Register the real one:

```bash
uv add --group dev ipykernel
uv run ipython kernel install --user --name=churnkit --display-name "churnkit (.venv)"
```

Then pick "churnkit (.venv)" in the kernel selector. Or skip kernel selection
entirely and run Jupyter itself through `uv run`:

```bash
uv run --group dev jupyter lab
```

Either way, this one fix removes most instances of "but it worked in the
notebook" — because most of the time the notebook was quietly running
against a different environment than the one in `pyproject.toml`.

**No `!pip install` in cells.** A cell that installs a package is a
dependency that exists nowhere `uv.lock` can see it. If the notebook needs a
package, it goes through the project:

```bash
uv add matplotlib
```

then restart the kernel. The notebook is not a package manager, and every
`!pip install` cell is a dependency your colleague's environment doesn't
have.

**Strip outputs before they hit git.** Notebook outputs are a diff-review and
data-leak problem — cell outputs can contain anything from noisy plots to
actual training data. `nbstripout` removes them at commit time:

```bash
uv add --group dev nbstripout
uv run nbstripout --install
```

Now `git diff` on a notebook shows code changes, not a wall of base64 PNG.

**`jupytext` for reviewable diffs.** Pair the notebook with a plain `.py`
mirror so reviewers can read a real diff instead of raw `.ipynb` JSON:

```bash
uv add --group dev jupytext
uv run jupytext --set-formats ipynb,py:percent notebooks/eda.ipynb
```

**`papermill` for parameterized, scheduled runs.** When a notebook needs to
run unattended with different inputs — a weekly report, a sweep — don't hand-edit
cells. Parameterize and execute it from the CLI:

```bash
uv run papermill notebooks/eval.ipynb runs/eval-2026-08-28.ipynb \
  -p data_version "s3://bucket/eval/9f8e.parquet" \
  -p threshold 0.5
```

The output notebook is itself a record — commit it (stripped) or archive it
next to the run manifest.

## ⚠️ Sharp edges

- **One seed call isn't enough.** `random.seed()`, `np.random.seed()`, and
  `torch.manual_seed()` are three unrelated RNGs. Set all of them, plus
  `PYTHONHASHSEED` (affects dict/set iteration order, which affects anything
  that iterates a set of features or labels), plus the DataLoader worker
  seed (`worker_init_fn`) — a multi-worker DataLoader has its own RNGs that
  the main process's seed does not reach.
- **Out-of-order execution.** A notebook's result depends on the order you
  clicked cells in, not the order they're written in. Before you believe any
  number, or hand a notebook to a colleague, "Restart & Run All" it and
  confirm the metric doesn't move.
- **A HF revision pins the weights, not everything around them.** Tokenizer
  config, chat templates, and preprocessing code sometimes live in a
  companion repo or a separate file that isn't covered by the model's
  `revision=`. Pin those explicitly too if your pipeline depends on them.

## ✅ Check yourself

<details>
<summary>Answer</summary>

**Q1: Your lock restores exactly and metrics still moved. Name two causes
outside the lock.**

Any two of: a different data version (the training table changed underneath
you), an unpinned model revision (`main` moved on the Hub), a seed that
wasn't actually set for every RNG in play (numpy vs torch vs the dataloader
workers), or GPU-side nondeterminism (cuDNN autotuning, TF32, atomics) if the
run used a GPU. The lockfile only covers rung 1–2 of the ladder; the rest is
data, seeds, and hardware — none of which `uv.lock` can see.

**Q2: What does pinning `revision=` buy you that pinning `transformers==`
does not?**

`transformers==` pins the *library code* that loads and runs the model —
it's a Python dependency like any other. `revision=` pins the *weights
themselves* — which specific checkpoint `from_pretrained` downloads. You can
pin the library perfectly and still get different weights every time `main`
moves on the Hub, because those are two independent things that happen to be
fetched by the same function call.

</details>

## 📖 Go deeper

- [The Turing Way — Reproducible Research](https://book.the-turing-way.org/reproducible-research/reproducible-research)
- [PyTorch — reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- [DVC — data versioning](https://dvc.org/doc/use-cases/versioning-data-and-models)
