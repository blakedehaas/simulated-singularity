# Simulated Singularity — Phase 2 Immutable Artifact Foundation

**Status:** Normative agent-facing scope specification  
**Milestone:** Phase 2 — Immutable artifact foundation  
**Authority:** Subordinate to `AGENTS.md` and the full Technical Implementation Guide  
**Prerequisite:** Phase 0 + Phase 1 reviewed and merged  
**Next milestone:** Phase 3 — execution foundation; not authorized by this document

> This document narrows the existing Technical Implementation Guide to the work authorized for Phase 2. It does not replace the guide. Where this document is silent, follow `AGENTS.md` and `docs/specifications/technical-implementation-guide.md`. If a genuine conflict is found, surface it explicitly rather than broadening scope.

## 1. Objective

Implement the durable artifact foundation on which later execution graphs and capabilities will depend.

Phase 2 MUST establish:

- typed platform identifiers needed by the artifact subsystem;
- immutable artifact records;
- immutable artifact payload handling;
- content-addressed filesystem storage;
- an `ArtifactRepository` contract and filesystem implementation;
- atomic, integrity-checked artifact writes;
- platform metadata persistence in SQLite for artifact and provenance records;
- provenance records sufficient to describe generated artifacts;
- contract, unit, and integration tests for the above;
- module manifests, architecture enforcement, and documentation for every bounded module introduced.

Phase 2 MUST NOT implement Phase 3 execution behavior or any TTS/provider capability.

## 2. Required reading

Before implementation:

1. Read repository-root `AGENTS.md`.
2. Read this document completely.
3. Read these sections of `docs/specifications/technical-implementation-guide.md`:
   - Architectural principles;
   - Repository structure;
   - Public interfaces;
   - Artifact model;
   - Provenance;
   - Local persistence;
   - Dependency direction;
   - Documentation rules;
   - Testing strategy;
   - Coverage and quality gate;
   - Agent-first repository constraints;
   - File-size discipline;
   - Implementation order.
4. Inspect the merged Phase 1 architecture, ADRs, module manifests, tests, and import-linter rules before editing.

Do not reread unrelated TTS/provider sections unless a concrete architectural question requires them.

## 3. Scope boundary

### Authorized

Phase 2 authorizes only the artifact foundation:

```text
typed identifiers
      ↓
immutable artifact/provenance models
      ↓
ArtifactRepository port
      ↓
content-addressed filesystem repository
      ↓
platform SQLite metadata persistence
      ↓
contract + integration validation
```

### Explicitly out of scope

Do NOT implement:

- LangGraph graphs or graph state;
- `ArtifactFactoryGraph`;
- execution-key derivation or canonical execution-cache behavior;
- run orchestration;
- checkpoint/resume;
- LangGraph SQLite persistence;
- typed execution events;
- run/review lifecycle behavior;
- speech domain models;
- Qwen, Whisper, FFmpeg, or other providers;
- model locking or model download behavior;
- TTS rendering;
- future modality packages;
- simulation graphs or simulation state;
- HTTP services, cloud workers, or microservices;
- speculative CLI commands for later capabilities;
- placeholder future APIs, empty packages, or TODO implementations.

The platform remains a modular monolith.

## 4. Architectural invariants

### 4.1 Artifacts are immutable

Every durable input or generated product is represented as an artifact.

An artifact payload MUST:

- be addressed by content hash;
- never be mutated in place;
- produce a new artifact identity when content changes.

No API may silently overwrite an existing content-addressed payload with different bytes.

### 4.2 Artifact identity is content-derived

Content addressing MUST use SHA-256.

The canonical artifact payload layout is rooted at:

```text
/workspace/artifacts/
└── sha256/
    └── <prefix>/
        └── <full-content-hash>
```

The exact safe prefix width may be selected consistently by the implementation, but the full SHA-256 MUST remain the payload identity and MUST be verifiable from stored bytes.

### 4.3 Durable metadata is separate from payload bytes

Use independent persistence concerns:

```text
/workspace/artifacts/          immutable payload bytes
/workspace/state/platform.sqlite3
                              platform metadata/provenance
```

Phase 2 MUST NOT place multimedia/blob payloads in SQLite.

Phase 2 MUST NOT create or modify LangGraph checkpoint tables. The future LangGraph database remains a separate persistence concern.

### 4.4 Ports remain provider-neutral

The artifact contract MUST describe artifact behavior, not the filesystem or SQLite implementation.

Canonical repository contract:

```python
class ArtifactRepository(Protocol):
    """Stores and retrieves immutable content-addressed artifacts."""

    def put(self, artifact: ArtifactPayload) -> ArtifactRecord:
        ...

    def get(self, artifact_id: ArtifactId) -> ArtifactPayload:
        ...

    def exists(self, artifact_id: ArtifactId) -> bool:
        ...
```

Equivalent refinements are allowed only when they preserve the specified responsibility and are justified by the existing architecture. Do not expose local filesystem paths as the platform contract.

