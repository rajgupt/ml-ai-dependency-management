# M6 · GPUs, CUDA & non-Python dependencies 🔵🔴

> ⏱ 25 minutes · **Optional deep-dive** — not on the core path
>
> This is the module that makes this an *ML* course. Layers 1 and 2 of the stack.
> Read it when you actually hit a GPU, CUDA, or system-library problem; the core
> path (M0–M4, Labs 1–2) does not depend on it.
>
> 🪟 **Windows:** the `uv` config here works natively — with one marker
> difference (Windows is `win32` / `AMD64`, called out below).

## 3 a.m. story

*Same lockfile. Your MacBook installs a 250 MB CPU build of torch and trains
happily. The A100 box installs the same version and every `.cuda()` call throws.
The lockfile is not lying — `torch` on PyPI is not one package.*

## What's actually going on

### Driver vs runtime vs toolkit

Three different things share the name "CUDA," and confusing them is where
the 3 a.m. story starts.

```
Layer 1  GPU driver     ← on the host, installed by ops/IT, NOT pip-installable
Layer 2  CUDA runtime   ← ships INSIDE the torch wheel (or the base image)
(dev)    CUDA toolkit   ← nvcc + headers, only needed to COMPILE custom kernels
```

- **Driver.** Lives on the machine, talks to the physical GPU, installed once
  by whoever owns the box (or baked into the cloud image). `uv` cannot
  install it, `pip` cannot install it, and no `pyproject.toml` can pin it —
  it's below the layer any Python tool controls.
- **CUDA runtime.** The shared libraries (`libcudart`, `libcublas`, `libcudnn`,
  …) that a GPU-enabled `torch` wheel actually calls at runtime. A
  `torch==2.6.0+cu128` wheel *contains its own copy* of this — that's most of
  why the wheel is 2+ GB. This part is pip-installable, and it's what `uv
  add torch` actually pulls in.
- **CUDA toolkit.** `nvcc`, headers, profilers — only needed if you're
  compiling a custom CUDA kernel or building a package like `flash-attn` from
  source. Most ML engineers never install this directly.

The rule that matters: **the driver's supported CUDA version must be ≥ the
CUDA version the wheel's runtime was built against.** A lockfile can pin the
torch wheel exactly and still be useless on a machine whose driver is too old
— that constraint lives in layer 1, which no `uv.lock` line can express. This
is exactly the 3 a.m. story: same lockfile, same wheel, one machine's driver
is new enough and one isn't.

`nvidia-smi` is the tool for reading layer 1 — but read it carefully. The
"CUDA Version" in its top-right corner is the *newest* CUDA runtime that
driver can support, not a runtime that's actually installed. Seeing
"CUDA Version: 12.4" doesn't mean nothing higher is on the box, and it
doesn't mean a `cu124`-tagged wheel is what's running — it's a ceiling, not a
version report. Reading it as "what's installed" is the single most common
misreading in this whole area, and it costs people hours chasing a mismatch
that was never there.

### Wheel tags and environment markers

A wheel filename is a compatibility contract. Take
`torch-2.6.0-cp312-cp312-manylinux_2_28_x86_64.whl` apart:

| Field | Value | Means |
|---|---|---|
| distribution-version | `torch-2.6.0` | package and version |
| Python tag | `cp312` | built for CPython 3.12 |
| ABI tag | `cp312` | binary-compatible with CPython 3.12's C ABI |
| platform tag | `manylinux_2_28_x86_64` | a Linux glibc ≥ 2.28, x86-64 |

Change any field and it's a different wheel, built separately: `cp311` for
Python 3.11, `macosx_11_0_arm64` for Apple Silicon, `manylinux…aarch64` for
Graviton or Jetson. That's why "installs on my Mac, fails on the cluster" is
so common — the resolver isn't choosing wrong, it's correctly picking the
one wheel that matches *your* machine, and your machine and the cluster are
different tags.

[PEP 508](https://peps.python.org/pep-0508/) markers are how you tell a
resolver "different platform, different dependency" *inside one
`pyproject.toml`*, instead of maintaining separate requirement files per
platform:

| Marker | Answers | Typical use in ML |
|---|---|---|
| `sys_platform` | `"linux"`, `"darwin"`, `"win32"` | route macOS to a CPU wheel, Linux to a CUDA one |
| `platform_machine` | `"x86_64"`, `"arm64"`, `"aarch64"`, `"AMD64"` | tell a cluster x86 box apart from a Jetson or Apple Silicon laptop |
| `python_version` | `"3.11"`, `"3.12"`, … | drop a dependency that doesn't yet support your interpreter |

| Machine | `sys_platform` | `platform_machine` | typically resolves to |
|---|---|---|---|
| MacBook (Apple Silicon) | `darwin` | `arm64` | CPU-only torch wheel |
| Training cluster node | `linux` | `x86_64` | `cu128` (or whichever CUDA build) torch wheel |
| ARM inference box / Jetson | `linux` | `aarch64` | a Linux ARM wheel, if one is published — often not for GPU builds |
| Windows workstation | `win32` | `AMD64` | a Windows CUDA wheel (`cu121`/`cu128`) or the CPU build |

One `pyproject.toml`, one `uv.lock`, and every platform in that table
resolves to the wheel that actually fits it. Recipe 2 below is exactly this
table turned into config.

> 🪟 **Windows markers gotcha.** 64-bit Windows reports `sys_platform == "win32"`
> (yes, even on 64-bit) and `platform_machine == "AMD64"` (not `"x86_64"`). A
> marker written for Linux won't match a Windows box — spell out the Windows
> case explicitly, as Recipe 2 does below.

## 🍳 Recipe 1 — pin a torch variant explicitly

PyPI's default `torch` wheel is a lowest-common-denominator CPU build. To get
a CUDA build, point `uv` at PyTorch's own index, and pin `torch` to it:

```toml
[[tool.uv.index]]
name = "pytorch-cu128"
url = "https://download.pytorch.org/whl/cu128"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cu128" }
```

`explicit = true` is not decoration. Without it, this index is in scope for
*every* package in the resolution, not just `torch` — which is both a
resolution slowdown (uv now checks a second index for every dependency) and a
dependency-confusion risk (a same-named package could resolve from an index
you didn't intend for it). `explicit = true` restricts the index to packages
that name it in `[tool.uv.sources]` — here, only `torch`.

PyTorch publishes a matching index per backend: `cpu`, `cu118`, `cu126`,
`cu128`, `cu130`, `rocm6.4`, `xpu`. Swap the `url` to change which build your
project locks to.

## 🍳 Recipe 2 — one lockfile, CPU laptops and GPU cluster

The recipe people actually come here for: laptops get a small CPU wheel,
the cluster gets the CUDA build, and it's all one `pyproject.toml` and one
`uv.lock`.

```toml
[project]
dependencies = ["torch>=2.6"]

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
    { index = "pytorch-cpu", marker = "sys_platform == 'darwin'" },
    { index = "pytorch-cu128", marker = "sys_platform == 'linux' and platform_machine == 'x86_64'" },
    { index = "pytorch-cu128", marker = "sys_platform == 'win32'" },
]
```

The third line is the Windows case: a native-Windows workstation with an NVIDIA
GPU pulls the same `cu128` build from PyTorch's Windows index. Drop that line if
your Windows users are CPU-only — they'll fall through to the default CPU wheel.

```bash
uv lock
```

Run that once and `uv.lock` records *all* the resolutions — the CPU wheel for
`darwin`, the `cu128` wheel for `linux`/`x86_64`, and the Windows `cu128` wheel —
in the same file. Then:

```bash
# on a MacBook
uv sync        # installs the CPU wheel, ~200 MB

