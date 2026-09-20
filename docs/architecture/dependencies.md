# Dependency and runtime verification

Verified 2026-09-20 against the official PyPI JSON metadata at
`https://pypi.org/pypi/<distribution>/json` before pinning. Each selected release
supports Python 3.12. The committed hash-checked locks are the installation
authority; PyPI is not queried to select versions during deployment.

| Purpose | Direct dependencies |
| --- | --- |
| Runtime | Typer 0.27.2 (the guide's pin); Phase 2A contracts use only the standard library |
| Build | pip 26.2.1, Hatchling 1.32.3, build 1.6.1 |
| Lock generation / editable development | pip-tools 7.6.1, editables 0.6 |
| Checks | Ruff 0.16.8, mypy 2.3.1, pytest 9.1.1, pytest-cov 7.1.0, import-linter 2.15 |
| Documentation | MkDocs 1.6.1, mkdocstrings 1.0.6, mkdocstrings-python 2.0.8, mkdocs-gen-files 0.6.1 |

[Typer's official release metadata](https://pypi.org/project/typer/0.27.2/)
confirms the specified version. Frameworks for future work (LangGraph, PyTorch,
Qwen, Whisper) are not dependencies of this foundation. Their guide pins
must be verified when their phases are authorized.

The guide's `nvidia/cuda:13.0.3-cudnn-runtime-ubuntu24.04` exists. Dockerfile pins its
[official linux/amd64 manifest](https://hub.docker.com/layers/nvidia/cuda/13.0.3-cudnn-runtime-ubuntu24.04/images/sha256-af851538a2bb05f587f27b660d61de3643d964e75ef5c04f4086ff2b36f2a12a)
to `sha256:af851538a2bb05f587f27b660d61de3643d964e75ef5c04f4086ff2b36f2a12a`.
Ubuntu Python packages receive repository security updates at build time; this is
not a claim of bit-for-bit image reproduction. The release check records the
resulting image ID. FFmpeg, model volumes, and model/persistence environment
variables are deferred with their consumers under the Phase 1 scope gate.

Compose's `gpus: all` requires
[Docker Compose 2.30.0 or newer](https://docs.docker.com/reference/compose-file/services/#gpus)
and a configured NVIDIA container runtime. Foundation checks use the same image
without GPU passthrough; they execute no inference or alternative backend.

The lock-generation procedure follows
[pip-tools' hash and layered-lock documentation](https://pip-tools.readthedocs.io/en/latest/).
Generate locks on Linux/amd64 with Python 3.12. Runtime, build and development
locks have separate purposes, and the development resolver is constrained by the
runtime and build locks. `make lock` preserves existing pins; intentional upgrades
require review of the input pins, resolved diff, and full release validation.
