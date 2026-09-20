import hashlib

import pytest

from simulated_singularity.platform.artifacts import (
    ArtifactIntegrityError,
    artifact_id_for_content,
    compute_sha256,
    verify_content_sha256,
)


@pytest.mark.parametrize("content", [b"", b"artifact bytes", bytes(range(256))])
def test_sha256_derivation_is_standard_and_deterministic(content: bytes) -> None:
    expected = hashlib.sha256(content).hexdigest()
    assert compute_sha256(content) == expected
    assert artifact_id_for_content(content).value == expected
    verify_content_sha256(content, expected)


@pytest.mark.parametrize("expected", ["bad", "A" * 64, "0" * 64, 12])
def test_verification_fails_closed_for_malformed_or_mismatched_digest(expected: object) -> None:
    with pytest.raises(ArtifactIntegrityError):
        verify_content_sha256(b"artifact bytes", expected)  # type: ignore[arg-type]


def test_integrity_error_reports_expected_and_actual_digests() -> None:
    expected = "0" * 64
    with pytest.raises(ArtifactIntegrityError, match=f"expected {expected}, got"):
        verify_content_sha256(b"artifact bytes", expected)


@pytest.mark.parametrize("content", [bytearray(b"mutable"), "text"])
def test_content_addressing_requires_immutable_bytes(content: object) -> None:
    with pytest.raises(TypeError, match="content must be bytes"):
        compute_sha256(content)  # type: ignore[arg-type]