# on the training cluster
uv sync        # installs the cu128 wheel, same lockfile, no re-resolution
```

That's what "universal lock" buys you: `uv.lock` isn't resolved for *your*
machine, it's resolved for every platform your markers cover, up front. A
teammate on either side of that split runs the same `uv sync` and gets the
right torch, with nobody hand-editing a requirements file per machine.

## ⚠️ Sharp edge — `--torch-backend=auto`

`uv` can also detect the installed driver and pick a matching backend for
you, live:

```bash
uv pip install torch --torch-backend=auto
```

This is genuinely useful — but only inside `uv pip install`, `uv pip
compile`, `uv pip sync`, and `uv tool run`/`uv tool install`. It does **not**
work with `uv add`, `uv lock`, or `uv sync`. Those commands resolve a
*project*, meant to be reproduced on other machines by other people; "detect
what's on this machine" is the opposite of that guarantee, so uv doesn't
apply it there.

Use `--torch-backend=auto` on a throwaway box, in a one-off Dockerfile `RUN`
line, or when you're not tracking a `pyproject.toml` at all. Inside a locked
project, use the marker split from Recipe 2 instead. Reach for `auto` inside
`uv add`/`uv sync` and nothing happens the way you expect — it's silently
ignored there, not an error — and it looks exactly like a broken project
config until you know this distinction.

## 🍳 Recipe 3 — non-Python dependencies: the decision tree

`ffmpeg`, `libGL`, `tesseract`, NCCL, MKL, system fonts, GDAL — none of these
are Python packages, so none of them belong in `pyproject.toml`. Work through
these questions in order:

1. **Does a wheel already vendor it?** Many packages ship the C library
   inside the wheel so you never see the gap — `opencv-python-headless`
   bundles its own `libopencv`; some `tesseract`/`pdf` bindings do too. Check
   first (`pip show`, or just try the import) before assuming you need a
   system install at all.
2. **Do you control the machine or the image?** If yes — your laptop, your
   base Docker image — install it as a system package (`apt install ffmpeg
   libgl1`, `brew install tesseract`) and write down the command in a
   Dockerfile or setup script. Simple, and it's how most teams should default.
3. **Do you need a solver-managed, cross-platform stack without root** —
   CUDA/NCCL/MKL/BLAS versions that have to match each other exactly, on
   machines you don't administer? Reach for **pixi** or **conda-forge**
   (locked with **conda-lock**). This is the one case plain `apt`/`brew`
   genuinely doesn't cover: a non-Python dependency solver.
4. **Is this a deploy target, not a dev machine?** Container. Always
   container — see Recipe 4. Don't try to make a serving host's system
   packages match a laptop's by hand; bake the image instead.

**The mixing rule, stated once:** if you're using conda/pixi at all, install
*as much as possible* from it — Python included — and use `pip`/`uv pip`
only for the last few packages conda-forge doesn't carry, then lock both
layers. A half-conda-half-pip environment where both tools think they own
the same packages is the single most common irreproducible ML environment
there is. If you're not already committed to conda for a real reason (step 3
above), skip it — plain `uv` plus system packages is simpler and reproduces
better.

## 🍳 Recipe 4 — the deploy image 🔵🔴

When Recipe 3 sends you to "bake an image," three things carry over from
everything else in this book. (The mechanics of *how* you build the image —
Dockerfile, or whatever your platform uses — are out of scope here; these are
the dependency-management decisions inside it.)

**Pin the base image by digest, not by tag.** A tag like `python:3.12-slim`
is a moving target — the same tag points at a different image next week when a
base-OS patch lands. A digest (`python:3.12-slim@sha256:...`) is immutable:
that digest is that exact image, forever. Resolve it once and commit it like
you'd commit a lockfile — because it is one, for layer 1 of the stack.

**Install dependencies from the lockfile, before the project source.**
Copy `pyproject.toml` and `uv.lock` and run `uv sync --frozen
--no-install-project` first — that installs every dependency but skips the
project itself. Then add `src/` and run `uv sync --frozen` to install the
project. Every image build system caches by input, so keeping the dependency
step separate from and ahead of the source means a code edit doesn't reinstall
torch. `--frozen` means install exactly what's in `uv.lock`, no re-resolution;
`--no-dev` drops the `dev` group (pytest, ruff — see [M4](04-packaging.md)
and [M2](02-uv.md)) so it never reaches the image at all.

**Train and serve are different images, not one image with more in it.**
A serving image doesn't need the compiler, `uv`, Jupyter, or the
`dev`/`notebook` groups — and it can skip the `[gpu]`/training-only extras
too, calling a `serve` console script instead of `churn-train`. The
difference shows up on disk: a training image carrying CUDA wheels and dev
tooling commonly runs 6–8 GB; a slim CPU inference image built the same way
can sit under 500 MB. Every package in that gap is attack surface and
pull-time you pay for on every replica, for no reason a serving request ever
uses.

Use a console script (`churn-train`, from [M4 Recipe 4](04-packaging.md)) as
the image's entrypoint, not `python src/cli.py`: it exists because the package
is installed, it's versioned with the image, and it doesn't care what working
directory the runtime left you in.

## ✅ Check yourself

<details>
<summary><code>nvidia-smi</code> reports "CUDA Version: 12.4". Can you install a <code>cu128</code>-tagged torch wheel? What actually decides?</summary>

Probably not directly relevant to whether it's *allowed* — but the number
you read is a ceiling, not an installed version: it's the newest CUDA
runtime that driver supports, not what's currently on the box. What decides
whether a `cu128` wheel will actually run is whether the driver supports CUDA
≥ 12.8. A driver reporting 12.4 as its max does not support a wheel built
against 12.8's runtime — you'd need to upgrade the driver first, or install a
`cu124`-or-lower build instead. `nvidia-smi`'s number tells you the upper
bound to pin against, not a version already sitting on the machine.
</details>

<details>
<summary>Why won't <code>--torch-backend=auto</code> help inside <code>uv sync</code>?</summary>

Because `--torch-backend=auto` is a flag on uv's pip-compatible commands
(`uv pip install/compile/sync`) and on `uv tool run`/`install` — it detects
the driver on *this* machine and picks a matching index live. `uv add`,
`uv lock`, and `uv sync` resolve and reproduce a *project*, meant to install
identically on every machine that runs it, so uv doesn't substitute
"whatever this machine happens to have" into that resolution. Getting a
CPU/GPU split inside a locked project means declaring it explicitly with the
`[tool.uv.sources]` marker split from Recipe 2, not this flag.
</details>

## 📖 Go deeper

- [uv — Using uv with PyTorch](https://docs.astral.sh/uv/guides/integration/pytorch/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/)
- [Docker — multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
