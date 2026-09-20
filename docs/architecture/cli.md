# CLI contract

The installed executable is `ss`. Phase 1 exposes these commands:

```sh
ss --help
ss doctor --help
ss doctor
ss doctor --json
```

`doctor` checks the running process for Linux, `x86_64`, and Python `3.12.x`.
An unsupported or unknown observation fails its check. Every check is required;
there is no warning-only or degraded mode. A passing report establishes these
foundation facts only. It makes no claim about CUDA availability, GPU identity,
model integrity, speech production, artifact storage, or persistence.

The application owns check policy. The runtime adapter observes the process;
the CLI only presents the resulting report and selects its process exit code.

| Exit status | Meaning |
| --- | --- |
| `0` | Help completed, or every doctor check passed. |
| `1` | A required doctor check failed, or a runtime observation raised an error. |
| `2` | Invalid command-line usage. |

Human output names each check and shows its observed and required values.
Machine callers should use `--json`, which emits one JSON object and no success
prose. The JSON contract is versioned independently of presentation:

```json
{
  "schema_version": 1,
  "passed": true,
  "checks": [
    {"name": "operating_system", "passed": true, "observed": "Linux", "required": "Linux"},
    {"name": "architecture", "passed": true, "observed": "x86_64", "required": "x86_64"},
    {"name": "python", "passed": true, "observed": "3.12.12", "required": "3.12.x"}
  ]
}
```

The Python patch version above is illustrative; the actual process supplies it.
`checks` always uses the documented order and names. `passed` is true exactly
when every check passed. A failed check still produces a complete report with
`passed: false` and exits `1`. An unexpected observation error propagates as an
error instead of producing a misleading report; it is not a schema-version-1
report.

There are no model, speech, run, artifact, graph, or deep diagnostic commands in
this milestone. Introduce each command with the complete subsystem it operates.
