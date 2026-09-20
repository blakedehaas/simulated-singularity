# 0001: Clean-slate platform and phase scope

Status: Established by the normative specifications; implementation subject to
Phase 1 review.

## Context

The platform will grow beyond its legacy TTS reference application. Its first
implementation milestone must establish reliable boundaries without carrying
legacy state, interfaces, or architecture into the new repository.

## Decision

Use the `simulated_singularity` package and implement Phase 0 + Phase 1 only.
Create modules only for complete implemented responsibilities. The current slice
is runtime diagnostics and its supporting development/deployment foundation.

## Consequences

There are no migration layers, renderer wrappers, compatibility shims, placeholder
capabilities, or pre-created artifact packages. Future work adds complete slices.
Phase 2 requires Phase 1 review and explicit authorization.

## Alternatives considered

Preserving the legacy structure would make TTS the platform's center. Creating
the full future package tree now would establish unsupported contracts. Both
conflict with the current scope specification.
