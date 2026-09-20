# Simulated Singularity TTS Engine - Clean-Slate LangGraph Vertical Slice Technical Implementation Guide

**Status:** Normative agent-facing implementation specification  
**Source:** *Simulated Singularity TTS Engine - Clean-Slate LangGraph Vertical Slice Technical Implementation Guide* (September 2026)  
**Source PDF SHA-256:** `ccbbd67a72b9cd04abb446723da6ee6d187449fc7d1e164d8703a649e2645e1a`  
**Platform:** Simulated Singularity  
**Target runtime:** local NVIDIA GPU execution inside a Linux container  
**Initial capability:** long-form text-to-speech production  
**Execution model:** LangGraph-native artifact factory  
**Primary interface:** CLI  
**Future interfaces:** HTTP/API, autonomous agents, Google Cloud workers, rich web frontend

> This Markdown is an agent-first structural conversion of the source document. It preserves implementation-critical requirements, exact pins, invariants, topology, contracts, and acceptance criteria while removing PDF layout noise and repeated explanatory prose. If an ambiguity is discovered, compare against the source PDF and correct this Markdown rather than silently inventing behavior.

## 0. Scope and architectural endpoint

Implement the first complete production vertical slice of Simulated Singularity:

```text
Source text
  -> text planning
  -> pronunciation preparation
  -> utterance segmentation
  -> Qwen speech synthesis
  -> physical audio validation
  -> Whisper semantic validation
  -> bounded repair
  -> optional human review
  -> lossless assembly
  -> mastering
  -> WAV / FLAC / M4B artifacts
```

The slice must prove an architecture suitable for future simulation, story, speech, music, images, video, visualization, and multimodal composition **without implementing placeholder versions of future capabilities**.

Repository constraints:

- no legacy-state migration;
- no compatibility wrapper for the old renderer;
- no native-Windows inference implementation;
- no alternate CPU inference backend;
- no speculative music/video/simulation packages;
- no empty interfaces with TODOs;
- no fake microservices;
- no provider fallbacks.

Import the source manuscript and voice reference into the new platform as immutable artifacts. Regenerate the audiobook from zero.

> **Phase gate:** when this guide is paired with `phase-0-1.md`, that document constrains the current work to Phase 0 + Phase 1. Later sections remain architectural specification, not authorization to implement later phases early.

---

## 1. Core architectural principles

### 1.1 LangGraph owns orchestration

LangGraph defines resumable state-machine execution. It does **not** own:

- multimedia bytes;
- domain rules;
- model implementations;
- storage implementations;
- FFmpeg logic;
- Qwen internals;
- Whisper internals.

### 1.2 Artifacts are immutable

Every durable input/generated product is an artifact, for example:

- `TextArtifact`
- `VoiceReferenceArtifact`
- `SpokenTextPlanArtifact`
- `UtteranceAudioArtifact`
- `SemanticValidationArtifact`
- `ReviewDecisionArtifact`
- `MasterAudioArtifact`
- `AudiobookArtifact`

Artifacts are content-addressed and never modified. Any changed product creates a new artifact.

### 1.3 Graph state stores references, not multimedia

Graph state may contain:

- artifact IDs;
- utterance IDs;
- status values;
- attempt counts;
- validation summaries;
- review requests;
- provenance references.

Graph state must **not** contain:

- WAV bytes;
- model tensors;
- entire model weights;
- multi-gigabyte media.

### 1.4 Providers are replaceable implementations

Speech capability depends on provider-neutral contracts such as:

- `SpeechSynthesizer`
- `SpeechSemanticValidator` / `SemanticValidator`
- `AudioInspector`
- `AudioMasterer`
- `ArtifactRepository`

Qwen, Whisper, and FFmpeg implement those contracts. Speech graphs must not import provider internals directly.

### 1.5 Interfaces are clients

The CLI is not the application. Future clients must invoke the same application/graph contracts:

```text
CLI ----------------+
HTTP API ------------+
autonomous agent ----+--> application / graph contracts
Google Batch --------+
web frontend --------+
```

CLI code may format output but must not contain speech-production business logic.

### 1.6 State-machine differences justify graphs

Configuration differences do not justify new graphs.

Do not create provider-specific orchestration such as:

```text
QwenGraph
WhisperGraph
FfmpegGraph
```

Use a subgraph only when a component has its own multi-step state machine.

---

## 2. Required graph topology

Initially implement exactly three LangGraph definitions:

```text
ArtifactFactoryGraph
        |
        v
SpeechProductionGraph
        |
        +----> UtteranceProductionGraph instance
        +----> UtteranceProductionGraph instance
        +----> ...
```