### 4.5 Dependency direction remains inward

Infrastructure implements platform/application contracts; platform/domain contracts do not depend on infrastructure.

In particular, artifact/domain models MUST NOT depend on:

- SQLite;
- concrete filesystem APIs as storage policy;
- Typer;
- Docker;
- Google Cloud;
- Qwen;
- Whisper;
- FFmpeg.

Machine-enforce new boundaries with import-linter or equivalent existing repository enforcement.

## 5. Typed identifiers

Implement explicit typed identifiers needed by Phase 2, including at minimum:

- `ArtifactId`;
- `ProvenanceId`;
- `CapabilityId` where required by provenance.

Identifiers MUST:

- prevent accidental interchange of semantically different IDs under static typing where practical;
- have deterministic, documented serialization;
- avoid ambiguous generic names such as bare `id`;
- remain independent of storage adapters.

Do not implement future execution/run/review identity behavior merely because later phases will need additional identifiers.

## 6. Artifact model

Use a single generic immutable artifact record with typed metadata rather than a deep media-type inheritance hierarchy.

The Phase 2 record MUST preserve the semantics of:

```python
class ArtifactRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    artifact_id: ArtifactId
    artifact_type: ArtifactType
    content_sha256: str
    byte_length: int
    media_type: str
    created_at: datetime
    provenance_id: ProvenanceId
    metadata: dict[str, JsonValue]
```

Implementation details may adapt to the established Phase 1 conventions, but MUST preserve:

- immutability;
- content SHA-256;
- byte length;
- media type;
- provenance linkage;
- typed artifact identity;
- JSON-compatible metadata.

Avoid a hierarchy such as `TextArtifactRecord`, `AudioArtifactRecord`, `ImageArtifactRecord`, etc. Phase 2 is platform infrastructure, not modality implementation.

`ArtifactPayload` MUST represent payload content without coupling callers to a particular durable filesystem path.

## 7. Atomic content-addressed writes

A successful durable write MUST follow the semantic sequence:

```text
write temporary payload
    ↓
flush / fsync durable content
    ↓
compute or verify SHA-256
    ↓
place at content-addressed destination by atomic rename
    ↓
register metadata
```

Required behavior:

- partial writes MUST NOT appear as valid artifacts;
- a hash mismatch MUST fail closed;
- an existing payload at the expected hash MUST be verified before reuse;
- repeated storage of identical bytes MUST be idempotent;
- a conflicting payload MUST never overwrite immutable content;
- temporary files MUST be safely cleaned or left recoverable without corrupting the repository;
- failures MUST surface as typed/structured artifact integrity or persistence errors consistent with repository conventions.

The implementation MUST test failure paths, not only the happy path.

## 8. Provenance

Every generated artifact requires immutable provenance sufficient for future reproducibility.

Preserve the Technical Implementation Guide's provenance semantics:

- provenance ID;
- capability ID;
- capability version;
- provider ID;
- provider version;
- model identity when applicable;
- model revision when applicable;
- application/container version where represented by the established schema;
- input artifact IDs;
- canonical configuration hash;
- execution-key reference;
- random seed where applicable;
- creation time.

The guide's illustrative shape includes:

```python
class ProvenanceRecord(BaseModel):
    provenance_id: ProvenanceId
    capability_id: CapabilityId
    capability_version: str
    provider_id: str
    provider_version: str
    model_id: str | None
    model_revision: str | None
    input_artifact_ids: tuple[ArtifactId, ...]
    configuration_sha256: str
    execution_key: ExecutionKey
    random_seed: int | None
```

### Phase-boundary note: `ExecutionKey`

The Technical Implementation Guide references `ExecutionKey` in provenance while assigning **execution-key implementation** to the next implementation stage.

For Phase 2:

- it is permissible to define only the minimal typed value/reference required for the provenance record contract;
- do NOT implement execution-key derivation, canonical configuration-to-key algorithms, retry identity, execution caching, or cache lookup behavior;
- those behaviors belong to Phase 3;
- if satisfying the provenance contract would require broader execution behavior, document the conflict rather than silently importing Phase 3.

This is a sequencing boundary, not authorization to implement execution infrastructure.

## 9. Platform metadata SQLite

Use:

```text
/workspace/state/platform.sqlite3
```

Phase 2 metadata persistence MUST cover:

- artifact records;
- provenance records;
- relationships required to retrieve/validate those records.

Although the final platform database will later also contain run, review, and execution-cache data, Phase 2 MUST NOT implement those later lifecycle systems merely to pre-create tables.

Requirements:

- explicit schema initialization;
- deterministic serialization/deserialization;
- foreign-key/integrity enforcement where appropriate;
- no mixing with LangGraph checkpoint schema;
- no blob/media payload storage;
- integration tests against real SQLite;
- restart/reopen persistence tests;
- clean failure behavior for corrupt, missing, or inconsistent metadata.

