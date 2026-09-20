# Artifact contracts

Phase 2A defines durable-product contracts without choosing a persistence adapter.
The public API is exported from `simulated_singularity.platform.artifacts` and
`simulated_singularity.platform.identifiers`.

## Identity and serialization

`ArtifactId` is exactly 64 lowercase hexadecimal characters: the SHA-256 digest
of the payload bytes, with no `sha256:` prefix. Its `serialize()` method and
`str()` return that digest. Uppercase, truncated, and non-hexadecimal values fail
validation.

`ProvenanceId`, `CapabilityId`, and `ExecutionKey` are nominally distinct,
immutable values. Their canonical serialization is the exact non-empty input
text; surrounding whitespace is rejected rather than normalized. Phase 2A does
not prescribe UUID generation for caller-assigned identifiers.

`ExecutionKey` exists solely because provenance refers to it. It is opaque:
Phase 2A defines no canonical configuration serialization, key derivation,
retry identity, cache lookup, or cache semantics. Those decisions belong to
Phase 3.

## Immutable values

`ArtifactPayload` carries immutable `bytes`, an open `ArtifactType`, media type,
timezone-aware creation time, provenance reference, and metadata. It never
contains a durable filesystem path. `ArtifactRecord` adds the content-derived
identity, digest, and byte length without embedding payload bytes.

Artifact metadata is copied during construction. Objects become read-only
mappings and arrays become tuples recursively. Keys must be strings; values must
be JSON scalars, arrays, or objects, and floats must be finite. This prevents
mutation through a caller-retained container while preserving deterministic,
JSON-compatible information for later adapters.

`ProvenanceRecord` stores capability and provider identity/version, optional model
and container identity, application version, ordered input artifact IDs, a
canonical configuration SHA-256 supplied by the future execution layer, the
opaque execution-key reference, optional random seed, and a timezone-aware
creation time. The record is frozen and contains no execution behavior.

## Content addressing and repository port

`compute_sha256()` returns standard lowercase SHA-256 hexadecimal text.
`artifact_id_for_content()` creates the corresponding `ArtifactId`.
`verify_content_sha256()` accepts only canonical digest text and raises
`ArtifactIntegrityError` for malformed text or mismatched bytes.

`ArtifactRepository` is the adapter-neutral port:

```python
def put(artifact: ArtifactPayload) -> ArtifactRecord: ...
def get(artifact_id: ArtifactId) -> ArtifactPayload: ...
def exists(artifact_id: ArtifactId) -> bool: ...
```

The contract requires content-derived identity, verified reads and reuse,
idempotence for identical payloads, structured missing-artifact failure, and no
filesystem paths. `tests/contract/artifact_repository_contract.py` provides the
reusable behavioral suite for Phase 2B and later implementations. Phase 2A uses
an in-test memory double only to prove that suite; it is not a platform adapter.
`ArtifactNotFoundError` and `ArtifactIntegrityError` share the public
`ArtifactError` base for structured caller handling.

## Current exclusions

There is no filesystem repository, atomic write implementation, SQLite schema,
metadata repository, execution-key derivation, cache, LangGraph graph, lifecycle,
provider, or modality behavior in Phase 2A.
