from dataclasses import FrozenInstanceError, dataclass

import pytest

from simulated_singularity.application.diagnostics import RuntimeFacts, run_doctor


@dataclass
class FixedRuntimeProbe:
    facts: RuntimeFacts
    calls: int = 0

    def inspect(self) -> RuntimeFacts:
        self.calls += 1
        return self.facts


@pytest.mark.parametrize("patch", [0, 3, 99])
def test_canonical_runtime_passes_and_is_observed_once(patch: int) -> None:
    probe = FixedRuntimeProbe(RuntimeFacts("Linux", "x86_64", (3, 12, patch)))
    report = run_doctor(probe)
    assert report.passed
    assert probe.calls == 1
    assert [check.name for check in report.checks] == ["operating_system", "architecture", "python"]
    assert [check.required for check in report.checks] == ["Linux", "x86_64", "3.12.x"]
    assert report.checks[2].observed == f"3.12.{patch}"


@pytest.mark.parametrize(
    ("facts", "failed"),
    [
        (RuntimeFacts("Windows", "x86_64", (3, 12, 0)), ["operating_system"]),
        (RuntimeFacts("Darwin", "x86_64", (3, 12, 0)), ["operating_system"]),
        (RuntimeFacts("Linux", "aarch64", (3, 12, 0)), ["architecture"]),
        (RuntimeFacts("Linux", "", (3, 12, 0)), ["architecture"]),
        (RuntimeFacts("Linux", "x86_64", (3, 11, 9)), ["python"]),
        (RuntimeFacts("Linux", "x86_64", (3, 13, 0)), ["python"]),
        (RuntimeFacts("Linux", "x86_64", (4, 12, 0)), ["python"]),
        (RuntimeFacts("", "", (0, 0, 0)), ["operating_system", "architecture", "python"]),
    ],
)
def test_unsupported_runtime_fails_closed(facts: RuntimeFacts, failed: list[str]) -> None:
    report = run_doctor(FixedRuntimeProbe(facts))
    assert not report.passed
    assert [check.name for check in report.checks if not check.passed] == failed


def test_probe_failure_is_not_a_healthy_report() -> None:
    class BrokenProbe:
        def inspect(self) -> RuntimeFacts:
            raise RuntimeError("observation unavailable")

    with pytest.raises(RuntimeError, match="observation unavailable"):
        run_doctor(BrokenProbe())


def test_observations_and_reports_are_immutable() -> None:
    facts = RuntimeFacts("Linux", "x86_64", (3, 12, 0))
    report = run_doctor(FixedRuntimeProbe(facts))
    for value, attribute in [(facts, "system"), (report, "checks"), (report.checks[0], "passed")]:
        with pytest.raises(FrozenInstanceError):
            setattr(value, attribute, None)
