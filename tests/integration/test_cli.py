import json

import pytest
from typer.testing import CliRunner

from simulated_singularity.application.diagnostics import DiagnosticCheck, DoctorReport
from simulated_singularity.interfaces.cli import app as cli

runner = CliRunner()


@pytest.mark.parametrize("arguments", [["--help"], ["doctor", "--help"]])
def test_help(arguments: list[str]) -> None:
    result = runner.invoke(cli.app, arguments)
    assert result.exit_code == 0
    assert "doctor" in result.output


@pytest.mark.parametrize("failed_index", [None, 0, 1, 2])
@pytest.mark.parametrize("json_output", [True, False])
def test_doctor_output_and_exit_status(
    monkeypatch: pytest.MonkeyPatch, failed_index: int | None, json_output: bool
) -> None:
    report = DoctorReport(
        (
            DiagnosticCheck("operating_system", failed_index != 0, "Linux", "Linux"),
            DiagnosticCheck("architecture", failed_index != 1, "x86_64", "x86_64"),
            DiagnosticCheck("python", failed_index != 2, "3.12.3", "3.12.x"),
        )
    )
    monkeypatch.setattr(cli, "diagnose_runtime", lambda: report)
    result = runner.invoke(cli.app, ["doctor", "--json"] if json_output else ["doctor"])
    assert result.exit_code == (0 if failed_index is None else 1)
    if json_output:
        assert json.loads(result.stdout) == {
            "schema_version": 1,
            "passed": failed_index is None,
            "checks": [
                {"name": c.name, "passed": c.passed, "observed": c.observed, "required": c.required}
                for c in report.checks
            ],
        }
        assert result.stderr == ""
    else:
        assert "Phase 1 foundation" in result.output
        for check in report.checks:
            assert f"{'PASS' if check.passed else 'FAIL'} {check.name}:" in result.output


def test_probe_error_cannot_emit_success_json(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken_diagnosis() -> DoctorReport:
        raise RuntimeError("observation unavailable")

    monkeypatch.setattr(cli, "diagnose_runtime", broken_diagnosis)
    result = runner.invoke(cli.app, ["doctor", "--json"])
    assert result.exit_code != 0
    assert isinstance(result.exception, RuntimeError)
    assert result.stdout == ""


@pytest.mark.parametrize("arguments", [[], ["speech"], ["doctor", "--deep"]])
def test_usage_errors_and_unimplemented_commands(arguments: list[str]) -> None:
    assert runner.invoke(cli.app, arguments).exit_code == 2
