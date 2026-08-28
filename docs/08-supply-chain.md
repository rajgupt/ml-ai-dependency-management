# M8 · Supply chain & upgrade hygiene 🟢🔵🔴

> ⏱ 12 minutes · Route: Full

## 3 a.m. story

*A teammate downloads a fine-tuned checkpoint from a model hub and calls
`torch.load(path)`. There is no error and no model. There is a reverse shell.
The `.pt` file was a pickle, and a pickle is a program.*

## What's actually going on

### ML's extra attack surface

Everything a normal Python project worries about — malicious packages, typosquats,
compromised maintainer accounts — applies here too. ML adds two more, and the
first one is worse than anything in ordinary application supply chain risk.

**Model weights are executable.** `pickle` doesn't deserialize data, it
*replays a program* — a sequence of instructions to import modules and
construct arbitrary objects. `torch.load()` uses `pickle` by default, which
means every `.pt`, `.pth`, and `.bin` checkpoint (and every `joblib` artifact)
can run arbitrary code the moment you load it. There is no error message
warning you, because from `pickle`'s point of view this is working as
designed. A model file you downloaded from a hub is not data — it's a
program you're about to execute, and you should trust it exactly as much as
you'd trust `curl | sh` from that same source. The fixes:

- Prefer formats that store tensors without executing anything —
  [`safetensors`](https://huggingface.co/docs/safetensors/index) reads
  weights as flat arrays, with no `__reduce__`, no arbitrary imports.
- If you must load a `.pt`, load it with `weights_only=True`:
  ```python
  import torch

  state_dict = torch.load("checkpoint.pt", weights_only=True)
  ```
  This restricts deserialization to tensors and a small allowlist of plain
  types instead of arbitrary objects.
- Scan untrusted checkpoints before loading them (the Hub itself runs a
  pickle scanner and flags files it can't clear).
- Only auto-load from registries you control or that you've decided to
  trust; treat a checkpoint from a random hub link the way you'd treat a
  random `pip install` from a URL nobody reviewed.

**The ordinary risks, amplified.** ML projects install unusually large
dependency trees, fast, often from a command copy-pasted out of a paper's
README or a Colab notebook rather than typed carefully — which is exactly
the condition typosquatting is built to exploit (`torch` vs `torchh`,
`opencv-python` vs `opencv-python-headless`-adjacent lookalikes). Dependency
confusion — an internal package name that also happens to exist on public
PyPI — hits ML teams particularly hard because internal `feature-store`,
`model-utils`, and similar generic names are common and rarely namespaced.
Both are covered in the recipes below.

## 🍳 Recipe 1 — audit what you already have

```bash
# Audit the resolved lock — no install, works straight from uv.lock
uvx pip-audit -r <(uv export --no-hashes)

# Or audit the live project environment directly
uvx pip-audit --path .venv

# What's simply behind, security issue or not
uv pip list --outdated
```

```powershell
# 🪟 PowerShell — no process substitution; write the export to a temp file
uv export --no-hashes -o $env:TEMP\req.txt
uvx pip-audit -r $env:TEMP\req.txt

uvx pip-audit --path .venv
uv pip list --outdated
```

`pip-audit` checks resolved versions against the
[OSV](https://osv.dev/) database and flags known CVEs, including ones in
transitive dependencies you never import directly. Not every finding is
worth acting on immediately — a CVE in a code path you don't call, in a
package with no fix yet, is a real but low-priority risk — but every finding
needs a *recorded* decision (fixed now, tracked for the next release, or
explicitly accepted and why), not silence. An audit nobody reads is a
compliance checkbox, not a control.

## 🍳 Recipe 2 — SBOM for the model service 🔴

A Software Bill of Materials is a machine-readable list of exactly what's in
your build — every package, version, and where it came from. Security
review, enterprise customers, and regulated deployments increasingly ask for
one before they'll approve a model service in production, the same way
they'd ask for a list of ingredients.

```bash
uv add --group dev cyclonedx-bom
uv run cyclonedx-py environment -o sbom.json
```

Generate it from the same environment your lock built (`uv sync --frozen`
first, so the SBOM matches what actually ships), attach it to the release
artifact and to the container image build, and regenerate it every time the
lock changes. Nobody reads an SBOM for pleasure; keep the pipeline that
produces it boring and automatic so it's always current when someone asks.

## 🍳 Recipe 3 — private indexes without dependency confusion 🔴

The failure mode: your org has an internal package called `feature-store`.
Someone (attacker or accident) publishes a package named `feature-store` to
public PyPI with a higher version number. An installer resolving by "highest
version wins" across both indexes takes the public one — now everyone
running `uv sync` on your internal service is running someone else's code.
That's dependency confusion, and it doesn't require anyone to make a
mistake beyond trusting the default resolution order.

Fixes, layered:

- **Explicit index pinning**, the same mechanism [M6](06-gpu-and-system-deps.md)
  used for the torch CUDA index — bind the internal package to your private
  index by name, so nothing else can supply it:

  ```toml
  [[tool.uv.index]]
  name = "internal"
  url = "https://pypi.internal.example.com/simple"
  explicit = true

  [tool.uv.sources]
  feature-store = { index = "internal" }
  ```

  `explicit = true` means the internal index is only consulted for packages
  that name it in `[tool.uv.sources]` — it's never in scope as a fallback
  for anything else, which is what closes the confusion window.

- **`--index-strategy`** controls how uv searches multiple indexes when a
  package *isn't* pinned to one explicitly. The default,
  `first-index`, stops at the first index that has the package at all —
  safer than blending. Avoid `unsafe-best-match` (searches every index and
  picks the best version across all of them) for any project that also
  talks to a private index; it's the setting that reintroduces the exact
  "highest version wins across indexes" hole above.
- **Namespace internal packages** — `acme-feature-store`, not
  `feature-store`. A name nobody else would plausibly publish removes the
  collision entirely, cheaper than any resolver configuration.
- **Claim your names on public PyPI** even for packages you never intend to
  publish publicly. An empty placeholder release blocks a squatter from
  taking the name later.

## 🍳 Recipe 4 — the upgrade ritual

An unmaintained lockfile doesn't stay safe — it stays *unaudited*. This is
the habit that keeps a project alive, run monthly or on every bot PR:

1. **Renovate or Dependabot opens the PR** on a schedule, grouped by
   ecosystem or by risk level rather than one PR per package — a wall of 40
   single-package PRs gets rubber-stamped or ignored, neither of which is
   review.
2. **Resolve it locally to see the real diff:**
   ```bash
   uv lock --upgrade-package scikit-learn   # one targeted bump
   uv lock --upgrade                        # the full sweep, less often
   ```
3. **Read the lock diff like code.** `uv.lock` is the most under-reviewed
   file in most ML repos, and it's the one that actually determines what
   ships. Look for:
   - a new transitive package you don't recognize — why did it show up?
   - a major version bump riding along behind a minor one you asked for
   - a package's source or index changing, not just its version
4. **Tests pass is not the bar.** [M1](01-why-it-breaks.md) already made
   this point: SemVer covers the API, not the numbers a model produces. Run
   your eval set and compare against the recorded baseline before merging —
   a `transformers` patch bump that changes tokenization defaults will pass
   every unit test and still move your metrics.
5. **Merge, tag, and let the run manifest** (M7, Recipe 1) **record the new
   lock hash** on the next training run, so the next person who asks "which
   lock produced this model" has an answer.

**Pinning policy, honestly.** Upper bounds (`transformers<5`) protect *you*
— they stop a breaking major version from landing in your environment
unannounced. They also hurt everyone downstream who depends on your
package, because an unnecessarily tight upper bound is frequently the actual
cause of a diamond-dependency deadlock two layers up ([M1](01-why-it-breaks.md)).
Henry Schreiner's [*Should You Use Upper Bound Version
Constraints?*](https://iscinumpy.dev/post/bound-version-constraints/) makes
the case against them thoroughly; the honest middle ground most teams land
on: **applications pin hard** (you deploy from a lock anyway, so an upper
bound in `pyproject.toml` buys you little the lock doesn't already give you,
while costing nothing) — **libraries stay permissive** and rely on a test
matrix instead, because a library's upper bound becomes every one of its
users' problem the day it's technically wrong.

## ⚠️ Sharp edges

- `weights_only=True` is a mitigation, not a sandbox — it narrows what
  `torch.load` can construct, it doesn't guarantee the file is safe. Prefer
  `safetensors` when you have the choice.
- `uv lock --upgrade` on a Friday afternoon is how you spend Monday morning
  bisecting a metric regression instead of doing anything else. Run the
  sweep when you have time to read the diff and re-run the eval set.
- Auto-merging bot PRs on an ML repo without an eval gate is how metrics
  drift silently — the PR is green, the tests pass, and three sprints later
  nobody can say which of nine merged bumps moved the number.

## ✅ Check yourself

<details>
<summary>Answer</summary>

**Q1: Why is a `.pt` checkpoint from a public hub a dependency and not an
input?**

Because loading it (`torch.load` with default settings) executes code via
`pickle`'s deserialization mechanism, not just data structures — the same
way installing a package runs its setup code. An "input" like a CSV can only
be misread; an executable checkpoint can run anything the file's author
chose to put in it, on your machine, with your credentials. That's the
definition of a dependency, not a data file.

**Q2: Your bot bumps `transformers` 4.51→4.52. Tests pass. What else runs
before merge?**

The eval set, with metrics compared against the recorded baseline — not just
the unit test suite. A minor bump to an ML library can change tokenization,
default generation parameters, or numerical behavior without breaking any
API contract, which is exactly the gap SemVer doesn't cover ([M1](01-why-it-breaks.md)).
Read the lock diff too, for any transitive package that moved alongside it.

</details>

## 📖 Go deeper

- [Hugging Face — pickle security and `safetensors`](https://huggingface.co/docs/hub/security-pickle)
- [pip-audit](https://github.com/pypa/pip-audit) and [OSV](https://osv.dev/)
- [Renovate — Python support](https://docs.renovatebot.com/modules/manager/pep621/)
