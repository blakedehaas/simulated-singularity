"""Provider-neutral port for immutable artifact persistence."""

from typing import Protocol

from simulated_singularity.platform.artifacts.models import ArtifactPayload, ArtifactRecord
from simulated_singularity.platform.identifiers import ArtifactId


class ArtifactRepository(Protocol):
    """Store and retrieve immutable content-addressed artifact payloads.

    Implementations derive identity from payload bytes, make repeated storage of
    identical payloads idempotent, verify content before reuse or return, and
    never expose a filesystem path through this contract.
    """

    def put(self, artifact: ArtifactPayload) -> ArtifactRecord:
        """Persist ``artifact`` atomically and return its immutable record.

        Implementations raise ``ArtifactIntegrityError`` for any content/hash
        inconsistency. Phase 2A defines no concrete persistence adapter or its
        storage-failure policy.
        """
        ...

    def get(self, artifact_id: ArtifactId) -> ArtifactPayload:
        """Return verified payload content or raise ``ArtifactNotFoundError``."""
        ...

    def exists(self, artifact_id: ArtifactId) -> bool:
        """Return whether a valid payload exists for ``artifact_id``.

        Corrupt content must not be reported as a valid existing artifact.
        """
        ...
