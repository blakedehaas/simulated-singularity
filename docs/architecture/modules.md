# Module ownership

An implemented bounded module has a `module.yaml` next to its code. The manifest
helps a maintainer or coding agent identify ownership and boundaries before
editing. It describes the current implementation; it is not a future API plan.

| Field | Meaning |
| --- | --- |
| `name` | Fully qualified implemented module name. |
| `purpose` | The module's present responsibility. |
| `public_api` | Exported Python contracts or CLI commands. |
| `owns` | Concepts and behavior maintained in this module. |
| `depends_on` | Permitted direct dependencies used by this module. |
| `prohibited_dependencies` | Important forbidden dependencies, when useful. |
| `invariants` | Rules changes must preserve. |

The package-root manifest records composition ownership. Namespace packages do
not need a manifest merely because they hold a directory. Phase 2A adds two
bounded platform modules to the three Phase 1 modules.

| Module | Responsibility | Boundary |
| --- | --- | --- |
| `application` | Immutable facts/reports, runtime probe port, compatibility evaluation. | Standard-library types only; no deployment observation or CLI framework. |
| `platform.identifiers` | Nominal artifact, provenance, capability, and execution-key references. | Stable text values only; no storage or execution behavior. |
| `platform.artifacts` | Immutable artifacts/provenance, SHA-256 primitives, and repository port. | Depends inward on identifiers; no adapter or filesystem policy. |
| `infrastructure` | Observe OS, architecture, and Python version. | Implements the application port structurally; does not choose policy. |
| `interfaces.cli` | Present `ss` help and diagnostics, JSON, and exit status. | Calls composition and does not construct infrastructure. |
| package composition | Supply the local adapter to the application. | Owns wiring, not evaluation or presentation. |

`RuntimeProbe.inspect()` returns `RuntimeFacts`. `run_doctor()` inspects once,
then evaluates the three required checks in operating-system, architecture,
Python order. DTOs are frozen dataclasses. `DoctorReport.passed` is derived from
all checks. Observation failures propagate and cannot become successful reports.

`ArtifactId` is the payload SHA-256. `ArtifactPayload` and `ArtifactRecord` own no
path, while `ProvenanceRecord` refers to a minimal opaque `ExecutionKey` without
Phase 3 semantics. `ArtifactRepository` is implemented by future infrastructure,
not by the platform module.

Import-linter contracts in `pyproject.toml` enforce dependency direction and
prohibited imports. Manifests complement that enforcement with purpose and
invariants. Update both when an approved architectural change modifies a boundary.
Do not add manifests or ports for unimplemented capabilities.