There may be thousands of runtime utterance-graph instances, but only one `UtteranceProductionGraph` definition.

### 2.1 ArtifactFactoryGraph

Platform-level artifact-production root. It must not contain TTS algorithms.

```text
START
  -> validate_request
  -> resolve_capability
  -> dispatch_capability_graph
  -> register_outputs
  -> finalize_run
  -> END
```

Initial capability registry contains exactly:

```text
speech.production
```

Future capabilities can register implementations without changing the factory contract.

Input contract:

```python
class ArtifactProductionRequest(BaseModel):
    run_id: RunId
    capability_id: CapabilityId
    input_artifact_ids: tuple[ArtifactId, ...]
    configuration: dict[str, JsonValue]
```

Output contract:

```python
class ArtifactProductionResult(BaseModel):
    run_id: RunId
    status: RunStatus
    output_artifact_ids: tuple[ArtifactId, ...]
    provenance_record_id: ProvenanceId
```

### 2.2 SpeechProductionGraph

Audiobook-level state machine:

```text
START
  -> load_input_artifacts
  -> build_spoken_text_plan
  -> segment_text
  -> dispatch_utterances
  -> collect_utterance_results
  -> review_required?
       no ------------------------------+
       yes                              |
        -> interrupt_for_review         |
        -> apply_review_decisions       |
        -> regenerate_requested         |
        -> collect_utterance_results ---+
  -> verify_source_coverage
  -> assemble_lossless_master
  -> master_audio
  -> create_delivery_formats
  -> register_output_artifacts
  -> END
```

State uses `TypedDict`; state values use typed immutable models.

```python
class SpeechProductionState(TypedDict):
    run_id: RunId
    source_text_artifact_id: ArtifactId
    voice_artifact_id: ArtifactId
    spoken_text_plan_artifact_id: ArtifactId | None
    utterance_ids: tuple[UtteranceId, ...]
    completed_utterances: Annotated[
        tuple[UtteranceResult, ...],
        merge_utterance_results,
    ]
    review_item_ids: tuple[ReviewItemId, ...]
    master_artifact_id: ArtifactId | None
    output_artifact_ids: tuple[ArtifactId, ...]
    status: SpeechProductionStatus
```

Do not expose Qwen objects, Whisper objects, filesystem paths, or tensors through graph state.

### 2.3 UtteranceProductionGraph

Reusable work-unit state machine:

```text
START
  -> prepare_utterance
  -> check_execution_cache
       hit  -> finish
       miss -> synthesize_candidate
            -> physical_validation
            -> semantic_validation
            -> evaluate_candidate
                 accepted -> finish
                 retry_allowed
                    -> choose_next_strategy
                    -> synthesize_candidate
                 automated_budget_exhausted
                    -> build_review_candidate_set
                    -> finish
```

No user interaction occurs inside this graph. It returns either `ACCEPTED` or `REVIEW_REQUIRED` to the parent speech graph.

---

## 3. Review architecture

Human review belongs at speech-production orchestration level because review may span many utterances.

Interrupt contract:

```python
class SpeechReviewRequest(BaseModel):
    run_id: RunId
    items: tuple[ReviewItem, ...]
```

Each review item must contain exactly two distinct playable candidates:

```python
class ReviewItem(BaseModel):
    review_item_id: ReviewItemId
    utterance_id: UtteranceId
    expected_text: str
    candidate_a_artifact_id: ArtifactId
    candidate_b_artifact_id: ArtifactId
    evidence_artifact_ids: tuple[ArtifactId, ...]
```

Invariant:

```text
candidate_a.sha256 != candidate_b.sha256
```

Review decisions:

```python
class ReviewDecisionType(StrEnum):
    ACCEPT_A = "accept_a"
    ACCEPT_B = "accept_b"
    REGENERATE = "regenerate"
```

A review decision becomes an immutable artifact/provenance record.

`REGENERATE` creates a new utterance attempt sequence; never overwrite candidate A/B.

Keep expensive generation outside the graph node whose sole purpose is waiting for review.

---

## 4. Speech quality invariants

### 4.1 Source coverage

Every speakable source span must map to exactly one final accepted audio contribution.

Final assembly fails closed unless:

```text
speech_source_coverage == 100%
```

Semantic uncertainty must never cause playable speech to disappear. If no valid playable artifact can be produced for a required utterance, fail the run explicitly rather than silently omitting content.

### 4.2 Physical and semantic validity are separate

Physical validation checks properties such as:

- nonempty audio;
- expected channel count;
- valid duration;
- finite samples;
- valid waveform;
- not effectively silent;
- not corrupted;
- not unexpectedly truncated.

