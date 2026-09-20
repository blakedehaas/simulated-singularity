"""Structured failures shared by artifact repository implementations."""

from simulated_singularity.platform.identifiers import ArtifactId


class ArtifactError(Exception):
    """Base class for failures exposed by artifact contracts."""


class ArtifactNotFoundError(ArtifactError):
    """Report that a repository has no payload for a requested artifact ID."""

    def __init__(self, artifact_id: ArtifactId) -> None:
        """Record the missing identity for structured caller handling."""
        self.artifact_id = artifact_id
        super().__init__(f"artifact not found: {artifact_id}")


class ArtifactIntegrityError(ArtifactError):
    """Report bytes or digest text that violates content-addressing integrity."""
