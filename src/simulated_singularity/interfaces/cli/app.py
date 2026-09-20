"""The public ``ss`` command surface; no runtime policy is implemented here."""

import json
from dataclasses import asdict
from typing import Annotated

import typer

from simulated_singularity.bootstrap import diagnose_runtime

app = typer.Typer(
    help="Simulated Singularity — Phase 1 foundation.",
    add_completion=False,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)


@app.callback()
def main() -> None:
    """Expose foundation commands without starting unimplemented capabilities."""


@app.command()
def doctor(
    json_output: Annotated[
        bool, typer.Option("--json", help="Emit a single JSON report with schema_version 1.")
    ] = False,
) -> None:
    """Check Linux, x86-64, and Python 3.12; exit 1 if any required check fails.

    Exit 0 means only the Phase 1 foundation passed, not GPU/inference readiness.
    Output is presentation of the application report; unexpected probe failures
    propagate as errors and cannot become a successful report.
    """
    report = diagnose_runtime()
    if json_output:
        typer.echo(json.dumps({"schema_version": 1, "passed": report.passed, **asdict(report)}))
    else:
        typer.echo("Phase 1 foundation diagnostics (no GPU or provider checks)")
        for check in report.checks:
            status = "PASS" if check.passed else "FAIL"
            typer.echo(f"{status} {check.name}: {check.observed} (required: {check.required})")
    raise typer.Exit(code=0 if report.passed else 1)
