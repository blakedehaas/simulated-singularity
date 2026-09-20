from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from typing import Any

import pytest

from simulated_singularity.platform.artifacts import ArtifactPayload, ArtifactRecord, ArtifactType
from simulated_singularity.platform.identifiers import ArtifactId, ProvenanceId

NOW = datetime(2026, 9, 20, 12, tzinfo=UTC)
PROVENANCE_ID = ProvenanceId("provenance-1")
ARTIFACT_TYPE = ArtifactType("document.source")


def make_payload(**changes: Any) -> ArtifactPayload:
    values: dict[str, Any] = {
        "content": b"immutable bytes",
        "artifact_type": ARTIFACT_TYPE,
        "media_type": "text/plain",
        "created_at": NOW,
        "provenance_id": PROVENANCE_ID,
        "metadata": {"language": "en", "pages": [1, 2], "nested": {"ok": True}},
    }
    values.update(changes)
    return ArtifactPayload(**values)


def test_artifact_type_has_stable_serialization_and_validation() -> None:
    artifact_type = ArtifactType.parse("document.source")
    assert artifact_type.serialize() == "document.source"
    assert str(artifact_type) == "document.source"
    with pytest.raises(ValueError):
        ArtifactType(" padded")
    with pytest.raises(TypeError):
        ArtifactType(1)  # type: ignore[arg-type]


def test_payload_and_metadata_are_deeply_immutable() -> None:
    source_metadata = {"items": [1, {"label": "original"}], "ratio": 1.5, "missing": None}
    payload = make_payload(metadata=source_metadata)
    source_metadata["items"] = []
    assert payload.metadata["items"] == (1, {"label": "original"})
    assert payload.metadata["ratio"] == 1.5
    with pytest.raises(FrozenInstanceError):
        payload.__setattr__("content", b"changed")
    with pytest.raises(TypeError):
        payload.metadata["new"] = "value"  # type: ignore[index]
    nested = payload.metadata["items"]
    assert isinstance(nested, tuple)
    assert isinstance(nested[1], dict) is False
    with pytest.raises(TypeError):
        nested[1]["label"] = "changed"


def test_record_from_payload_derives_all_content_facts() -> None:
    payload = make_payload()
    record = ArtifactRecord.from_payload(payload)
    assert record.artifact_id.value == record.content_sha256
    assert record.byte_length == len(payload.content)
    assert record.artifact_type == payload.artifact_type
    assert record.media_type == payload.media_type
    assert record.created_at == payload.created_at
    assert record.provenance_id == payload.provenance_id
    assert record.metadata == payload.metadata
    with pytest.raises(FrozenInstanceError):
        record.__setattr__("byte_length", 0)


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"content": bytearray(b"mutable")}, TypeError),
        ({"artifact_type": "document.source"}, TypeError),
        ({"provenance_id": "provenance-1"}, TypeError),
        ({"media_type": ""}, ValueError),
        ({"media_type": 3}, TypeError),
        ({"created_at": datetime(2026, 1, 1)}, ValueError),
        ({"created_at": "today"}, TypeError),
        ({"metadata": {1: "value"}}, TypeError),
        ({"metadata": {"bad": float("nan")}}, ValueError),
        ({"metadata": {"bad": float("inf")}}, ValueError),
        ({"metadata": {"bad": object()}}, TypeError),
        ({"metadata": "not-a-mapping"}, TypeError),
    ],
)
def test_payload_rejects_invalid_values(changes: dict[str, Any], error: type[Exception]) -> None:
    with pytest.raises(error):
        make_payload(**changes)


def test_record_rejects_inconsistent_identity() -> None:
    payload = make_payload()
    record = ArtifactRecord.from_payload(payload)
    with pytest.raises(ValueError, match="artifact_id"):
        ArtifactRecord(
            artifact_id=ArtifactId("0" * 64),
            artifact_type=record.artifact_type,
            content_sha256=record.content_sha256,
            byte_length=record.byte_length,
            media_type=record.media_type,
            created_at=record.created_at,
            provenance_id=record.provenance_id,
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"artifact_id": "0" * 64},
        {"artifact_type": "document.source"},
        {"provenance_id": "provenance-1"},
    ],
)
def test_record_rejects_untyped_identity_fields(changes: dict[str, Any]) -> None:
    record = ArtifactRecord.from_payload(make_payload())
    values: dict[str, Any] = {
        "artifact_id": record.artifact_id,
        "artifact_type": record.artifact_type,
        "content_sha256": record.content_sha256,
        "byte_length": record.byte_length,
        "media_type": record.media_type,
        "created_at": record.created_at,
        "provenance_id": record.provenance_id,
    }
    values.update(changes)
    with pytest.raises(TypeError):
        ArtifactRecord(**values)


@pytest.mark.parametrize(
    ("byte_length", "error"),
    [(-1, ValueError), (True, TypeError), (1.5, TypeError)],
)
def test_record_rejects_invalid_byte_length(byte_length: Any, error: type[Exception]) -> None:
    payload = make_payload()
    record = ArtifactRecord.from_payload(payload)
    with pytest.raises(error):
        ArtifactRecord(
            artifact_id=record.artifact_id,
            artifact_type=record.artifact_type,
            content_sha256=record.content_sha256,
            byte_length=byte_length,
            media_type=record.media_type,
            created_at=record.created_at,
            provenance_id=record.provenance_id,
        )
