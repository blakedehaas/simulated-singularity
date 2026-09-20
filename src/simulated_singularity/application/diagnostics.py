"""Evaluate the implemented runtime foundation without importing deployment details."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RuntimeFacts:
    """An immutable observation of the Python process, with no deployment handles.

    Adapters supply OS and machine names and the numeric Python version. These
    are observations, not assertions of compatibility or GPU readiness.
    """

    system: str
    machine: str
    python_version: tuple[int, int, int]


class RuntimeProbe(Protocol):
    """Observe the current process without deciding whether it is supported."""

    def inspect(self) -> RuntimeFacts:
        """Return a runtime snapshot; propagate observation failures to the caller."""
        ...


@dataclass(frozen=True)
class DiagnosticCheck:
    """One required check, including observed and required values for remediation.

    The stable name identifies the check in machine output. A false ``passed``
    value is a failure, never a warning or an invitation to use a fallback.
    """

    name: str
    passed: bool
    observed: str
    required: str


@dataclass(frozen=True)
class DoctorReport:
    """The three Phase 1 checks in OS, architecture, Python order.

    Reports contain no provider, filesystem, model, or persistence claims.
    ``passed`` is derived from the checks rather than stored independently.
    """

    checks: tuple[DiagnosticCheck, DiagnosticCheck, DiagnosticCheck]

    @property
    def passed(self) -> bool:
        """Return true only when every required foundation check passes."""
        return all(check.passed for check in self.checks)


def run_doctor(probe: RuntimeProbe) -> DoctorReport:
    """Inspect once and evaluate the canonical Linux/amd64/Python 3.12 foundation.

    Unsupported observations become failed checks, including unknown values.
    Probe exceptions propagate; an observation failure must never report success.
    GPU execution and later subsystems are outside this contract.
    """
    facts = probe.inspect()
    return DoctorReport(
        checks=(
            DiagnosticCheck("operating_system", facts.system == "Linux", facts.system, "Linux"),
            DiagnosticCheck("architecture", facts.machine == "x86_64", facts.machine, "x86_64"),
            DiagnosticCheck(
                "python",
                facts.python_version[:2] == (3, 12),
                ".".join(str(part) for part in facts.python_version),
                "3.12.x",
            ),
        )
    )
