"""Reusable behavioral contract for future ArtifactRepository adapters."""

from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from simulated_singularity.platform.artifacts import (
    ArtifactError,
    ArtifactNotFoundError,
    ArtifactPayload,
    ArtifactRecord,
    ArtifactRepository,
    ArtifactType,
    artifact_id_for_content,
    verify_content_sha256,
)
from simulated_singularity.platform.identifiers import ArtifactId, ProvenanceId

RepositoryFactory = Callable[[], ArtifactRepository]


def sample_payload(content: bytes = b"contract payload") -> ArtifactPayload:
    """Create deterministic immutable input shared by repository contract cases."""
    return ArtifactPayload(
        content=content,
        artifact_type=ArtifactType("contract.fixture"),
        media_type="application/octet-stream",
        created_at=datetime(2026, 9, 20, tzinfo=UTC),
        provenance_id=ProvenanceId("contract-provenance"),
        metadata={"suite": "ArtifactRepository"},
    )


class ArtifactRepositoryContract:
    """Mixin supplying adapter-independent ArtifactRepository contract tests.

    Concrete test classes inherit this mixin and provide a
    ``repository_factory`` fixture. Repeated factory calls must reopen the same
    backing repository for the duration of one test.
    """

    def test_put_get_round_trip(self, repository_factory: RepositoryFactory) -> None:
        repository = repository_factory()
        payload = sample_payload()
        record = repository.put(payload)
        assert repository.get(record.artifact_id) == payload

    def test_exists_tracks_valid_artifacts(self, repository_factory: RepositoryFactory) -> None:
        repository = repository_factory()
        payload = sample_payload()
        artifact_id = artifact_id_for_content(payload.content)
        assert not repository.exists(artifact_id)
        repository.put(payload)
        assert repository.exists(artifact_id)

    def test_identical_content_is_idempotent(self, repository_factory: RepositoryFactory) -> None:
        repository = repository_factory()
        payload = sample_payload()
        assert repository.put(payload) == repository.put(payload)

    def test_changed_content_has_new_identity(self, repository_factory: RepositoryFactory) -> None:
        repository = repository_factory()
        first = repository.put(sample_payload(b"first"))
        second = repository.put(sample_payload(b"second"))
        assert first.artifact_id != second.artifact_id

    def test_missing_artifact_is_structured(self, repository_factory: RepositoryFactory) -> None:
        repository = repository_factory()
        missing = ArtifactId("0" * 64)
        assert not repository.exists(missing)
        with pytest.raises(ArtifactNotFoundError) as raised:
            repository.get(missing)
        assert raised.value.artifact_id == missing
        assert isinstance(raised.value, ArtifactError)

    def test_record_identity_matches_payload_hash(
        self, repository_factory: RepositoryFactory
    ) -> None:
        payload = sample_payload()
        record = repository_factory().put(payload)
        assert record == ArtifactRecord.from_payload(payload)
        assert record.artifact_id == artifact_id_for_content(payload.content)
        assert record.content_sha256 == record.artifact_id.value

    def test_retrieved_content_matches_identity(
        self, repository_factory: RepositoryFactory
    ) -> None:
        repository = repository_factory()
        record = repository.put(sample_payload())
        retrieved = repository.get(record.artifact_id)
        verify_content_sha256(retrieved.content, record.content_sha256)

    def test_reopened_repository_retains_payload(
        self, repository_factory: RepositoryFactory
    ) -> None:
        first = repository_factory()
        payload = sample_payload()
        artifact_id = first.put(payload).artifact_id
        reopened = repository_factory()
        assert reopened is not first
        assert reopened.exists(artifact_id)
        assert reopened.get(artifact_id) == payload
