from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from typing import Any

import pytest

from simulated_singularity.platform.artifacts import ProvenanceRecord
from simulated_singularity.platform.identifiers import (
    ArtifactId,
    CapabilityId,
    ExecutionKey,
    ProvenanceId,
)

NOW = datetime(2026, 9, 20, 12, tzinfo=UTC)
INPUT_ID = ArtifactId("a" * 64)


def make_provenance(**changes: Any) -> ProvenanceRecord:
    values: dict[str, Any] = {
        "provenance_id": ProvenanceId("provenance-1"),
        "capability_id": CapabilityId("document.import"),
        "capability_version": "1.0.0",
        "provider_id": "built-in",
        "provider_version": "1.0.0",
        "model_id": None,
        "model_revision": None,
        "application_version": "0.1.0",
        "container_version": None,
        "input_artifact_ids": (INPUT_ID,),
        "configuration_sha256": "b" * 64,
        "execution_key": ExecutionKey("phase-3-owned-key"),
        "random_seed": None,
        "created_at": NOW,
    }
    values.update(changes)
    return ProvenanceRecord(**values)


def test_provenance_preserves_ordered_inputs_and_optional_reproducibility_fields() -> None:
    second_id = ArtifactId("c" * 64)
    record = make_provenance(
        model_id="model",
        model_revision="revision",
        container_version="image@sha256:digest",
        input_artifact_ids=(INPUT_ID, second_id, INPUT_ID),
        random_seed=0,
    )
    assert record.input_artifact_ids == (INPUT_ID, second_id, INPUT_ID)
    assert record.execution_key == ExecutionKey("phase-3-owned-key")
    assert record.random_seed == 0
    with pytest.raises(FrozenInstanceError):
        record.__setattr__("provider_id", "changed")


@pytest.mark.parametrize(
    "changes",
    [
        {"provenance_id": "provenance-1"},
        {"capability_id": "document.import"},
        {"execution_key": "phase-3-owned-key"},
    ],
)
def test_provenance_requires_nominal_identifier_types(changes: dict[str, Any]) -> None:
    with pytest.raises(TypeError):
        make_provenance(**changes)


@pytest.mark.parametrize(
    "changes",
    [
        {"capability_version": ""},
        {"provider_id": " padded"},
        {"provider_version": 1},
        {"application_version": ""},
        {"model_id": ""},
        {"model_revision": " "},
        {"container_version": ""},
    ],
)
def test_provenance_rejects_invalid_version_and_identity_text(changes: dict[str, Any]) -> None:
    with pytest.raises((TypeError, ValueError)):
        make_provenance(**changes)


def test_model_revision_requires_model_identity() -> None:
    with pytest.raises(ValueError, match="model_revision requires model_id"):
        make_provenance(model_revision="revision")


@pytest.mark.parametrize("value", [[], [INPUT_ID], ("not-an-artifact-id",)])
def test_input_artifacts_require_an_immutable_typed_tuple(value: Any) -> None:
    with pytest.raises(TypeError, match="input_artifact_ids"):
        make_provenance(input_artifact_ids=value)


@pytest.mark.parametrize("value", ["short", "B" * 64])
def test_configuration_hash_must_be_canonical_sha256(value: str) -> None:
    with pytest.raises(ValueError):
        make_provenance(configuration_sha256=value)


@pytest.mark.parametrize("value", [True, 1.5, "1"])
def test_random_seed_must_be_an_integer_or_none(value: Any) -> None:
    with pytest.raises(TypeError, match="random_seed"):
        make_provenance(random_seed=value)


def test_provenance_requires_timezone_aware_creation_time() -> None:
    with pytest.raises(ValueError, match="UTC offset"):
        make_provenance(created_at=datetime(2026, 9, 20))
