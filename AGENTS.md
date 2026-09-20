# Simulated Singularity — Agent Instructions

**Status:** Normative repository instructions for coding agents and maintainers  
**Repository:** `simulated-singularity`  
**Current authorized milestone:** Phase 0 + Phase 1 only

This file is intentionally concise. It routes agents to the normative specifications and records the invariants that must be present in every implementation session. Do not duplicate the full specifications here.

## 1. Required reading and authority

Before making architectural or implementation decisions, read in this order:

1. `docs/specifications/phase-0-1.md`
2. `docs/specifications/technical-implementation-guide.md`
3. Relevant existing code, tests, module manifests, ADRs, and documentation for the area being changed.

Authority rules:

- `phase-0-1.md` is the **current scope gate**. It authorizes **Phase 0 and Phase 1 only**.
- `technical-implementation-guide.md` is the primary long-form architectural and implementation specification within the authorized scope.
- A GitHub issue describes the task-specific delta; it does not silently override repository specifications.
- If an issue conflicts with a normative specification, identify the conflict rather than silently following the issue.
- Do not begin Phase 2 until Phase 1 has been reviewed and explicitly authorized.
- If a time-sensitive dependency/runtime fact materially affects implementation, verify it against an authoritative current source when the available tools permit. Do not guess a version or compatibility claim.
- If current authoritative behavior genuinely conflicts with the specifications, make the smallest principled adjustment and document the deviation.

At the beginning of a new implementation thread, read both specifications completely. On continuation turns, revisit only the sections relevant to the current work unless context has been lost or the architectural question has changed.

## 2. Current scope: Phase 0 + Phase 1

The immediate goal is a clean-slate, production-quality repository foundation.

**Do not implement TTS yet.** In Phase 1, do not implement:

- Qwen inference;
- Whisper validation;
- audiobook rendering;
- artifact-production graphs;
- the complete artifact subsystem;
- speech-production behavior;
- simulation graphs or persistent simulated reality;
- music, image, video, or other future modality capabilities;
- speculative services, placeholder APIs, or empty future packages.

The legacy Simulated Singularity TTS application is reference material only. Do not add migration layers, compatibility shims, deprecated interfaces, legacy renderer wrappers, or architecture-preservation adapters.

## 3. Architectural north star

Simulated Singularity is a **LangGraph-native artifact factory** intended to grow into a scalable multimodal and simulation platform.

Preserve these boundaries now even though later capabilities are out of scope:

- **LangGraph = execution/orchestration.** Do not build a competing workflow engine.
- **Artifacts = durable products.** Future artifacts are immutable and content-addressed; graph state will hold references rather than large multimedia payloads.
- **Capabilities = what the platform can do.**
- **Providers = how a capability is implemented.**
- **Interfaces = clients of application contracts.** The CLI is not the application.
- **Modular monolith first.** Use strong internal boundaries inside one canonical Linux application/container. Do not create premature microservices.

The canonical Python package name is:

```text
simulated_singularity
```

Never center the platform architecture on TTS or name the package `simulated_singularity_tts`.

## 4. Dependency and design rules

Use explicit ports-and-adapters boundaries and machine-enforce dependency direction where practical.

Domain/application code must not directly depend on provider or deployment details such as:

- Qwen;
- Whisper;
- FFmpeg;
- CUDA;
- Docker;
- Google Cloud;
- SQLite;
- local filesystem paths;
- Typer;
- HTTP frameworks.

Provider/infrastructure code may implement application-facing ports. Domain code must not import infrastructure or interface layers.

Public contracts are architectural boundaries. Treat changes to these as architectural actions rather than routine refactors:

- public `Protocol` signatures;
- graph input/output schemas;
- graph state contracts;
- persistent schemas;
- event schemas;
- public DTOs;
- public CLI behavior;
- dependency direction.

Do not change an exported contract merely because changing it makes the current implementation easier. If a materially different architectural decision is required, document the proposed decision and obtain human review; use an ADR when the decision is adopted.

## 5. Repository design for agents

Implemented bounded modules should be self-describing and independently understandable.

Prefer:

- clear ownership;
- small public APIs;
- explicit names rather than vague abbreviations;
- typed contracts;
- explicit invariants;
- contract tests;
- complete public docstrings;
- concise `module.yaml` manifests for implemented bounded modules.

A module manifest should describe only what exists now, including fields such as:

