# Glossary 🟢

<!-- WRITE: keep every entry to two sentences maximum. Terms used in this book only. -->

**Abstract dependency** — what your project *supports*, written as a range in `pyproject.toml`.

**Concrete dependency** — what a specific run *used*, written as an exact version + hash in a lockfile.

**Build backend** — the tool that turns your source tree into a wheel (`hatchling`, `setuptools`). Declared in `[build-system]`.

**CUDA driver / runtime / toolkit** — driver is on the host and not pip-installable; runtime ships inside wheels; toolkit (`nvcc`) is only needed to compile kernels.

**Dependency confusion** — an internal package name that also exists on a public index, causing the installer to fetch the wrong one.

**Dependency group (PEP 735)** — `[dependency-groups]`, for people working on the repo. Never shipped to users.

**Editable install** — the installed package points at your source tree, so edits take effect without reinstalling.

**Extra (PEP 621)** — `[project.optional-dependencies]`, an opt-in feature bundle that ships with your package: `pip install pkg[gpu]`.

**Environment marker (PEP 508)** — a condition on a dependency, e.g. `; sys_platform == "linux"`.

**Lockfile** — the exact, hashed, resolved set of packages for a project. `uv.lock` is universal (all platforms in one file).

**manylinux** — the wheel tag family that says which glibc a Linux wheel is compatible with.

**Resolution** — picking one version of every package such that all constraints hold. Fails on a genuine conflict; the error names the chain.

**Run manifest** — the record emitted with each training run: git SHA, lock hash, data version, image digest, seeds, metrics.

**safetensors** — a weights format that stores tensors only, with no code execution on load. The safe alternative to pickle-based checkpoints.

**sdist / wheel** — source distribution (needs building) vs pre-built distribution (just unpacks).

**src layout** — source under `src/pkg/` rather than `pkg/`, so tests can only import the *installed* package.

**Universal lock** — one lockfile resolved for every platform and Python version the project supports.

**Wheel tag** — the compatibility fields in a wheel filename: `cp312-cp312-manylinux_2_28_x86_64`.
