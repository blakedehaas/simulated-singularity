from dataclasses import FrozenInstanceError
from typing import Any

import pytest

from simulated_singularity.platform.identifiers import (
    ArtifactId,
    CapabilityId,
    ExecutionKey,
    ProvenanceId,
)

SHA256 = "a" * 64


def test_artifact_id_serializes_as_canonical_digest() -> None:
    artifact_id = ArtifactId.parse(SHA256)
    assert artifact_id.value == SHA256
    assert artifact_id.serialize() == SHA256
    assert str(artifact_id) == SHA256


@pytest.mark.parametrize(
    "value",
    ["", "a" * 63, "a" * 65, "A" * 64, "g" * 64, " " + "a" * 63, 42],
)
def test_artifact_id_rejects_noncanonical_values(value: Any) -> None:
    error = TypeError if not isinstance(value, str) else ValueError
    with pytest.raises(error):
        ArtifactId.parse(value)


@pytest.mark.parametrize("identifier_type", [ProvenanceId, CapabilityId, ExecutionKey])
def test_opaque_identifiers_preserve_exact_serialization(
    identifier_type: type[ProvenanceId] | type[CapabilityId] | type[ExecutionKey],
) -> None:
    identifier = identifier_type.parse("stable:value/1")
    assert identifier.value == "stable:value/1"
    assert identifier.serialize() == "stable:value/1"
    assert str(identifier) == "stable:value/1"


@pytest.mark.parametrize("identifier_type", [ProvenanceId, CapabilityId, ExecutionKey])
@pytest.mark.parametrize("value", ["", " padded", "padded ", 7])
def test_opaque_identifiers_reject_ambiguous_values(
    identifier_type: type[ProvenanceId] | type[CapabilityId] | type[ExecutionKey], value: Any
) -> None:
    error = TypeError if not isinstance(value, str) else ValueError
    with pytest.raises(error):
        identifier_type.parse(value)


def test_identifier_types_are_nominal_and_immutable() -> None:
    provenance_id = ProvenanceId("same")
    capability_id = CapabilityId("same")
    execution_key = ExecutionKey("same")
    assert provenance_id != capability_id  # type: ignore[comparison-overlap]
    assert capability_id != execution_key  # type: ignore[comparison-overlap]
    with pytest.raises(FrozenInstanceError):
        provenance_id.__setattr__("value", "changed")
