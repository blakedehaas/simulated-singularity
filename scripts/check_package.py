"""Smoke-test a built wheel in an isolated environment, outside the source tree."""

import json
import subprocess
import tomllib
import venv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
version = tomllib.loads((root / "pyproject.toml").read_text())["project"]["version"]
wheel = root / "dist" / f"simulated_singularity-{version}-py3-none-any.whl"
environment = root / ".validation-venv"
venv.EnvBuilder(with_pip=True, clear=True).create(environment)
python = environment / "bin/python"
subprocess.run(
    [
        str(python),
        "-m",
        "pip",
        "install",
        "--require-hashes",
        "-r",
        str(root / "requirements.lock"),
    ],
    check=True,
)
subprocess.run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)], check=True)
subprocess.run([str(python), "-m", "pip", "check"], check=True)
subprocess.run(
    [
        str(python),
        "-I",
        "-c",
        (
            "import simulated_singularity; "
            "import simulated_singularity.platform.artifacts; "
            "import simulated_singularity.platform.identifiers"
        ),
    ],
    cwd=environment,
    check=True,
)
command = str(environment / "bin/ss")
subprocess.run([command, "--help"], cwd=environment, check=True)
report = subprocess.run(
    [command, "doctor", "--json"], cwd=environment, check=True, capture_output=True, text=True
)
payload = json.loads(report.stdout)
assert payload["schema_version"] == 1 and payload["passed"] is True
assert len(payload["checks"]) == 3
print(
    "Isolated installed wheel: public imports, dependency consistency, CLI, and doctor JSON passed."
)
