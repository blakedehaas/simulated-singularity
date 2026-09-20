# Architecture

Simulated Singularity is a clean-slate, LangGraph-native artifact factory. Phase
2A adds immutable artifact contracts to the reviewed Phase 1 modular Python
application. The [Phase 2 specification](docs/specifications/phase-2.md) gates the broader
[implementation guide](docs/specifications/technical-implementation-guide.md).

The implemented runtime slice remains diagnostics:

```text
interfaces.cli.app             presentation and process exit status
        |
        v
bootstrap.diagnose_runtime      composition
        |
        +--> application.diagnostics     contracts and compatibility policy
        |
        +--> infrastructure.runtime     observations of the current process
                      |
                      v
             application.diagnostics.RuntimeFacts
```

The CLI calls the composition root, which supplies `LocalRuntimeProbe` to the
application's `RuntimeProbe` port. `run_doctor` evaluates immutable observations
and returns a `DoctorReport`. It has no operating-system, filesystem, framework,
or provider imports. The runtime adapter collects facts without choosing policy;
the CLI formats the result without deciding compatibility.

Phase 2A adds a separate provider-neutral platform boundary:

```text
platform.artifacts
  immutable ArtifactPayload / ArtifactRecord / ProvenanceRecord
  ArtifactRepository port
  SHA-256 derivation and verification
          |
          v
platform.identifiers
  ArtifactId / ProvenanceId / CapabilityId / opaque ExecutionKey
```

Artifact identity is exactly the lowercase 64-character SHA-256 digest of its
bytes. Models expose no filesystem path. Metadata is copied into recursively
read-only mappings and tuples, and accepts only finite JSON values. Repository
adapters will depend on these contracts; none is implemented in Phase 2A.

Import-linter enforces inward dependency direction, prevents the CLI from
constructing infrastructure, and forbids adapter, deployment, presentation, and
future-provider dependencies in application and platform contracts. Artifacts
may depend only inward on identifiers. See [the module convention](docs/architecture/modules.md)
and each implemented module's `module.yaml` for its public surface and invariants.

Public contracts include the artifact and provenance models, identifiers,
content-addressing functions, `ArtifactRepository`, diagnostics DTOs and port,
the composition function, and the `ss doctor` behavior. Changing these boundaries is an
architectural action. The [CLI contract](docs/architecture/cli.md) documents the
versioned machine output. Generated API documentation derives from public Python
docstrings.

The canonical deployment is `linux/amd64`, Ubuntu 24.04, NVIDIA CUDA 13, and
Python 3.12. Compose reserves NVIDIA GPUs. Foundation diagnostics check only
Linux, x86-64, and Python 3.12 because inference is not implemented. The same
Python code is exercised by local development checks; there is no alternate
application runtime or inference backend.

The future boundaries are deliberate: LangGraph owns execution, immutable
content-addressed artifacts own durable products, capabilities describe what can
be done, and providers implement capability contracts. `ExecutionKey` is only an
opaque provenance reference; derivation and cache semantics remain Phase 3. These
boundaries are recorded in [ADRs](docs/adr/index.md).

```text
src/simulated_singularity/
  application/diagnostics.py      runtime contracts and evaluation
  platform/identifiers/           nominal identifiers and serialization
  platform/artifacts/             immutable models, hash primitives, repository port
  infrastructure/runtime.py       local runtime observation
  interfaces/cli/app.py           ss help and doctor
  bootstrap.py                    adapter composition
tests/                            policy, contracts, adapter, and CLI checks
docs/                             specifications, architecture, ADRs, API reference
```

After Phase 2A review, the next proposed slice is **Phase 2B: content-addressed
filesystem repository**. It will add atomic durable writes, integrity verification,
idempotent reuse, and run the reusable repository contract against that adapter.
No filesystem or SQLite persistence is implemented yet.
