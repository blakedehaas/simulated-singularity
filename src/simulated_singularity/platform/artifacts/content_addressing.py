"""Derive and verify storage-independent SHA-256 artifact identities."""

import hashlib
import hmac

from simulated_singularity.platform.artifacts.errors import ArtifactIntegrityError
from simulated_singularity.platform.identifiers import ArtifactId


def compute_sha256(content: bytes) -> str:
    """Return the lowercase SHA-256 hexadecimal digest of immutable bytes."""
    if not isinstance(content, bytes):
        raise TypeError("content must be bytes")
    return hashlib.sha256(content).hexdigest()


def artifact_id_for_content(content: bytes) -> ArtifactId:
    """Return the content-derived artifact identity for ``content``."""
    return ArtifactId(compute_sha256(content))


def verify_content_sha256(content: bytes, expected_sha256: str) -> None:
    """Verify bytes against canonical digest text or fail closed.

    Args:
        content: Immutable bytes whose identity is being verified.
        expected_sha256: A canonical lowercase SHA-256 hexadecimal digest.

    Raises:
        ArtifactIntegrityError: If the expected digest is malformed or the
            bytes produce a different digest.
    """
    try:
        expected = ArtifactId(expected_sha256)
    except (TypeError, ValueError) as error:
        raise ArtifactIntegrityError("expected SHA-256 is not canonical") from error
    actual = compute_sha256(content)
    if not hmac.compare_digest(actual, expected.value):
        raise ArtifactIntegrityError(f"content SHA-256 mismatch: expected {expected}, got {actual}")
