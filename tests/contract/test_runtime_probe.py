import platform
import sys

from simulated_singularity.application.diagnostics import RuntimeProbe
from simulated_singularity.bootstrap import diagnose_runtime
from simulated_singularity.infrastructure.runtime import LocalRuntimeProbe


def test_local_probe_fulfills_application_contract() -> None:
    probe: RuntimeProbe = LocalRuntimeProbe()
    facts = probe.inspect()
    assert facts.system == platform.system()
    assert facts.machine == platform.machine()
    assert facts.python_version == sys.version_info[:3]


def test_composition_uses_current_process_observations() -> None:
    report = diagnose_runtime()
    assert [check.observed for check in report.checks] == [
        platform.system(),
        platform.machine(),
        ".".join(map(str, sys.version_info[:3])),
    ]