Do not add an ORM unless it materially improves the existing architecture and dependency policy; prefer the smallest explicit persistence design consistent with Phase 1 conventions.

## 10. Repository/module structure

Follow the Technical Implementation Guide's intended boundaries, adapted to the repository actually established in Phase 1.

Expected concepts include:

```text
src/simulated_singularity/
├── platform/
│   ├── identifiers/
│   └── artifacts/
│       ├── models
│       ├── repository contract
│       ├── content addressing
│       └── provenance
└── infrastructure/
    ├── artifacts/
    │   └── filesystem repository
    └── metadata/
        └── SQLite persistence
```

Do not mechanically create files or packages that have no complete Phase 2 responsibility.

Every bounded module introduced MUST include/update:

- useful public docstrings;
- `module.yaml`;
- public API description;
- owned concepts;
- permitted/prohibited dependencies;
- invariants;
- relevant architecture documentation.

Changing an established public contract or dependency direction is an architectural action and requires the repository's ADR process.

## 11. Testing requirements

Tests MUST mirror architecture.

### Unit tests

Cover at minimum:

- typed identifiers and serialization;
- hash/content-address derivation;
- immutable models;
- metadata validation;
- provenance validation;
- atomic-write helper behavior;
- integrity/error branches.

### Contract tests

Define reusable `ArtifactRepository` contract tests and run them against the filesystem implementation.

The contract MUST exercise at least:

- put/get round trip;
- exists behavior;
- identical-content idempotence;
- immutable identity;
- missing artifact behavior;
- content/hash integrity;
- reopen/restart behavior where applicable.

### Integration tests

Use real temporary filesystem and SQLite resources to verify:

- content-addressed payload persistence;
- atomic registration;
- artifact metadata persistence;
- provenance persistence;
- reopening the database/repository;
- metadata/payload consistency;
- failure behavior.

No GPU or model downloads are required for Phase 2.

## 12. Quality gate

Phase 2 must preserve all applicable Phase 1 release gates.

At minimum, before handoff:

- Ruff lint passes;
- format check passes;
- strict mypy passes;
- import-linter/architecture checks pass;
- pytest passes;
- production Python maintains the repository's comprehensive/100% line-coverage standard;
- exception/failure branches are meaningfully tested;
- compile validation passes;
- documentation builds successfully;
- packaging/install smoke remains green;
- canonical container build/runtime checks remain green;
- committed dependency locks remain reproducible/current;
- worktree is clean.

Do not add meaningless tests merely to satisfy coverage.

## 13. Recommended implementation slices

Phase 2 may be delivered as sequential, independently reviewable increments:

### Phase 2A — Artifact contracts

Implement:

- typed identifiers;
- immutable artifact/provenance models;
- `ArtifactRepository` protocol;
- content-addressing primitives;
- module manifests;
- unit/contract-test framework;
- architecture enforcement/documentation.

Do not implement filesystem/SQLite behavior beyond what is required to prove contracts.

### Phase 2B — Content-addressed filesystem repository

Implement:

- filesystem adapter;
- atomic writes;
- hash verification;
- idempotent identical-content behavior;
- repository contract compliance;
- filesystem integration tests.

### Phase 2C — Metadata and provenance persistence

Implement:

- `platform.sqlite3` schema for Phase 2 records;
- artifact metadata persistence;
- provenance persistence;
- integrity relationships;
- reopen/restart tests;
- final Phase 2 documentation and end-to-end artifact persistence validation.

Each merged slice MUST be complete and tested. Do not merge placeholders for later slices.

## 14. Definition of done

Phase 2 is complete when the repository can, without implementing an execution graph or TTS capability:

1. construct a valid immutable artifact payload/record;
2. derive and verify its content hash;
3. atomically store its bytes in the content-addressed artifact repository;
4. persist its artifact metadata in `platform.sqlite3`;
5. persist and retrieve its provenance;
6. close and reopen the persistence layer;
7. retrieve the same artifact and verify its bytes, identity, and provenance;
8. reject integrity violations and invalid mutation attempts;
9. pass reusable `ArtifactRepository` contract tests;
10. pass all applicable repository quality, architecture, documentation, packaging, and container gates.

The implementation MUST leave no known Phase 2 TODOs, placeholder APIs, or silent integrity failures.

## 15. Handoff requirements

The final Phase 2 handoff MUST report:

- implemented modules and responsibilities;
- public contracts introduced or changed;
- artifact identity/content-addressing scheme;
- atomic-write guarantees;
- SQLite schema ownership and persistence behavior;
- provenance fields and the exact treatment of the Phase 3 `ExecutionKey` boundary;
- architecture/import rules added or changed;
- exact unit/contract/integration/CI validation results;
- coverage results;
- any deviation from the Technical Implementation Guide;
- intentionally excluded later-phase scope;
- concise resulting repository map;
- the proposed Phase 3 milestone.

Do not begin Phase 3 without explicit authorization.
