"""Composition root: connect application contracts to their concrete adapters."""

from simulated_singularity.application.diagnostics import DoctorReport, run_doctor
from simulated_singularity.infrastructure.runtime import LocalRuntimeProbe


def diagnose_runtime() -> DoctorReport:
    """Run foundation diagnostics against this process; propagate probe failures.

    This function owns wiring only. Compatibility policy belongs to the
    application and fact collection belongs to the runtime adapter.
    """
    return run_doctor(LocalRuntimeProbe())