Semantic validation asks whether audio represents the expected utterance.

Do not collapse both into one boolean.

### 4.3 Preserve source text separately from synthesis text

```python
class UtterancePlan(BaseModel):
    utterance_id: UtteranceId
    source_text: str
    synthesis_text: str
    source_start_offset: int
    source_end_offset: int
    pause_before_ms: int
    pause_after_ms: int
```

This preserves invented terms and pronunciation transformations.

Whisper validation must evaluate against both canonical source text and pronunciation-expanded synthesis text and preserve evidence used for classification.

### 4.4 Short-utterance policy

Do not rely on WER alone for one-word/very short invented utterances.

Validator evidence should include:

- transcript;
- normalized transcript;
- word-level similarity;
- character-level similarity;
- duration;
- no-speech probability/evidence;
- candidate score;
- decision reason.

The validator produces evidence. A separate policy chooses `ACCEPT`, `RETRY`, or `REVIEW`. Whisper-specific assumptions must not leak through the architecture.

---

## 5. Deterministic retry and execution identity

Generation may remain stochastic while execution remains reproducible.

Each run receives a root seed. Derive utterance-attempt seed deterministically:

```text
seed = hash(
  run_seed,
  utterance_id,
  attempt_number,
  synthesis_strategy
)
```

Build execution key:

```text
execution_key = SHA256(
  capability_id
  + capability_version
  + provider_version
  + model_revision
  + input_artifact_ids
  + canonical_configuration
  + random_seed
)
```

If an execution key already produced an artifact, return it. Restarting must not accidentally create a new candidate for the same logical attempt.

`REGENERATE` intentionally increments attempt generation and therefore yields a different seed.

---

## 6. Repair policy

Repair is a domain policy, not nested graph-node conditionals.

```python
class UtteranceRepairPolicy:
    """Selects the next bounded synthesis action from validation evidence."""
```

Use a finite attempt budget. Initial production policy:

| Attempt class | Maximum |
|---|---:|
| Initial candidate | 1 |
| Normal repair candidates | 4 |
| Contextual repair candidates | 3 |
| **Maximum automatic attempts** | **8** |

Canonical policy key: `maximum_automatic_attempts: 8`.

Exact values belong in versioned `SpeechProductionPolicy`, not magic constants.

When budget is exhausted:

```text
two playable distinct candidates
  -> REVIEW_REQUIRED

fewer than two playable candidates
  -> bounded alternate-candidate generation
  -> if still fewer than two: explicit production failure
```

No unbounded repair loops.

---

## 7. Repository/package structure

Package name:

```text
simulated_singularity
```

Do not name the platform package `simulated_singularity_tts`.

Target structure:

```text
simulated-singularity/
├── Dockerfile
├── compose.yaml
├── pyproject.toml
├── requirements.in
├── requirements.lock
├── models.lock.yaml
├── README.md
├── ARCHITECTURE.md
├── CONTRIBUTING.md
├── docs/
│   ├── index.md
│   ├── architecture/
│   ├── reference/
│   └── adr/
│       ├── 0001-clean-slate-platform.md
│       ├── 0002-langgraph-execution-kernel.md
│       ├── 0003-immutable-artifacts.md
│       └── 0004-speech-vertical-slice.md
├── src/simulated_singularity/
│   ├── factory/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── contracts.py
│   │   ├── registry.py
│   │   └── module.yaml
│   ├── platform/
│   │   ├── artifacts/
│   │   │   ├── models.py
│   │   │   ├── repository.py
│   │   │   ├── content_addressing.py
│   │   │   └── provenance.py
│   │   ├── execution/
│   │   │   ├── execution_key.py
│   │   │   ├── context.py
│   │   │   └── events.py
│   │   ├── identifiers/models.py
│   │   └── errors/models.py
│   ├── capabilities/speech/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── contracts.py
│   │   ├── module.yaml
│   │   ├── utterance/
│   │   │   ├── graph.py
│   │   │   ├── state.py
│   │   │   └── nodes/
│   │   ├── domain/
│   │   │   ├── utterance.py
│   │   │   ├── candidate.py
│   │   │   ├── validation.py
│   │   │   ├── review.py
│   │   │   └── policies.py
│   │   ├── application/
│   │   │   ├── spoken_text_planner.py
│   │   │   ├── segmenter.py
│   │   │   ├── coverage_verifier.py
│   │   │   └── assembler.py
│   │   └── ports/
│   │       ├── speech_synthesizer.py
│   │       ├── semantic_validator.py
│   │       ├── audio_inspector.py
│   │       └── audio_masterer.py
│   ├── providers/
│   │   ├── qwen/synthesizer.py
│   │   ├── whisper/semantic_validator.py
│   │   └── ffmpeg/
│   │       ├── inspector.py
│   │       ├── assembler.py
│   │       └── masterer.py
│   ├── infrastructure/
│   │   ├── artifacts/filesystem_repository.py
│   │   ├── metadata/sqlite_repository.py
│   │   └── langgraph/sqlite_checkpointer.py
│   └── interfaces/cli/
│       ├── app.py
│       ├── doctor.py
│       ├── models.py
│       ├── speech.py
│       ├── runs.py
│       ├── review.py
│       └── artifacts.py
└── tests/
    ├── unit/
    ├── contract/
    ├── integration/
    ├── gpu/
    └── system/
```

