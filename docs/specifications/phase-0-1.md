# Simulated Singularity - Phase 0-1 Implementation Specification

**Status:** Normative agent-facing specification  
**Source:** *Simulated Singularity - Phase 0-1 Fresh-Conversation Initialization Prompt* (September 2026)  
**Source PDF SHA-256:** `785e6d7e8062a0783ac9e3c2ad0f7dc5cd721b34e40c1634c18556be5b2d2970`  
**Companion specification:** `technical-implementation-guide.md`  
**Current authorized scope:** Phase 0 + Phase 1 only  
**Audience:** Coding agents and human maintainers

> This Markdown is an agent-first structural conversion of the source document. It preserves the source's intended requirements while reducing layout noise and repeated prose. If an ambiguity is discovered, compare against the source PDF and correct this Markdown rather than silently inventing behavior.

## 0. Required reading and authority

Before making architectural or implementation decisions:

1. Read this specification completely.
2. Read `technical-implementation-guide.md` completely.
3. Treat the Technical Implementation Guide as the primary implementation specification for this phase.
4. Treat this document as the **scope gate**: implement **Phase 0 and Phase 1 only**.
5. Do not casually reinterpret or broaden either document.
6. If a dependency/runtime fact is time-sensitive, verify it against an authoritative current source before pinning or implementing it.
7. If current authoritative behavior genuinely conflicts with the guide, identify the incompatibility explicitly and make the smallest principled adjustment.

## 1. Immediate objective

Implement only:

- **Phase 0 - Clean break**
- **Phase 1 - Architectural foundation**

Do **not** begin Phase 2 until Phase 1 has been reviewed.

---

## 2. Phase 0 - Clean break

Establish a new repository:

```text
simulated-singularity
```

The existing Simulated Singularity TTS application is a behavioral/reference implementation only.

### 2.1 No backward-compatibility requirement

There is no requirement to preserve the legacy application's:

- code structure;
- CLI;
- persistent state;
- schemas;
- remaster state;
- caches;
- version history;
- output directories;
- internal APIs.

### 2.2 Prohibited legacy work

Do **not** build:

- migration layers;
- compatibility shims;
- deprecated interfaces;
- wrappers around the legacy renderer;
- adapters whose only purpose is preserving the old architecture.

The audiobook can later be regenerated from its original source transcript and voice reference.

---

## 3. Phase 1 - Architectural foundation

Build the production-quality repository foundation on which the Technical Implementation Guide can later be implemented.

### 3.1 Explicitly out of scope

**Do not implement TTS yet.**

Phase 1 must **not** implement:

- TTS production behavior;
- Qwen inference;
- Whisper validation;
- audiobook rendering;
- artifact-production graphs;
- future simulation capabilities;
- music generation;
- image generation;
- video generation;
- speculative service implementations.

The goal is a **small, unusually disciplined repository** in which future work can safely occur.

---

## 4. Architectural north star

Simulated Singularity is intended to become:

> A LangGraph-native artifact factory in which autonomous agents and deterministic/model-backed capabilities operate through typed state machines, producing immutable multimedia artifacts with reproducible provenance.

Future platform capabilities may include:

- speech;
- text/story generation;
- music;
- images;
- video;
- visualization;
- multimodal composition;
- autonomous agents;
- multiscale simulations;
- persistent simulation state;
- dynamically activated subagents/subgraphs;
- rich web interfaces hosted at `simulatedsingularity.cc`.

The first production vertical slice will be TTS, but **TTS must not become the architectural center of the platform**.

Canonical Python package:

```text
simulated_singularity
```

Do not use:

```text
simulated_singularity_tts
```

---

## 5. Mandatory architectural principles

These principles remain mandatory unless explicitly changed through an architectural decision.

### 5.1 LangGraph is the orchestration substrate

LangGraph will eventually own:

- state-machine execution;
- cyclic workflows;
- subgraph composition;
- resumability;
- persistence boundaries;
- interrupts;
- delegation;
- dynamic fan-out;
- agent orchestration.

Do **not** build a competing custom workflow engine.

LangGraph does **not** own:

- multimedia bytes;
- domain models;
- model implementations;
- filesystem implementations;
- provider-specific logic;
- business rules.

### 5.2 Modular monolith first

Initially deploy a single Linux container/application with strong internal boundaries.

Use:

- bounded contexts;
- typed contracts;
- ports and adapters;
- explicit dependency direction;
- independently testable modules.

Do **not** introduce distributed microservices merely because they might be useful later.

Design boundaries so components can be extracted behind remote/API boundaries later if scale requires it.

### 5.3 Agentic-AI-first repository design

The repository will eventually be developed by multiple coding agents in parallel. Implemented modules should therefore expose:

- clear ownership;
- small public APIs;
- meaningful names;
- explicit invariants;
- machine-readable module manifests;
- contract tests;
- comprehensive in-code documentation.

An agent entering a module should quickly understand:

- why it exists;
- what it owns;
- what it may depend on;
- what contracts it exports;
- what invariants it must preserve.

### 5.4 Self-describing code

Prefer explicit identifiers, for example:

```text
semantic_validation_result
source_artifact_id
```

rather than vague names such as:

```text
result
id
```

Avoid unexplained abbreviations. Public APIs should be understandable without reverse engineering implementation details.

### 5.5 Object-oriented where appropriate

Use objects for:

- identity;
- lifecycle;
- state;
- replaceable behavior;
- dependency injection;
- domain concepts.

Use pure functions for stateless transformations.

Do not introduce classes merely to wrap one pure function.

### 5.6 Ports and adapters

Domain/application logic must not depend directly on:

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

Those dependencies belong behind ports/adapters.

### 5.7 Public contracts are stable boundaries

Implementation internals may change freely. Treat changes to the following as architectural actions:

- public `Protocol` signatures;
- graph input/output schemas;
- graph state contracts;
- persistent schemas;
- event schemas;
- public DTOs;
- public CLI behavior;
- dependency direction.

Do not casually propagate public-contract changes through the repository to make implementation easier.

### 5.8 No placeholder architecture

Do not create empty future APIs/packages such as:

```python
class VideoProductionGraph:
    # TODO
    pass
```

If a capability is not implemented as a complete vertical slice, it should not exist yet. Preserve extension points through architecture, not placeholder code.

### 5.9 No giant files

Avoid architectural dumping grounds such as:

- `utils.py`;
- `helpers.py`;
- `manager.py`;
- giant renderer files;
- giant generic model files.

Use file size as a design smell, not an arbitrary gate:

| Size | Guidance |
|---|---|
| `< ~300 LOC` | ordinary |
| `300-500 LOC` | inspect responsibility |
| `500-800 LOC` | likely decomposition candidate |
| `> 800 LOC` | architecture review warranted |

Graph-definition files should primarily describe topology, not contain algorithms.

### 5.10 Comprehensive documentation

All public classes, functions, `Protocol`s, graph states, DTOs, and domain models must have useful docstrings explaining, as applicable:

- purpose;
- responsibilities;
- non-responsibilities;
- important invariants;
- failure behavior;
- inputs/outputs.

Use documentation tooling capable of generating API reference automatically. Architecture decisions belong in ADRs.

---

## 6. Future graph taxonomy - preserve, do not implement in Phase 1

Expected future reusable graph definitions include:

- `SimulationGraph`;
- `CoordinatorGraph`;
- `ResolutionIslandGraph`;
- `EntityGraph`.

Runtime instances may be numerous. Graph definitions represent **execution scopes**, not the topology of the simulated universe.

Future persistent simulated reality will be represented separately as a sparse multiscale relational world model.

Intentional separation:

```text
LangGraph = execution/orchestration
Multiscale world model = simulated reality
```

Do not prematurely implement either system in Phase 1.

---

## 7. Artifact architecture - establish boundaries only

Future durable outputs may include:

- text;
- audio;
- images;
- video;
- simulation-state artifacts;
- validation artifacts;
- composition artifacts.

Future artifacts will be immutable and content-addressed. Graph state will contain artifact references rather than large multimedia payloads.

**Phase 1 requirement:** establish only the package/module boundaries and documentation required for this architecture. The complete artifact subsystem belongs to **Phase 2**.

---

## 8. Interface architecture

Development is currently CLI-first, but the CLI must eventually remain only one client of the application/backend.

Do not place domain/business logic inside CLI commands.

The architecture must remain capable of supporting the same application contracts from:

```text
CLI
HTTP API
autonomous agents
Google Cloud workers
rich web frontend
```

During Phase 1, establish only the CLI framework and foundational commands actually required by the Technical Implementation Guide.

---

## 9. Canonical runtime target

Canonical application runtime:

- Linux;
- `linux/amd64`;
- NVIDIA CUDA;
- Python 3.12;
- Docker/OCI container.

A Windows workstation may host development through Docker Desktop/WSL2, but **native Windows is not an application runtime**.

There must be one canonical Linux/CUDA code path.

Do not build:

- native-Windows inference support;
- CPU fallback inference;
- AMD fallback;
- DirectML fallback;
- parallel runtime branches.

Future Google Cloud deployment should run the same canonical container.

---

## 10. Phase 1 deliverables

Create a complete development foundation including, where appropriate to the Technical Implementation Guide:

- `pyproject.toml`;
- canonical package structure;
- `Dockerfile`;
- `compose.yaml`;
- source layout under `src/simulated_singularity`;
- test layout;
- `README.md`;
- `ARCHITECTURE.md`;
- `CONTRIBUTING.md`;
- ADR directory and initial ADRs;
- module-manifest convention;
- CLI entrypoint `ss`;
- initial `ss --help`;
- initial `ss doctor` appropriate to what actually exists in Phase 1;
- Ruff configuration;
- formatter configuration;
- strict type checking;
- pytest configuration;
- coverage configuration;
- import/dependency architecture enforcement;
- MkDocs;
- mkdocstrings;
- automated API/documentation generation;
- container build;
- compilation/static validation;
- local development commands;
- release-quality validation command(s).

