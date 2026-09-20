from collections.abc import Callable

import pytest

from simulated_singularity.platform.artifacts import (
    ArtifactNotFoundError,
    ArtifactPayload,
    ArtifactRecord,
    ArtifactRepository,
)
from simulated_singularity.platform.identifiers import ArtifactId
from tests.contract.artifact_repository_contract import ArtifactRepositoryContract


class InMemoryArtifactRepository:
    """Test double proving the reusable contract independently of Phase 2B."""

    def __init__(self, payloads: dict[ArtifactId, ArtifactPayload]) -> None:
        self._payloads = payloads

    def put(self, artifact: ArtifactPayload) -> ArtifactRecord:
        record = ArtifactRecord.from_payload(artifact)
        existing = self._payloads.setdefault(record.artifact_id, artifact)
        return ArtifactRecord.from_payload(existing)

    def get(self, artifact_id: ArtifactId) -> ArtifactPayload:
        try:
            return self._payloads[artifact_id]
        except KeyError as error:
            raise ArtifactNotFoundError(artifact_id) from error

    def exists(self, artifact_id: ArtifactId) -> bool:
        return artifact_id in self._payloads


@pytest.fixture
def repository_factory() -> Callable[[], ArtifactRepository]:
    payloads: dict[ArtifactId, ArtifactPayload] = {}

    def factory() -> ArtifactRepository:
        return InMemoryArtifactRepository(payloads)

    return factory


class TestInMemoryArtifactRepositoryContract(ArtifactRepositoryContract):
    """Execute every reusable case against a deterministic contract test double."""
