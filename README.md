# Simulated Singularity

A clean-slate, LangGraph-native artifact factory. This checkout implements the
Phase 0 + Phase 1 foundation only. See [the scope specification](docs/specifications/phase-0-1.md).

The canonical application runtime is Linux/amd64, Python 3.12, in the pinned NVIDIA
CUDA container. Linux development checks exercise the same Python code.

```sh
make bootstrap
make check
.venv/bin/ss --help
.venv/bin/ss doctor --json
```

Container and full release validation:

```sh
make container-check
make release-check
docker compose run --rm engine ss doctor --json
```

Doctor checks only Linux, x86-64, and Python 3.12. A successful result establishes
the Phase 1 Python foundation; it does not certify GPU readiness or inference.
Compose reserves NVIDIA GPUs for the canonical deployment; foundation smoke
checks need no GPU because there are no inference providers.

See [architecture](ARCHITECTURE.md), [contributing](CONTRIBUTING.md), and
[documentation](docs/index.md) for contracts and validation details.

The implemented application is a small diagnostics slice: a typed application
contract, a standard-library runtime adapter, explicit composition, and a Typer
client. Module manifests describe ownership and allowed dependencies beside the
code. Import-linter enforces the dependency direction.

This milestone contains no speech production, models, artifact storage, graphs,
or persistent state. LangGraph remains the specified future execution kernel;
the dependency is introduced when execution is implemented.

The next milestone is **Phase 2: implement the immutable artifact foundation**.
It requires review of Phase 1 and explicit authorization before implementation.
