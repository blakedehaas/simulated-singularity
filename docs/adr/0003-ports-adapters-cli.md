# 0003: Ports, adapters, and CLI composition

Status: Established by the normative specifications; concrete contracts subject
to Phase 1 review.

## Context

The CLI is the first client of the application. Future clients must be able to
reuse application policy without importing CLI or deployment details.

## Decision

Use one modular monolith with explicit ports and adapters. Application diagnostics
owns `RuntimeProbe`, immutable DTOs, and `run_doctor`. `LocalRuntimeProbe` collects
process facts. `bootstrap.diagnose_runtime` wires the adapter to the application;
the Typer CLI formats its report. Import-linter enforces these boundaries.

The public CLI offers help and `doctor`, with schema-version-1 JSON and documented
exit codes. Public contracts and dependency direction require architectural review
when changed.

## Consequences

Application policy is independently testable using supplied observations. The
CLI cannot directly construct infrastructure. Observation failures propagate;
failed required checks cannot be presented as successful diagnostics. Manifests
and generated public API documentation describe current ownership.

## Alternatives considered

Putting compatibility policy in command handlers would couple application
behavior to Typer. Adding services or a general dependency-injection framework
adds machinery without a current need. Direct explicit composition is sufficient.
