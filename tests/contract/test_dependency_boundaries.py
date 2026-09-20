import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    ("module", "illegal_import", "contract"),
    [
        (
            "application/diagnostics.py",
            "import simulated_singularity.infrastructure.runtime",
            "Interfaces call the composition root",
        ),
        (
            "application/diagnostics.py",
            "import simulated_singularity.interfaces.cli.app",
            "Interfaces call the composition root",
        ),
        (
            "interfaces/cli/app.py",
            "import simulated_singularity.infrastructure.runtime",
            "CLI does not construct infrastructure",
        ),
        (
            "application/diagnostics.py",
            "import typer",
            "Application is independent of deployment and presentation",
        ),
        (
            "application/diagnostics.py",
            "from pathlib import Path",
            "Application is independent of deployment and presentation",
        ),
        (
            "platform/artifacts/models.py",
            "from pathlib import Path",
            "Platform contracts are independent of adapters and deployment",
        ),
        (
            "platform/identifiers/models.py",
            "import simulated_singularity.platform.artifacts.models",
            "Artifact contracts depend inward on identifiers",
        ),
    ],
)
def test_import_contracts_reject_real_boundary_violations(
    tmp_path: Path, module: str, illegal_import: str, contract: str
) -> None:
    # Analyze a disposable source copy, so mutation tests never change the checkout.
    source = tmp_path / "src"
    shutil.copytree(ROOT / "src", source, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy(ROOT / "pyproject.toml", tmp_path)
    target = source / "simulated_singularity" / module
    target.write_text(target.read_text() + f"\n{illegal_import}\n")
    result = subprocess.run(
        [str(Path(sys.executable).parent / "lint-imports"), "--no-cache"],
        cwd=tmp_path,
        env={**os.environ, "PYTHONPATH": str(source)},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert contract in result.stdout
    assert "BROKEN" in result.stdout