- module name;
- purpose;
- public API;
- owned concepts;
- permitted dependencies;
- prohibited dependencies when useful;
- invariants.

Do not create module manifests, packages, Protocols, graph definitions, or other APIs for capabilities that do not yet exist.

## 6. Code-shape constraints

Prefer simple, explicit implementations over premature abstraction.

- Use objects where identity, lifecycle, state, replaceable behavior, dependency injection, or a domain concept justifies them.
- Use pure functions for stateless transformations.
- Do not create classes solely to wrap a single pure function.
- Avoid dumping grounds such as generic `utils.py`, `helpers.py`, `manager.py`, or giant model/renderer files.
- Graph-definition files should primarily describe topology, not implementation algorithms.
- Avoid circular dependencies.

File size is a design smell, not a hard rule:

- `<300` lines: ordinary;
- `300–500`: inspect responsibility;
- `500–800`: likely decomposition candidate;
- `>800`: architecture review warranted.

## 7. Canonical runtime

The application has one canonical runtime target:

- Linux;
- `linux/amd64`;
- NVIDIA CUDA;
- Python 3.12;
- Docker/OCI container.

Windows/WSL2 may host the container but is not a second application runtime.

Do not add native-Windows inference, CPU fallback inference, AMD/DirectML fallback, or parallel runtime branches.

During Phase 1, implement only runtime/deployment pieces actually authorized by the specifications. Do not pretend unavailable future providers or models exist.

## 8. Documentation and ADR discipline

All public classes, functions, Protocols, graph states, DTOs, and domain models must have useful docstrings that explain purpose and important invariants; include responsibilities, non-responsibilities, inputs/outputs, and failure behavior when relevant.

Architecture decisions belong in concise ADRs using:

- Context;
- Decision;
- Consequences;
- Alternatives considered.

Do not write an ADR for ordinary implementation details. Do not make materially different architectural decisions silently.

## 9. Development method

Phase 1 establishes contracts future agents will inherit. Work conservatively and sequentially.

For every meaningful increment:

1. inspect before editing;
2. make the smallest coherent change;
3. run relevant tests/static checks immediately;
4. fix failures before proceeding;
5. keep the repository runnable;
6. avoid temporary architecture and speculative abstractions;
7. do not defer known correctness problems into TODOs.

Do not parallelize independent architectural decisions during Phase 1. One agent may implement a bounded issue, but architectural contracts remain subject to human review before promotion.

Do not ask for clarification merely because several implementation details are reasonable. Choose the simplest design consistent with the specifications. Ask for human input when a materially different architectural decision from the specifications would be required.

## 10. Required Phase 1 quality bar

Phase 1 should finish with all applicable foundation checks green, including:

- clean container build;
- successful package import;
- working `ss` CLI entry point and `ss --help`;
- truthful Phase-1-appropriate `ss doctor`;
- tests passing;
- strict type checking passing;
- lint and format checks passing;
- dependency/import architecture checks passing;
- Python compile validation passing;
- documentation build passing;
- public APIs documented;
- comprehensive meaningful coverage for production Python;
- no placeholder implementations;
- no TODO architecture;
- no legacy compatibility code;
- no business logic hidden in CLI commands;
- no circular architectural dependencies.

Use reproducible dependency locking. Do not use unbounded `latest` dependencies. Keep the dependency surface intentionally small.

## 11. Scope completion and handoff

When a Phase 1 implementation issue is complete, provide a concise engineering handoff covering:

- what changed;
- architecture/boundaries established;
- public contracts introduced or changed;
- exact validation performed and results;
- deviations from the Technical Implementation Guide, if any;
- intentional scope exclusions;
- concise repository map when useful;
- the next authorized milestone.

The next milestone after reviewed Phase 1 is **Phase 2: immutable artifact foundation**. Do not begin it automatically.

## 12. Factory execution rules

When running under the Simulated Singularity Symphony/Codex factory:

- work only in the provided issue workspace;
- create and commit only the dedicated issue branch;
- never obtain or search for GitHub credentials;
- never push directly to `main`, `dev`, `blakedehaas`, or `agent-dev`;
- never force-push or rewrite shared history;
- use the provided credential-isolated publication mechanism rather than direct authenticated Git operations;
- leave the pull request unmerged for review.

The factory's workflow instructions may provide more specific operational commands. Follow those commands when they do not conflict with this repository specification.