Do not create future modality directories until a complete vertical capability is implemented.

> When operating under `phase-0-1.md`, create only the minimal subset required for the foundation. Do not pre-create later-phase packages as empty placeholders.

---

## 8. Public contracts and dependency direction

Ports must be small and capability-oriented. Example contracts:

```python
class SpeechSynthesizer(Protocol):
    """Produces a candidate speech artifact from a synthesis request."""

    def synthesize(
        self,
        request: SpeechSynthesisRequest,
        context: ExecutionContext,
    ) -> SpeechSynthesisResult:
        ...


class SemanticValidator(Protocol):
    """Produces semantic evidence for a speech candidate."""

    def validate(
        self,
        request: SemanticValidationRequest,
        context: ExecutionContext,
    ) -> SemanticValidationResult:
        ...


class ArtifactRepository(Protocol):
    """Stores and retrieves immutable content-addressed artifacts."""

    def put(self, artifact: ArtifactPayload) -> ArtifactRecord: ...
    def get(self, artifact_id: ArtifactId) -> ArtifactPayload: ...
    def exists(self, artifact_id: ArtifactId) -> bool: ...
```

Avoid provider names in public contracts.

Bad:

```text
QwenService
WhisperChecker
FFmpegAudioThing
```

Good:

```text
SpeechSynthesizer
SemanticValidator
AudioMasterer
AudioInspector
```

Required dependency direction:

```text
interfaces
   |
   v
graphs / application
   |
   v
domain
   |
   v
ports
   ^
   |
providers / infrastructure implement ports
```

Forbidden dependencies include:

```text
domain -> qwen
domain -> whisper
domain -> ffmpeg
domain -> typer
domain -> sqlite
domain -> filesystem
domain -> google cloud
```

Add import-linter rules so violations fail CI/tests.

---

## 9. Artifact model and provenance

### 9.1 Generic immutable artifact record

Use one generic immutable record with typed media metadata rather than a deep inheritance tree.

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

Content layout:

```text
/workspace/artifacts/sha256/38/38fc7f...
```

Writes must be atomic:

```text
write temporary file
-> fsync
-> verify SHA-256
-> atomic rename
-> register metadata
```

Never mutate an existing content-addressed payload.

### 9.2 Provenance

Every generated artifact records:

- capability ID;
- capability version;
- provider ID;
- provider version;
- model identity;
- model revision;
- container/application version;
- input artifact IDs;
- canonical configuration hash;
- execution key;
- random seed where applicable;
- creation time.

Example:

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

---

## 10. Persistence model

Keep three persistence concerns independent.

### 10.1 LangGraph checkpoints

```text
/workspace/state/langgraph.sqlite3
```

Use `langgraph-checkpoint-sqlite` for local development.

Set:

```text
LANGGRAPH_STRICT_MSGPACK=true
```

Future migration should allow:

```text
SqliteSaver -> PostgresSaver
```

without changing graph definitions.

### 10.2 Platform metadata

```text
/workspace/state/platform.sqlite3
```

Stores:

- artifact records;
- run records;
- provenance records;
- review records;
- execution-cache mappings.

Do not mix platform metadata tables into LangGraph checkpoint schema.

### 10.3 Artifact filesystem

```text
/workspace/artifacts/
```

Stores immutable media/data payloads.

---

## 11. Typed events

Graph logs are not an API. Emit structured events, e.g.:

```python
class UtteranceSynthesisStarted(DomainEvent):
    run_id: RunId
    utterance_id: UtteranceId
    attempt_number: int


class ReviewRequired(DomainEvent):
    run_id: RunId
    review_item_ids: tuple[ReviewItemId, ...]
```

Local sinks:

- `ConsoleEventSink`
- `JsonlEventSink`

Future cloud sink:

- `PubSubEventSink`

Events should drive CLI status and future real-time frontends.

---

## 12. Documentation and agent-first repository rules

### 12.1 Public documentation

