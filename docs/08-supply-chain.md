# M8 · Supply chain & upgrade hygiene 🟢🔵🔴

> ⏱ 12 minutes · Route: Full

## 3 a.m. story

*A teammate downloads a fine-tuned checkpoint from a model hub and calls
`torch.load(path)`. There is no error and no model. There is a reverse shell.
The `.pt` file was a pickle, and a pickle is a program.*

## What's actually going on

### ML's extra attack surface

<!-- WRITE: ~200 words. Ordinary Python supply chain risk PLUS two things specific to ML:

     1. Model weights are executable. `pickle` (and therefore the default `torch.load`,
        and `.pt`/`.pth`/`.bin` checkpoints, and joblib artifacts) deserializes by
        CONSTRUCTING objects — arbitrary imports and calls. A downloaded checkpoint is
        untrusted code, not data. Treat it like a dependency, because it is one.
        Fixes: prefer `safetensors`; `torch.load(..., weights_only=True)`; scan before load;
        only load from registries you control.
     2. ML repos install a LOT, fast, often from copy-pasted commands — which is exactly
        the condition typosquatting exploits.

     Then the ordinary risks that hit ML teams hardest:
     typosquatting; dependency confusion (an internal package name that also exists on
     public PyPI, and the installer picks the higher version); post-install scripts in sdists. -->

## 🍳 Recipe 1 — audit what you already have

<!-- WRITE:
       uvx pip-audit -r <(uv export --no-hashes)     # or pip-audit against the env
       uv pip list --outdated
     How to triage a CVE that's in a transitive dep you don't call. Not every finding is
     an action — but every finding needs a decision, recorded. -->

## 🍳 Recipe 2 — SBOM for the model service 🔴

<!-- WRITE: what an SBOM is in two sentences and who asks for it (security review, customers,
     regulated deployments). Generate CycloneDX from the lock, attach it to the release
     and to the container image. Keep it short and practical. -->

## 🍳 Recipe 3 — private indexes without dependency confusion 🔴

<!-- WRITE: the failure mode first: internal package `feature-store` also exists on public PyPI
     at a higher version → the installer takes the public one. That's dependency confusion.
     Fixes: `explicit = true` index pinning per-package (same mechanism as M6's torch index),
     `--index-strategy` behaviour, namespacing internal packages (`acme-feature-store`),
     and claiming your names on public PyPI. -->

## 🍳 Recipe 4 — the upgrade ritual

<!-- WRITE: the habit that keeps a project alive. Monthly, or on a bot PR:

       1. Renovate/Dependabot opens the PR (schedule it; grouped, not one PR per package).
       2. `uv lock --upgrade-package scikit-learn` for a targeted bump;
          `uv lock --upgrade` for the full sweep.
       3. **Read the lock diff like code.** It is the most under-reviewed file in ML repos.
          What to look for: a new transitive package you've never heard of, a major bump
          hidden behind a minor one, a source that changed index.
       4. Tests pass ≠ safe (M1: SemVer doesn't cover numerics). Run the eval set and
          compare metrics against the recorded baseline before merging.
       5. Merge, tag, and let the run manifest record the new lock hash.

     Pinning policy, honestly: upper bounds protect you and hurt everyone downstream.
     Recommend: applications yes (you deploy from a lock anyway), libraries no —
     link both sides of the argument and let the reader choose. -->

## ⚠️ Sharp edges

<!-- WRITE:
     - `weights_only=True` is a mitigation, not a sandbox.
     - `uv lock --upgrade` on a Friday. Don't.
     - Auto-merging bot PRs on an ML repo without an eval gate is how metrics drift silently. -->

## ✅ Check yourself

<!-- WRITE: Q1: Why is a `.pt` checkpoint from a public hub a dependency and not an input?
           Q2: Your bot bumps `transformers` 4.51→4.52. Tests pass. What else runs before merge? -->

## 📖 Go deeper

- [Hugging Face — pickle security and `safetensors`](https://huggingface.co/docs/hub/security-pickle)
- [pip-audit](https://github.com/pypa/pip-audit) and [OSV](https://osv.dev/)
- [Renovate — Python support](https://docs.renovatebot.com/modules/manager/pep621/)
