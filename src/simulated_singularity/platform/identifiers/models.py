"""Define storage-independent identifiers required by the artifact contracts."""

from dataclasses import dataclass
from typing import Self


def _validate_opaque_value(value: str, kind: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{kind} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{kind} must be non-empty and have no surrounding whitespace")


@dataclass(frozen=True, slots=True)
class ArtifactId:
    """Identify artifact bytes by their lowercase, 64-character SHA-256 digest.

    ``serialize`` and ``str`` both return the digest without a scheme prefix.
    Construction and ``parse`` reject uppercase, truncated, or non-hexadecimal
    values. The type describes identity only; it owns no filesystem layout.
    """

    value: str

    def __post_init__(self) -> None:
        """Reject values that are not canonical SHA-256 hexadecimal text."""
        if not isinstance(self.value, str):
            raise TypeError("ArtifactId must be a string")
        if len(self.value) != 64 or any(
            character not in "0123456789abcdef" for character in self.value
        ):
            raise ValueError("ArtifactId must be 64 lowercase hexadecimal characters")

    @classmethod
    def parse(cls, value: str) -> Self:
        """Parse canonical serialized text, raising for invalid input."""
        return cls(value)

    def serialize(self) -> str:
        """Return the canonical storage and interchange representation."""
        return self.value

    def __str__(self) -> str:
        """Return the canonical serialized digest."""
        return self.serialize()


@dataclass(frozen=True, slots=True)
class ProvenanceId:
    """Identify one provenance record using caller-assigned opaque text.

    Phase 2A does not prescribe UUID or database-generation semantics. The
    canonical serialization is the exact non-empty, whitespace-trimmed value.
    """

    value: str

    def __post_init__(self) -> None:
        """Reject non-string, empty, or ambiguously padded values."""
        _validate_opaque_value(self.value, type(self).__name__)

    @classmethod
    def parse(cls, value: str) -> Self:
        """Parse canonical serialized text, raising for invalid input."""
        return cls(value)

    def serialize(self) -> str:
        """Return the exact canonical text supplied at construction."""
        return self.value

    def __str__(self) -> str:
        """Return the canonical serialized value."""
        return self.serialize()


@dataclass(frozen=True, slots=True)
class CapabilityId:
    """Identify a provider-neutral capability using stable opaque text."""

    value: str

    def __post_init__(self) -> None:
        """Reject non-string, empty, or ambiguously padded values."""
        _validate_opaque_value(self.value, type(self).__name__)

    @classmethod
    def parse(cls, value: str) -> Self:
        """Parse canonical serialized text, raising for invalid input."""
        return cls(value)

    def serialize(self) -> str:
        """Return the exact canonical text supplied at construction."""
        return self.value

    def __str__(self) -> str:
        """Return the canonical serialized value."""
        return self.serialize()


@dataclass(frozen=True, slots=True)
class ExecutionKey:
    """Reference a future execution identity without defining its derivation.

    This Phase 2A value is intentionally opaque. Canonical configuration,
    execution-key derivation, retry identity, cache lookup, and cache policy
    remain Phase 3 responsibilities. Serialization preserves the exact value.
    """

    value: str

    def __post_init__(self) -> None:
        """Reject non-string, empty, or ambiguously padded values."""
        _validate_opaque_value(self.value, type(self).__name__)

    @classmethod
    def parse(cls, value: str) -> Self:
        """Parse canonical serialized text, raising for invalid input."""
        return cls(value)

    def serialize(self) -> str:
        """Return the exact canonical text supplied at construction."""
        return self.value

    def __str__(self) -> str:
        """Return the canonical serialized value."""
        return self.serialize()
