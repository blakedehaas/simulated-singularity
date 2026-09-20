# 0002: LangGraph execution and durable artifacts

Status: Established by the normative specifications; later implementations are
outside Phase 1.

## Context

The future platform needs resumable workflows and durable multimedia products.
Execution state and durable products have different ownership and lifecycle.

## Decision

LangGraph is the future execution/orchestration kernel. Artifacts will be
immutable and content-addressed; graph state will contain their references rather
than multimedia bytes. Capabilities describe what the platform does; providers
implement capability contracts. No competing workflow engine is introduced.

## Consequences

Phase 1 records these boundaries without adding graph definitions, artifact APIs,
provider packages, or dependencies that have no implemented consumer. Phase 2
will implement the immutable artifact foundation. Execution follows separately.

## Alternatives considered

A custom workflow engine duplicates LangGraph's role. Storing media in graph
state entangles persistence with product storage. Implementing a partial artifact
system now exceeds the authorized milestone.
