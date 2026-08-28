# M6 · GPUs, CUDA & non-Python dependencies 🔵🔴

> ⏱ 25 minutes · Route: Full, Fast
>
> This is the module that makes this an *ML* course. Layers 1 and 2 of the stack.

## 3 a.m. story

*Same lockfile. Your MacBook installs a 250 MB CPU build of torch and trains
happily. The A100 box installs the same version and every `.cuda()` call throws.
The lockfile is not lying — `torch` on PyPI is not one package.*

## What's actually going on

### Driver vs runtime vs toolkit

<!-- WRITE: ~180 words + a small diagram.
     - GPU driver: on the host, installed by ops, NOT pip-installable. `nvidia-smi` shows it.
     - CUDA runtime: ships inside the torch wheel (or the base image). Pip-installable.
     - CUDA toolkit (nvcc): only needed to COMPILE custom kernels.
     Key rule to state loudly: the driver must be >= what the wheel's CUDA runtime needs.
     That's the constraint no lockfile can express, and the reason the story above happens.
     Explain what `nvidia-smi`'s "CUDA Version" actually means (max supported by the driver,
     not what's installed) — this single misreading causes a lot of wasted hours. -->

### Wheel tags and environment markers

<!-- WRITE: decode `torch-2.6.0-cp312-cp312-manylinux_2_28_x86_64.whl` field by field.
     Then PEP 508 markers as the tool for "different platforms, different dependency":
       sys_platform, platform_machine, python_version.
     Table: mac arm64 / linux x86_64 / linux aarch64 → what resolves.
     This is the "installs on my Mac, fails on the cluster" explanation in one page. -->

## 🍳 Recipe 1 — pin a torch variant explicitly

<!-- WRITE: the [[tool.uv.index]] + [tool.uv.sources] pattern.

     [[tool.uv.index]]
     name = "pytorch-cu128"
     url = "https://download.pytorch.org/whl/cu128"
     explicit = true          # ← only packages that ask for it use this index

     [tool.uv.sources]
     torch = { index = "pytorch-cu128" }

     Explain why `explicit = true` matters: without it the index is in scope for EVERY
     package, which is a dependency-confusion risk and a resolution slowdown.
     Backends available: cpu, cu118, cu126, cu128, cu130, rocm6.4, xpu. -->

## 🍳 Recipe 2 — one lockfile, CPU laptops and GPU cluster

<!-- WRITE: the marker split — the recipe people actually come here for.
     torch from the cpu index when sys_platform == "darwin", from cu128 on linux x86_64.
     Show the full pyproject block and then `uv lock` + `uv sync` on both machines.
     Emphasise: ONE lockfile, resolved for all platforms. That's what "universal lock" buys you. -->

## ⚠️ Sharp edge — `--torch-backend=auto`

<!-- WRITE: uv can detect the installed driver and pick the index automatically:
       uv pip install torch --torch-backend=auto
     But it works with `uv pip install/compile/sync`, `uv tool run/install` — NOT with
     `uv add`, `uv lock`, `uv sync`. So it's great for a throwaway box or a Dockerfile
     RUN line, and NOT a substitute for the marker split in a locked project.
     Get this wrong and you'll think the project config is broken. -->

## 🍳 Recipe 3 — non-Python dependencies: the decision tree

<!-- WRITE: ffmpeg, libGL, tesseract, NCCL, MKL, system fonts, GDAL.
     A decision tree, one page, no religion:

       Is there a manylinux wheel that vendors it?          → just use pip/uv. Done.
       Do you control the machine (or the image)?           → system package (apt/brew) + document it.
       Do you need a non-Python solver stack, cross-platform, without root?
                                                            → pixi / conda-forge (+ conda-lock)
       Is it a deploy target?                               → container. Always container.

     State the mixing rule: if you use conda, install as much as possible from conda,
     and pip only at the very end, and lock both. Half-conda-half-pip environments
     are the single most common irreproducible ML env. -->

## 🍳 Recipe 4 — the Dockerfile 🔵🔴

<!-- WRITE: annotated multi-stage build.
     - Base image pinned BY DIGEST, not tag.
     - Dependency layer built with `uv sync --frozen --no-install-project --no-dev`
       BEFORE copying source → source edits don't bust the dependency cache. Explain the
       layer-cache reasoning; this is the trick that takes CI builds from 6 min to 40 s.
     - Then copy src, `uv sync --frozen --no-dev`.
     - Runtime stage: copy the venv, no build tools, no jupyter.
     - Train vs serve images: different extras, different base, different size. Show both
       numbers — the size difference is the argument.
     - ENTRYPOINT uses the console script from M4. -->

## ✅ Check yourself

<!-- WRITE: Q1: `nvidia-smi` says CUDA 12.4. Can you install a cu128 torch wheel? What actually decides?
           Q2: Why won't `--torch-backend=auto` help inside `uv sync`? -->

## 📖 Go deeper

- [uv — Using uv with PyTorch](https://docs.astral.sh/uv/guides/integration/pytorch/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/)
- [Docker — multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