Do not pretend nonexistent dependencies or capabilities exist. Example: `ss doctor` must not report on Qwen or Whisper until those providers actually exist.

---

## 11. Dependency policy

Before pinning dependencies whose versions materially matter:

1. Verify current authoritative versions and compatibility.
2. Use reproducible dependency locking.
3. Do not use unbounded `latest` dependencies.
4. Keep the dependency surface intentionally small.
5. Prefer the standard library when it is sufficient; add a framework only when it materially improves the architecture.

---

## 12. Architecture enforcement

Architectural boundaries should be machine-enforced where practical, not merely described.

Static/tests must prevent accidental dependency violations such as:

```text
domain -> infrastructure
domain -> CLI
```

The initial module set must remain minimal. Do not create empty future packages merely to satisfy a theoretical dependency diagram.

---

## 13. Module manifests for coding agents

Define a concise `module.yaml` convention for implemented bounded modules. It should be useful immediately to humans and autonomous coding agents without overengineering the schema.

Useful fields include:

- module name;
- purpose;
- public API;
- owned concepts;
- permitted dependencies;
- prohibited dependencies when useful;
- invariants.

Only implement/document manifest fields that serve an immediate purpose.

---

## 14. ADR requirements

Capture foundational decisions established by this work. Likely subjects:

- clean-slate platform implementation;
- LangGraph as execution kernel;
- modular-monolith / ports-and-adapters architecture;
- Linux-container-only canonical runtime;
- CLI as a client rather than a business-logic layer;
- no speculative capability implementations.

Keep ADRs concise:

1. Context
2. Decision
3. Consequences
4. Alternatives considered

Do not write essays where a short record is enough.

---

## 15. Development method for Phase 1

Phase 1 uses **tight HITL peer-programming**, not broad autonomous multi-agent development, because it establishes contracts future agents will depend on.

Do not parallelize architectural decisions prematurely.

Work incrementally. After each meaningful implementation increment:

1. run relevant tests/static validation;
2. fix failures before proceeding;
3. keep the repository runnable;
4. avoid accumulating temporary architecture;
5. do not defer known correctness problems into TODOs.

Reasonable implementation decisions may be made without repeatedly asking for confirmation.

Pause for human input before making a materially different architectural decision from the supplied implementation guide.

Do not ask clarification merely because several reasonable details are possible. Choose the simplest design consistent with the specification and explain the decision.

---

## 16. Required quality standard

Phase 1 is complete only when the repository has:

- a clean container build;
- successful package import;
- functioning CLI;
- functioning `ss --help`;
- correct Phase-1-appropriate `ss doctor`;
- passing tests;
- passing strict type checking;
- passing linting;
- passing architecture/import checks;
- passing Python compilation;
- documentation build without errors;
- documented public APIs;
- no placeholder implementations;
- no TODO architecture;
- no legacy compatibility code;
- no application logic hidden in the CLI;
- no giant files;
- no circular architectural dependencies.

Where production Python exists, target comprehensive coverage. Do not write meaningless tests solely to inflate coverage.

---

## 17. Working style

For this foundational task:

- inspect before editing;
- make small coherent changes;
- run validation frequently;
- prefer simple, explicit designs;
- explain architectural decisions as they arise;
- do not silently broaden scope;
- do not rewrite large portions merely for aesthetics;
- do not add future functionality simply to demonstrate extensibility.

If the guide conflicts with verified current runtime/dependency behavior, explicitly identify and verify the incompatibility, then implement the smallest principled adjustment.

---

## 18. Final Phase 1 handoff

Provide a concise engineering report containing all of the following.

### 18.1 What changed

Repository/files/modules created and their responsibilities.

### 18.2 Architecture established

Important boundaries and invariants now enforced.

### 18.3 Public contracts

Any public interfaces future work will build against.

### 18.4 Validation

Exact results for:

- tests;
- coverage;
- lint;
- formatting;
- type checking;
- architecture checks;
- compile validation;
- documentation build;
- Docker build/runtime checks.

### 18.5 Deviations from the Technical Implementation Guide

List each deviation with rationale. If none, state that explicitly.

### 18.6 Known scope boundaries

List only things intentionally excluded from Phase 1 - not unfinished TODOs.

### 18.7 Repository map

Provide a concise resulting tree.

### 18.8 Next milestone

Define the exact Phase 2 task: **implement the immutable artifact foundation**.

Do not begin Phase 2 until Phase 1 has been reviewed.

---

## 19. Start condition

Begin implementation only after:

1. reading `technical-implementation-guide.md` completely;
2. inspecting the available environment;
3. verifying current runtime/dependency facts that materially affect Phase 1.

Then implement **Phase 0 + Phase 1 only**.
