"""Generate API/CLI reference and publish root guides during the MkDocs build."""

from pathlib import Path

import mkdocs_gen_files
from typer.testing import CliRunner

from simulated_singularity.interfaces.cli.app import app

for guide in ("ARCHITECTURE", "CONTRIBUTING"):
    with mkdocs_gen_files.open(f"{guide.lower()}.md", "w") as output:
        output.write(Path(f"{guide}.md").read_text().replace("](docs/", "]("))

with mkdocs_gen_files.open("reference/api.md", "w") as output:
    output.write("# Python API\n\nGenerated from the implemented public modules.\n\n")
    for source in sorted(Path("src/simulated_singularity").rglob("*.py")):
        if source.name == "__init__.py":
            continue
        module = ".".join(source.relative_to("src").with_suffix("").parts)
        output.write(f"::: {module}\n\n")

with mkdocs_gen_files.open("reference/cli.md", "w") as output:
    output.write("# CLI reference\n\nGenerated from the installed command definitions.\n\n")
    for arguments in (["--help"], ["doctor", "--help"]):
        result = CliRunner().invoke(app, arguments, env={"COLUMNS": "100", "NO_COLOR": "1"})
        if result.exit_code != 0:
            raise RuntimeError(f"CLI reference failed: {result.output}")
        output.write(f"## ss {' '.join(arguments)}\n\n```text\n{result.stdout}\n```\n\n")
