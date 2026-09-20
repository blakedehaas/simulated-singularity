"""Immutable artifact, provenance, repository, and content-addressing contracts."""

from simulated_singularity.platform.artifacts.content_addressing import (
    artifact_id_for_content,
    compute_sha256,
    verify_content_sha256,
)
from simulated_singularity.platform.artifacts.errors import (
    ArtifactError,
    ArtifactIntegrityError,
    ArtifactNotFoundError,
)
from simulated_singularity.platform.artifacts.models import (
    ArtifactPayload,
    ArtifactRecord,
    ArtifactType,
    JsonValue,
)
from simulated_singularity.platform.artifacts.provenance import ProvenanceRecord
from simulated_singularity.platform.artifacts.repository import ArtifactRepository

__all__ = [
    "ArtifactError",
    "ArtifactIntegrityError",
    "ArtifactNotFoundError",
    "ArtifactPayload",
    "ArtifactRecord",
    "ArtifactRepository",
    "ArtifactType",
    "JsonValue",
    "ProvenanceRecord",
    "artifact_id_for_content",
    "compute_sha256",
    "verify_content_sha256",
]