All public classes, functions, protocols, graph states, and domain models require complete docstrings covering:

- purpose;
- responsibilities;
- non-responsibilities where useful;
- inputs;
- outputs;
- important invariants;
- failure behavior.

Generate documentation with:

- MkDocs;
- mkdocstrings.

Documentation outputs should cover:

- Python API reference;
- CLI reference;
- architecture documentation;
- ADRs;
- graph diagrams;
- schema documentation.

### 12.2 `module.yaml`

Each implemented bounded module receives a `module.yaml` describing:

- purpose;
- public API;
- owned concepts;
- permitted dependencies;
- invariants.

Example semantic shape:

```yaml
name: speech
purpose: >
  Produce complete validated long-form speech artifacts.
public_api:
  - SpeechProductionGraph
  - SpeechProductionRequest
  - SpeechProductionResult
owns:
  - spoken text planning
  - utterance segmentation
  - synthesis orchestration
  - speech semantic QA policy
  - review workflow
  - source coverage validation
depends_on:
  - platform.artifacts
  - SpeechSynthesizer
  - SemanticValidator
  - AudioMasterer
invariants:
  - source speech coverage is 100 percent
  - semantic uncertainty alone never removes playable speech
  - review always presents two distinct playable candidates
  - human-selected audio is terminal for that decision
```

Agent rule:

```text
Modify implementation internals freely.
Do not change exported contracts without an ADR.
Do not import across forbidden boundaries.
Do not create placeholder APIs.
```

### 12.3 File-size discipline

| Size | Guidance |
|---|---|
| `<300 LOC` | ordinary |
| `300-500` | inspect responsibility |
| `500-800` | likely decomposition candidate |
| `>800` | architecture review required |

Graph files should mostly describe topology. If `graph.py` contains audio decoding, text normalization, model inference, similarity calculations, or filesystem writes, boundaries are wrong.

---

## 13. Canonical runtime and container

Supported application environment:

```text
linux/amd64
NVIDIA CUDA
Python 3.12
```

For current Windows/NVIDIA development, use Docker Desktop WSL2 backend. WSL2 is host machinery; the application runtime remains one Linux container.

### 13.1 Canonical GPU software stack

Pin initial environment to:

| Component | Version |
|---|---|
| Ubuntu | 24.04 |
| Python | 3.12 |
| CUDA userspace | 13.0 |
| PyTorch | 2.14.0 + cu130 |
| Qwen TTS package | 0.1.1 |
| LangGraph | 1.2.11 |
| LangGraph SQLite | 3.1.1 |
| Pydantic | 2.13.5 |
| Typer | 0.27.2 |
| OpenAI Whisper | 20250625 |
| FFmpeg | Ubuntu package, image-pinned |

Use PyTorch SDPA as canonical attention implementation initially. Do not create FlashAttention as a second runtime branch.

> Before pinning versions during implementation, verify current authoritative availability/compatibility when required by `phase-0-1.md`.

### 13.2 Base container

Base image:

```text
nvidia/cuda:13.0.3-cudnn-runtime-ubuntu24.04
```

Canonical Dockerfile intent:

```dockerfile
FROM nvidia/cuda:13.0.3-cudnn-runtime-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LANGGRAPH_STRICT_MSGPACK=true
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3.12 \
        python3.12-venv \
        python3-pip \
        ffmpeg \
        git \
        ca-certificates \
        libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN python3.12 -m venv /opt/venv \
    && pip install --upgrade pip

WORKDIR /app
COPY requirements.lock /app/requirements.lock

RUN pip install \
    --index-url https://download.pytorch.org/whl/cu130 \
    torch==2.14.0

RUN pip install -r /app/requirements.lock

COPY pyproject.toml README.md /app/
COPY src /app/src
RUN pip install --no-deps /app

RUN useradd --create-home --uid 10001 simulated-singularity
RUN mkdir -p /workspace /models \
    && chown -R simulated-singularity:simulated-singularity /workspace /models

USER simulated-singularity
CMD ["ss", "--help"]
```

Lockfile must constrain PyTorch to `2.14.0`; package installation must not replace it. FFmpeg belongs inside the image, not on host.

---

## 14. Dependency and model locking

### 14.1 Python dependency locking

Maintain:

```text
requirements.in
requirements.lock
```

`requirements.in` contains intentional top-level dependencies. `requirements.lock` pins every transitive dependency.

Do not install `latest` during runtime.

Build process should:

```text
resolve dependencies
-> generate lock
-> build image
-> run complete suite
-> record image digest
```

Committed lockfile is execution authority.

### 14.2 Model locking

Maintain:

```text
models.lock.yaml
```

Qwen model:

