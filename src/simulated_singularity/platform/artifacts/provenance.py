"""Immutable provenance describing how an artifact was produced."""

from dataclasses import dataclass
from datetime import datetime

from simulated_singularity.platform.artifacts.models import _validate_text, _validate_timestamp
from simulated_singularity.platform.identifiers import (
    ArtifactId,
    CapabilityId,
    ExecutionKey,
    ProvenanceId,
)


@dataclass(frozen=True, slots=True)
class ProvenanceRecord:
    """Record reproducibility facts without implementing execution behavior.

    Input artifact order is preserved as part of provenance. Configuration is
    represented only by its canonical SHA-256 supplied by the future execution
    layer. ``execution_key`` is an opaque Phase 3 reference: this model performs
    no derivation, retry, lookup, or caching.
    """

    provenance_id: ProvenanceId
    capability_id: CapabilityId
    capability_version: str
    provider_id: str
    provider_version: str
    model_id: str | None
    model_revision: str | None
    application_version: str
    container_version: str | None
    input_artifact_ids: tuple[ArtifactId, ...]
    configuration_sha256: str
    execution_key: ExecutionKey
    random_seed: int | None
    created_at: datetime

    def __post_init__(self) -> None:
        """Validate reproducibility fields and canonical hash representation."""
        if not isinstance(self.provenance_id, ProvenanceId):
            raise TypeError("provenance_id must be a ProvenanceId")
        if not isinstance(self.capability_id, CapabilityId):
            raise TypeError("capability_id must be a CapabilityId")
        if not isinstance(self.execution_key, ExecutionKey):
            raise TypeError("execution_key must be an ExecutionKey")
        _validate_text(self.capability_version, "capability_version")
        _validate_text(self.provider_id, "provider_id")
        _validate_text(self.provider_version, "provider_version")
        _validate_text(self.application_version, "application_version")
        for name, value in (
            ("model_id", self.model_id),
            ("model_revision", self.model_revision),
            ("container_version", self.container_version),
        ):
            if value is not None:
                _validate_text(value, name)
        if self.model_revision is not None and self.model_id is None:
            raise ValueError("model_revision requires model_id")
        if not isinstance(self.input_artifact_ids, tuple):
            raise TypeError("input_artifact_ids must be a tuple")
        if any(not isinstance(artifact_id, ArtifactId) for artifact_id in self.input_artifact_ids):
            raise TypeError("input_artifact_ids must contain only ArtifactId values")
        ArtifactId(self.configuration_sha256)
        if self.random_seed is not None and (
            not isinstance(self.random_seed, int) or isinstance(self.random_seed, bool)
        ):
            raise TypeError("random_seed must be an integer or None")
        _validate_timestamp(self.created_at, "created_at")
