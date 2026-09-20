"""Immutable artifact payload and metadata records."""

import math
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType
from typing import cast

from simulated_singularity.platform.artifacts.content_addressing import artifact_id_for_content
from simulated_singularity.platform.identifiers import ArtifactId, ProvenanceId

type _JsonScalar = None | bool | int | float | str
type JsonValue = _JsonScalar | tuple[JsonValue, ...] | Mapping[str, JsonValue]


def _validate_text(value: str, name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{name} must be non-empty and have no surrounding whitespace")


def _validate_timestamp(value: datetime, name: str) -> None:
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must include a UTC offset")


def _freeze_json(value: object, location: str) -> JsonValue:
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"{location} must not contain non-finite floats")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, JsonValue] = {}
        for key, child in value.items():
            if not isinstance(key, str):
                raise TypeError(f"{location} keys must be strings")
            frozen[key] = _freeze_json(child, f"{location}.{key}")
        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_json(child, f"{location}[]") for child in value)
    raise TypeError(f"{location} contains a non-JSON value: {type(value).__name__}")


def _freeze_metadata(metadata: Mapping[str, object]) -> Mapping[str, JsonValue]:
    if not isinstance(metadata, Mapping):
        raise TypeError("metadata must be a mapping")
    return cast(Mapping[str, JsonValue], _freeze_json(metadata, "metadata"))


@dataclass(frozen=True, slots=True)
class ArtifactType:
    """Classify an artifact without defining a closed modality hierarchy.

    The exact non-empty value is its deterministic serialized representation.
    """

    value: str

    def __post_init__(self) -> None:
        """Reject non-string, empty, or ambiguously padded values."""
        _validate_text(self.value, type(self).__name__)

    @classmethod
    def parse(cls, value: str) -> "ArtifactType":
        """Parse canonical serialized text, raising for invalid input."""
        return cls(value)

    def serialize(self) -> str:
        """Return the exact canonical text supplied at construction."""
        return self.value

    def __str__(self) -> str:
        """Return the canonical serialized value."""
        return self.serialize()


@dataclass(frozen=True, slots=True)
class ArtifactPayload:
    """Carry immutable bytes and descriptive metadata without a storage path.

    Metadata is recursively copied into read-only mappings and tuples. Only
    finite JSON scalar values are accepted. Repository adapters derive identity
    from ``content`` and must not mutate or overwrite it.
    """

    content: bytes
    artifact_type: ArtifactType
    media_type: str
    created_at: datetime
    provenance_id: ProvenanceId
    metadata: Mapping[str, JsonValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate payload invariants and make metadata deeply immutable."""
        if not isinstance(self.content, bytes):
            raise TypeError("content must be bytes")
        if not isinstance(self.artifact_type, ArtifactType):
            raise TypeError("artifact_type must be an ArtifactType")
        if not isinstance(self.provenance_id, ProvenanceId):
            raise TypeError("provenance_id must be a ProvenanceId")
        _validate_text(self.media_type, "media_type")
        _validate_timestamp(self.created_at, "created_at")
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))


@dataclass(frozen=True, slots=True)
class ArtifactRecord:
    """Describe one immutable, content-addressed artifact.

    ``artifact_id`` and ``content_sha256`` must be the same canonical digest.
    The record contains no payload bytes or filesystem path. Metadata is deeply
    immutable and JSON-compatible under the artifact module's value contract.
    """

    artifact_id: ArtifactId
    artifact_type: ArtifactType
    content_sha256: str
    byte_length: int
    media_type: str
    created_at: datetime
    provenance_id: ProvenanceId
    metadata: Mapping[str, JsonValue] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate identity, size, text, timestamp, and metadata invariants."""
        if not isinstance(self.artifact_id, ArtifactId):
            raise TypeError("artifact_id must be an ArtifactId")
        if not isinstance(self.artifact_type, ArtifactType):
            raise TypeError("artifact_type must be an ArtifactType")
        if not isinstance(self.provenance_id, ProvenanceId):
            raise TypeError("provenance_id must be a ProvenanceId")
        content_id = ArtifactId(self.content_sha256)
        if self.artifact_id != content_id:
            raise ValueError("artifact_id must equal content_sha256")
        if not isinstance(self.byte_length, int) or isinstance(self.byte_length, bool):
            raise TypeError("byte_length must be an integer")
        if self.byte_length < 0:
            raise ValueError("byte_length must not be negative")
        _validate_text(self.media_type, "media_type")
        _validate_timestamp(self.created_at, "created_at")
        object.__setattr__(self, "metadata", _freeze_metadata(self.metadata))

    @classmethod
    def from_payload(cls, payload: ArtifactPayload) -> "ArtifactRecord":
        """Build a consistent record from payload bytes and descriptive fields."""
        artifact_id = artifact_id_for_content(payload.content)
        return cls(
            artifact_id=artifact_id,
            artifact_type=payload.artifact_type,
            content_sha256=artifact_id.value,
            byte_length=len(payload.content),
            media_type=payload.media_type,
            created_at=payload.created_at,
            provenance_id=payload.provenance_id,
            metadata=payload.metadata,
        )