```text
Qwen/Qwen3-TTS-12Hz-1.7B-Base
revision: fd4b254389122332181a7c3db7f27e918eec64e3
```

Known hashes:

```text
main model:
38fc7fc51c5e776e840414b6fd443962e9411b9654888fd7913e4da643cb857c

speech tokenizer:
836b7b357f5ea43e889936a3709af68dfe3751881acefe4ecf0dbd30ba571258
```

Whisper:

```text
model: small.en
SHA256: f953ad0fd29cacd07d5a9eda5624af0f6bcf2258be67c92b79389873d91e0872
```

Implement:

```text
ss models sync
ss models verify
```

`sync` downloads missing locked models. `verify` checks every model before inference.

After synchronization, production-quality local tests should succeed with network disabled.

---

## 15. Compose and host setup

Canonical compose intent:

```yaml
services:
  engine:
    build:
      context: .
    image: simulated-singularity:dev
    gpus: all
    environment:
      SSTTS_WORKSPACE: /workspace
      SSTTS_MODEL_ROOT: /models
      HF_HOME: /models/huggingface
      LANGGRAPH_STRICT_MSGPACK: "true"
    volumes:
      - ./workspace:/workspace
      - simulated_singularity_models:/models

volumes:
  simulated_singularity_models:
```

Mount only persistent data:

- application stays in container;
- model volume stores verified model data;
- workspace stores project/user artifacts and persistent state.

Windows host:

```text
wsl --update
```

Use Docker Desktop with WSL2 backend, Linux containers, GPU support.

GPU validation:

```bash
docker run --rm --gpus all \
  nvidia/cuda:13.0.3-base-ubuntu24.04 \
  nvidia-smi
```

Direct Linux workstation deployment should use the exact same container. Host deployment differences are not application fallbacks.

---

## 16. CLI contract

CLI executable:

```text
ss
```

Initial command surface:

```text
ss doctor
ss models sync
ss models verify
ss speech render
ss speech review
ss run status
ss run resume
ss run events
ss artifact inspect
ss artifact export
ss graph mermaid
ss test
```

Every informational command supports `--json`.

Example:

```bash
docker compose run --rm engine \
  ss speech render \
  --text /workspace/inputs/I_Am_Here.txt \
  --voice /workspace/inputs/narrator.wav \
  --config /workspace/config/I_Am_Here.yaml
```

Human output example:

```text
Run created: 01K...
Status: RUNNING
```

Machine-readable callers use structured JSON, e.g.:

```text
ss run status 01K... --json
```

No caller should need to parse console prose.

---

## 17. `ss doctor`

`doctor` is a first-class deployment validation command.

It must verify, once those components exist:

- Linux runtime;
- x86-64 architecture;
- Python version;
- PyTorch version;
- CUDA runtime;
- `torch.cuda.is_available()`;
- GPU identity;
- GPU memory;
- Qwen import;
- Whisper import;
- FFmpeg;
- model presence;
- model hashes;
- workspace read/write;
- atomic artifact writes;
- SQLite metadata DB;
- LangGraph checkpoint DB.

`ss doctor --deep` additionally performs:

- one Qwen synthesis;
- one Whisper transcription;
- one FFmpeg probe;
- one artifact write/read;
- one LangGraph checkpoint/resume cycle.

No degraded mode. Failure of a required subsystem means doctor failed.

> Under Phase 1, `ss doctor` must report only on components that actually exist; do not pretend Qwen/Whisper/providers are implemented.

---

## 18. Source import and segmentation

Import source transcript as immutable UTF-8 artifact and preserve:

- exact bytes;
- line boundaries;
- paragraph boundaries;
- character offsets.

Segmentation creates explicit source mapping.

Stable utterance ID derives from:

```text
source artifact ID
+ source start offset
+ source end offset
+ normalized utterance identity
```

Represent blank-line/paragraph structure as timing semantics rather than discarding it; this is especially important for poetic material.

---

## 19. Provider requirements

### 19.1 Qwen speech provider

Implement:

```python
class QwenSpeechSynthesizer(SpeechSynthesizer):
    ...
```

Owns:

- model loading;
- voice prompt preparation;
- GPU tensor handling;
- generation parameters;
- seed control;
- native audio extraction;
- model-specific errors.

Does not own:

- retry policy;
- semantic QA thresholds;
- review policy;
- artifact assembly;
- CLI output.

Preserve model-native sample rate for generated utterance artifacts unless resampling is actually required.

Provider lifecycle:

```text
container process
  -> load Qwen once
  -> reuse model across utterances
  -> release on process shutdown
```

Do not reload model per graph node. Inject a process-scoped provider instance through graph runtime context.

