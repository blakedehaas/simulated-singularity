# Simulated Singularity

A clean-slate, LangGraph-native artifact factory. This checkout implements the
reviewed Phase 1 foundation and Phase 2A immutable artifact contracts. See the
[Phase 2 scope specification](docs/specifications/phase-2.md).

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

The implemented application includes the Phase 1 diagnostics slice plus nominal
artifact identifiers, immutable artifact and provenance models, SHA-256
content-addressing primitives, and the provider-neutral `ArtifactRepository`
port. Module manifests describe ownership and allowed dependencies beside the
code. Import-linter enforces the dependency direction.

This milestone contains no speech production, models, filesystem artifact
storage, SQLite metadata, graphs, or persistent state. The minimal `ExecutionKey`
is only an opaque provenance reference; derivation and cache behavior remain
Phase 3. LangGraph remains the specified future execution kernel.

The next proposed slice is **Phase 2B: content-addressed filesystem repository**.
It requires review of Phase 2A and explicit authorization before implementation.
