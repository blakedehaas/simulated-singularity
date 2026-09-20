# Simulated Singularity

Simulated Singularity is a clean-slate, LangGraph-native artifact factory. The
current implementation is the reviewed Phase 1 repository foundation plus Phase
2A artifact contracts: typed runtime diagnostics, immutable artifact/provenance
models, SHA-256 content identity, a repository port, a CLI client, a canonical
container, documentation, and automated quality and architecture checks.

Start with the [architecture](architecture.md) and
[contributing guide](contributing.md).
The [Phase 2 specification](specifications/phase-2.md) defines current scope;
the [Technical Implementation Guide](specifications/technical-implementation-guide.md)
defines the long-term implementation within that gate.

- [Module ownership and manifest convention](architecture/modules.md)
- [Artifact contracts](architecture/artifacts.md)
- [CLI and diagnostics contract](architecture/cli.md)
- [Architecture decision records](adr/index.md)

The build also generates API reference from the implemented package's docstrings.
Only existing APIs are documented. There are no speech providers, production
graphs, model downloads, filesystem artifact storage, or metadata persistence.

The next proposed slice is **Phase 2B: content-addressed filesystem repository**,
after Phase 2A review and explicit authorization.