### 19.2 Whisper semantic validator

Implement:

```python
class WhisperSemanticValidator(SemanticValidator):
    ...
```

Use:

```text
openai/whisper-small.en
```

For `.en` models, do not force multilingual language/task behavior.

Provider emits evidence; it does not decide whether audio is discarded.

Cache validation by:

```text
audio artifact ID
+ validator version
+ model hash
+ validation configuration hash
```

Identical audio must not be retranscribed unnecessarily.

### 19.3 FFmpeg providers

Separate responsibilities:

```text
FfmpegAudioInspector
FfmpegAssembler
FfmpegMasterer
FfmpegDeliveryEncoder
```

Do not create one giant FFmpeg service.

Assembly first creates a lossless master, then derives:

```text
lossless master
  +-> WAV
  +-> FLAC
  +-> M4B
```

WAV/FLAC remain lossless derivatives. M4B is listening/distribution convenience.

Mastering parameters belong in a named, versioned model such as:

```python
class NarrationMasteringProfileV1(BaseModel):
    ...
```

Do not hide loudness parameters inside command strings.

---

## 20. Application configuration

Use one validated YAML/JSON schema.

Example:

```yaml
schema_version: 1
speech:
  provider: qwen3_tts
  model: Qwen/Qwen3-TTS-12Hz-1.7B-Base
generation:
  temperature: 0.9
  top_p: 1.0
  top_k: 50
validation:
  provider: whisper
  model: small.en
repair:
  maximum_automatic_attempts: 8
  minimum_review_candidates: 2
mastering:
  profile: narration_v1
delivery:
  wav: true
  flac: true
  m4b: true
```

Validate complete configuration before expensive work. Canonicalize and hash it. Configuration hash participates in execution identity.

---

## 21. Status and error models

### 21.1 Stable run statuses

```text
CREATED
RUNNING
AWAITING_REVIEW
COMPLETE
FAILED
CANCELED
```

Speech-local states may additionally include:

```text
PLANNING
SYNTHESIZING
VALIDATING
REPAIRING
ASSEMBLING
MASTERING
```

Do not derive status by parsing logs.

### 21.2 Structured errors

Examples:

- `ConfigurationError`
- `ArtifactIntegrityError`
- `ModelIntegrityError`
- `SpeechSynthesisError`
- `PhysicalAudioValidationError`
- `InsufficientReviewCandidatesError`
- `SourceCoverageError`
- `MasteringError`
- `CheckpointError`

Each error includes:

- error code;
- human message;
- run ID;
- relevant artifact/entity IDs;
- retry classification;
- underlying provider information.

Avoid `except Exception: continue` behavior. No failure may silently remove source content.

---

## 22. Testing strategy

Tests mirror architecture.

```text
tests/unit/
  domain policies
  segmentation
  identifiers
  execution keys
  coverage
  review logic

tests/contract/
  ArtifactRepository contract
  SpeechSynthesizer contract
  SemanticValidator contract
  event sink contract

tests/integration/
  SQLite persistence
  LangGraph checkpoint/resume
  FFmpeg
  artifact repository

tests/gpu/
  Qwen load
  Qwen short synthesis
  Whisper transcription
  sequential Qwen/Whisper GPU lifecycle

tests/system/
  full miniature audiobook
  interruption/resume
  review cycle
  final artifact creation
```

Use fake deterministic providers for ordinary graph/system tests. Use real GPU providers only in GPU integration tests. Graph behavior must remain testable without loading multi-gigabyte models for every test.

---

## 23. Release quality gate

Release gate includes:

```text
ruff check
format check
mypy --strict
import-linter
pytest
100% line coverage for production Python
compileall
documentation build
container build
ss doctor --deep
GPU synthesis smoke
Whisper semantic-QA smoke
FFmpeg assembly smoke
checkpoint/resume system test
HITL review system test
```

GPU-dependent provider code still needs unit coverage through injected lower-level interfaces/mocks plus real GPU integration tests.

Do not leave uncovered exception branches merely because they are inconvenient.

---

## 24. Graph visualization

Implement:

```text
ss graph mermaid artifact-factory
ss graph mermaid speech
ss graph mermaid utterance
```

Commands emit current compiled topology. Visualization is both documentation and an agent-development aid.

---

## 25. First system fixture

Create a small deterministic integration manuscript containing:

- ordinary sentence;
- short sentence;
- single invented token;
- hyphenated invented token;
- paragraph break;
- question.

Use it to exercise:

- segmentation;
- pronunciation mapping;
- synthesis;
- validation;
- retry;
- review;
- assembly;
- mastering;
- checkpoint/resume.

