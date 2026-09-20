"""Read local runtime facts using the standard library."""

import platform
import sys

from simulated_singularity.application.diagnostics import RuntimeFacts


class LocalRuntimeProbe:
    """Implement RuntimeProbe for the current process without I/O or side effects."""

    def inspect(self) -> RuntimeFacts:
        """Return OS, architecture, and interpreter facts without testing providers."""
        return RuntimeFacts(
            system=platform.system(),
            machine=platform.machine(),
            python_version=(sys.version_info.major, sys.version_info.minor, sys.version_info.micro),
        )
