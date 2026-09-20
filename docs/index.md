# Simulated Singularity

Simulated Singularity is a clean-slate, LangGraph-native artifact factory. The
current implementation is the Phase 0 + Phase 1 repository foundation: typed
runtime diagnostics, a CLI client, a canonical container, documentation, and
automated quality and architecture checks.

Start with the [architecture](architecture.md) and
[contributing guide](contributing.md).
The [Phase 0–1 specification](specifications/phase-0-1.md) defines current scope;
the [Technical Implementation Guide](specifications/technical-implementation-guide.md)
defines the long-term implementation within that gate.

- [Module ownership and manifest convention](architecture/modules.md)
- [CLI and diagnostics contract](architecture/cli.md)
- [Architecture decision records](adr/index.md)

The build also generates API reference from the implemented package's docstrings.
Only existing APIs are documented. There are no speech providers, production
graphs, model downloads, artifact storage, or persistence APIs in Phase 1.

The next proposed milestone is **Phase 2: implement the immutable artifact
foundation**, after Phase 1 review and explicit authorization.
