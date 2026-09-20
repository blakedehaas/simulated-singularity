# Contributing

Read the repository-root `AGENTS.md`, the complete
[Phase 0–1 specification](docs/specifications/phase-0-1.md), and the complete
[Technical Implementation Guide](docs/specifications/technical-implementation-guide.md)
before making architectural decisions. Phase 0 and Phase 1 are the current scope.

Use Linux with Python 3.12 for development. The supported deployed application is
the pinned NVIDIA CUDA container on `linux/amd64`. Docker with NVIDIA GPU support
is required for the canonical Compose deployment. Windows/WSL2 may host that
container; native Windows is not an application runtime.

```sh
make bootstrap
make check
.venv/bin/ss --help
.venv/bin/ss doctor --json
```

`make bootstrap` installs the locked development environment. `make check` runs
the foundation quality checks: lint, formatting, strict typing, import contracts,
tests and coverage, compilation, and documentation. Production Python is held to
100% coverage; tests should demonstrate behavior and failure handling, rather
than merely execute lines.

```sh
make docs
make container-check
make release-check
docker compose run --rm engine ss doctor --json
```

`make container-check` builds and exercises the foundation container. The
foundation smoke checks require no GPU execution. `make release-check` combines
the local and container checks. Record exact results before handing off work;
the existence of these commands does not establish that a particular checkout
has passed them.

Top-level dependencies are declared in `requirements.in`,
`requirements-build.in`, and `requirements-dev.in`; corresponding committed
lockfiles pin the complete dependency sets. Verify material version and runtime
claims against authoritative sources before changing pins. Run `make lock` to
regenerate locks and run the release checks after a dependency change. Never
replace a lock with unbounded runtime resolution.

Inspect the relevant implementation, tests, documentation, and module manifest
before editing. Make small coherent increments and run their relevant checks
immediately. Keep application policy behind typed contracts, infrastructure in
adapters, and CLI code limited to input/output and process status. Prefer a pure
function for stateless transformations. Do not create empty future packages.

Document public APIs with useful docstrings and keep generated API documentation
current. Update `module.yaml` when an implemented module's ownership or public
surface changes. Public protocols, DTOs, CLI behavior, persistent schemas, and
dependency direction are architectural contracts. Record adopted architectural
decisions in concise ADRs with Context, Decision, Consequences, and Alternatives
considered. A material departure from the supplied guide requires human review.

Issue branches target `agent-dev` for review. Existing promotion gates allow only
`agent-dev` or `blakedehaas` into `dev`, and only `dev` into `main`; release PR
titles start with `Release:`. Factory workers follow the publication instructions
provided for their issue and leave their pull requests unmerged.

A Phase 1 handoff states what changed, boundaries and public contracts, exact
validation results, deviations with rationale, intentional exclusions, a concise
repository map, and the next proposed milestone: **Phase 2: implement the
immutable artifact foundation**. Phase 2 starts only after Phase 1 review and
explicit authorization.
