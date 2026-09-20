# 0002: LangGraph execution and durable artifacts

Status: Accepted; artifact contracts implemented in Phase 2A and execution remains deferred.

## Context

The future platform needs resumable workflows and durable multimedia products.
Execution state and durable products have different ownership and lifecycle.

## Decision

LangGraph is the future execution/orchestration kernel. Artifacts will be
immutable and content-addressed; graph state will contain their references rather
than multimedia bytes. Capabilities describe what the platform does; providers
implement capability contracts. No competing workflow engine is introduced.

## Consequences

Phase 2A adds nominal identifiers, immutable artifact and provenance values,
SHA-256 primitives, and the `ArtifactRepository` port. It adds no persistence
adapter. The provenance `ExecutionKey` is an opaque value only; execution-key
derivation, graphs, and caching follow separately.

## Alternatives considered

A custom workflow engine duplicates LangGraph's role. Storing media in graph
state entangles persistence with product storage. Implementing a partial artifact
system now exceeds the authorized milestone.