The large `I_Am_Here` manuscript is the real acceptance workload, not the smallest fixture.

---

## 26. `I Am Here` acceptance run

After lower-level gates pass:

```bash
docker compose run --rm engine ss models verify
```

Then:

```bash
docker compose run --rm engine \
  ss speech render \
  --text /workspace/inputs/I_Am_Here/I_Am_Here.txt \
  --voice /workspace/voices/synthetic_02_subharmonic_entity_RAW.wav \
  --config /workspace/inputs/I_Am_Here/config.yaml
```

System must support interruption at any point.

Resume:

```bash
docker compose run --rm engine ss run resume RUN_ID
```

Review:

```bash
docker compose run --rm engine ss speech review RUN_ID
```

Status:

```bash
docker compose run --rm engine ss run status RUN_ID
```

Completion requires:

- `status = COMPLETE`;
- source coverage = 100%;
- every utterance has accepted audio;
- all artifact hashes verify;
- master WAV exists;
- master FLAC exists;
- chapterized M4B exists;
- provenance is complete;
- run can be reconstructed from persistent state.

---

## 27. Implementation order

Build in this order. Every merged stage must be complete and tested. Do not merge placeholder future architecture.

1. **Foundation** - clean repository, packaging, Linux container, strict typing/linting, documentation generation, module manifests, architecture enforcement.
2. **Artifacts** - identifiers, immutable records, filesystem content-addressed storage, metadata SQLite, provenance, atomic writes, contract tests.
3. **Execution** - execution keys, typed events, LangGraph SQLite persistence, run identity, checkpoint/resume, `ArtifactFactoryGraph`.
4. **Speech domain** - source text model, spoken-text plan, segmentation, utterance identity, source coverage, validation evidence, candidates, repair policy, review models.
5. **Providers** - Qwen, Whisper, FFmpeg behind ports, independently tested.
6. **Utterance graph** - bounded synthesis -> validation -> repair -> review-candidate lifecycle.
7. **Speech graph** - dynamic fan-out, aggregation, review interrupt/resume, coverage verification, assembly, mastering, delivery artifacts.
8. **CLI** - doctor, models, speech render, run inspection/resume, review, artifacts, JSON output, graph visualization.
9. **Hardening** - GPU/system tests, network-disabled execution after model prep, docs build, architectural linting, 100% coverage.
10. **Acceptance** - regenerate complete audiobook from source transcript and voice reference.

When paired with `phase-0-1.md`, only Step 1 is authorized during the current milestone.

---

## 28. Definition of done for the vertical slice

A clean machine with supported NVIDIA GPU can:

1. install Docker GPU runtime;
2. clone repository;
3. build container;
4. sync locked models;
5. pass `ss doctor --deep`;
6. import source + voice;
7. start audiobook production;
8. stop container;
9. resume production;
10. complete automated repair;
11. pause for bounded HITL where necessary;
12. resume after review;
13. produce WAV / FLAC / M4B;
14. verify 100% source coverage;
15. inspect full provenance;
16. rerun without recomputing cached work;
17. run with network disabled after models are cached;
18. pass complete release test suite.

At that point TTS is the first complete capability on the Simulated Singularity artifact-production framework, not a standalone special-case application.

Future modalities should add complete capability graphs/providers without changing platform fundamentals.

---

## 29. Final architectural shape

```text
CLI
 |
 v
ArtifactFactoryGraph
 |
 v
SpeechProductionGraph
 |
 dynamic LangGraph fan-out
 +-------------+-------------+
 v             v             v
Utterance    Utterance     Utterance
Graph        Graph         Graph
 |             |             |
 +-- SpeechSynthesizer --- Qwen
 +-- SemanticValidator --- Whisper
 +-- Audio capabilities -- FFmpeg
 |
 v
immutable artifacts
 |
 v
content-address store
 |
 v
lossless assembly
 |
 v
mastering
 |
 +----+-----+
 v    v     v
WAV  FLAC  M4B
```

Persistent execution:

```text
LangGraph
  -> execution/checkpoint state

Platform SQLite
  -> metadata/provenance/review/cache mappings

Artifact repository
  -> immutable source/generated media

Model volume
  -> verified pinned model snapshots
```

Future expansion:

```text
SimulationGraph
  +-- requests speech artifact
  +-- requests image artifact
  +-- requests music artifact
  +-- requests video artifact
  |
  v
ArtifactFactoryGraph
```

Simulation architecture and artifact architecture remain complementary rather than entangled.

**LangGraph is the orchestration substrate.**  
**Artifacts are the durable products.**  
**Capabilities define what can be done.**  
**Providers define how it is done.**  
**The CLI is only the first client.**
