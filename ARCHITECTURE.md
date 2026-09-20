# Architecture

Simulated Singularity is a clean-slate, LangGraph-native artifact factory. Phase 1
establishes one modular Python application in one canonical Linux container.
The [phase specification](docs/specifications/phase-0-1.md) gates the broader
[implementation guide](docs/specifications/technical-implementation-guide.md).

The implemented vertical slice is runtime diagnostics:

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

Import-linter enforces inward dependency direction, prevents the CLI from
constructing infrastructure, and forbids deployment and presentation dependencies
in application code. See [the module convention](docs/architecture/modules.md)
and each implemented module's `module.yaml` for its public surface and invariants.

Public contracts include the diagnostics DTOs and port, the composition function,
and the `ss doctor` output and exit behavior. Changing these boundaries is an
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
be done, and providers implement capability contracts. Graph state will hold
artifact references rather than multimedia bytes. These boundaries are recorded
in [ADRs](docs/adr/index.md); their later implementations are outside Phase 1.

```text
src/simulated_singularity/
  application/diagnostics.py      runtime contracts and evaluation
  infrastructure/runtime.py       local runtime observation
  interfaces/cli/app.py           ss help and doctor
  bootstrap.py                    adapter composition
tests/                            policy, contracts, adapter, and CLI checks
docs/                             specifications, architecture, ADRs, API reference
```

After Phase 1 review, the next proposed milestone is **Phase 2: implement the
immutable artifact foundation**: identifiers, immutable records, content-addressed
filesystem storage, separate SQLite metadata, provenance, atomic writes, and
repository contract tests. It requires explicit authorization; no artifact or
execution packages are pre-created here.
