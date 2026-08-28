# M7 · Reproducibility beyond pip 🟢

> ⏱ 15 minutes · Route: Full, Notebook-first

## 3 a.m. story

*A reviewer asks you to reproduce the AUC from a model you trained in March.
The lockfile restores perfectly. The number comes back 0.834 instead of 0.841.
Nothing in the dependency tree changed — but the model card you fine-tuned from
now points at a different commit on the Hub, and the training table gained
40,000 rows.*

## What's actually going on

### The reproducibility ladder

<!-- WRITE: be honest here — over-promising is how courses lose trust.

     Rung 1  same lock              → same environment.                        Guaranteed.
     Rung 2  same env + same code   → same code path.                          Guaranteed.
     Rung 3  + same data version    → same inputs.                             Your job, not pip's.
     Rung 4  + same seeds           → same result on CPU.                      Usually.
     Rung 5  + same GPU/driver/flags→ same result on GPU.                      Only with effort.

     Rung 5 caveats, briefly: cuDNN autotuning picks different kernels per run,
     float atomics reorder, TF32 on Ampere+ changes matmul precision, thread counts
     change reduction order. Mention torch.use_deterministic_algorithms(True) and
     what it costs (speed, and some ops just raise).
     The honest takeaway: aim for rungs 1–4 always; buy rung 5 only when you need it. -->

### Models and data are dependencies too

<!-- WRITE: the concept most dependency courses miss entirely.
     - A Hugging Face model id without a revision is `latest`. Pin the commit SHA:
       `from_pretrained("org/model", revision="<40-char sha>")`. `main` moves.
     - Datasets: DVC / lakeFS / an object-store path that contains a content hash.
       Whatever you choose, the version must be recorded, not remembered.
     - A model in a registry has a version. Log it next to the lock hash. -->

## 🍳 Recipe 1 — the run manifest

<!-- WRITE: the single highest-value habit in this module. Every training run emits:
       git SHA (+ dirty flag), uv.lock hash, python version, data version/hash,
       container image digest, seeds, GPU model + driver, key package versions,
       and the resulting metrics.
     Show a ~20-line Python snippet writing manifest.json next to the model artifact.
     Line to land: six months from now, this file is the difference between
     "reproduce it" and "retrain it and hope". -->

## 🍳 Recipe 2 — notebook hygiene

<!-- WRITE:
     - The kernel is not the project env. Register it: `uv run ipython kernel install --user --name=<proj>`
       (or run jupyter itself via `uv run`). This one fix removes most "but it worked in the notebook".
     - No `!pip install` in cells. If you need a package, `uv add` it; the notebook is not a package manager.
     - nbstripout in pre-commit → outputs out of git, diffs become reviewable, no leaked data in outputs.
     - jupytext for a .py mirror your reviewers can actually read.
     - papermill when a notebook must run on a schedule with parameters.
     Framing: notebooks aren't the problem, *hidden state and hidden installs* are. -->

## ⚠️ Sharp edges

<!-- WRITE:
     - `random.seed()` is not `np.random.seed()` is not `torch.manual_seed()`. Set all of them,
       plus PYTHONHASHSEED, plus the dataloader worker seed.
     - Out-of-order execution makes a notebook's result depend on your clicking history.
       "Restart & Run All" before you believe any number.
     - Pinning a HF revision pins the weights, not the tokenizer config in a separate repo. -->

## ✅ Check yourself

<!-- WRITE: Q1: Your lock restores exactly and metrics still moved. Name two causes outside the lock.
           Q2: What does pinning `revision=` buy you that pinning `transformers==` does not? -->

## 📖 Go deeper

- [The Turing Way — Reproducible Research](https://book.the-turing-way.org/reproducible-research/reproducible-research)
- [PyTorch — reproducibility](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- [DVC — data versioning](https://dvc.org/doc/use-cases/versioning-data-and-models)
