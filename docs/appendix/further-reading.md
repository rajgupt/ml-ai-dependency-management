# Further reading 🟢

Curated, not exhaustive. Everything here is worth your evening.

## Tooling

- [uv documentation](https://docs.astral.sh/uv/) — start with *Working on projects*
- [uv — Using uv with PyTorch](https://docs.astral.sh/uv/guides/integration/pytorch/) — the index and marker recipes from M6
- [Python Packaging User Guide](https://packaging.python.org/) — the canonical reference
- [Scientific Python Development Guide](https://learn.scientific-python.org/development/) — the single best reference for this audience
- [pixi](https://pixi.sh/) · [conda-lock](https://conda.github.io/conda-lock/) — when you need conda-forge system libraries

## Standards worth skimming

- [PEP 621](https://peps.python.org/pep-0621/) — project metadata in `pyproject.toml`
- [PEP 517](https://peps.python.org/pep-0517/) / [PEP 518](https://peps.python.org/pep-0518/) — build backends
- [PEP 508](https://peps.python.org/pep-0508/) — dependency specification and environment markers
- [PEP 735](https://peps.python.org/pep-0735/) — dependency groups
- [PEP 751](https://peps.python.org/pep-0751/) — `pylock.toml`, the standard lockfile format

## Arguments worth having

- Henry Schreiner — [*Should You Use Upper Bound Version Constraints?*](https://iscinumpy.dev/post/bound-version-constraints/)
- Brett Cannon — [*What the heck is pyproject.toml?*](https://snarky.ca/what-the-heck-is-pyproject-toml/)
- Joel Grus — [*I Don't Like Notebooks*](https://www.youtube.com/watch?v=7jiPeIFXb6U) — read M7 as the rebuttal

## ML-specific

- [The Turing Way — Reproducible Research](https://book.the-turing-way.org/reproducible-research/reproducible-research)
- [PyTorch — reproducibility notes](https://docs.pytorch.org/docs/stable/notes/randomness.html)
- [Hugging Face — pickle security and `safetensors`](https://huggingface.co/docs/hub/security-pickle)
- [DVC — versioning data and models](https://dvc.org/doc/use-cases/versioning-data-and-models)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/)
- [Docker — multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

## Security

- [pip-audit](https://github.com/pypa/pip-audit) · [OSV](https://osv.dev/) · [CycloneDX Python](https://github.com/CycloneDX/cyclonedx-python)
- [Renovate — PEP 621 manager](https://docs.renovatebot.com/modules/manager/pep621/)
