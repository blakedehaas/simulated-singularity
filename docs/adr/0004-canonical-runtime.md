# 0004: Canonical Linux CUDA container

Status: Established by the normative specifications; implementation subject to
Phase 1 review.

## Context

Later NVIDIA-backed providers need a reproducible deployment target. Phase 1
needs a real container foundation without pretending those providers exist.

## Decision

Use one `linux/amd64` NVIDIA CUDA container based on Ubuntu 24.04 with Python 3.12.
Pin the base image and Python dependencies. Run the application as a non-root
user. Compose reserves NVIDIA GPUs and introduces no persistence mounts before
persistent subsystems exist.

Doctor evaluates Linux, x86-64, and Python 3.12 only. Foundation container smoke
checks exercise the Python application without invoking GPU inference.

## Consequences

Windows/WSL2 and Linux workstations host the same canonical application container.
There is no native-Windows, CPU fallback, AMD, or DirectML inference branch.
Passing Phase 1 doctor does not certify GPU readiness. Provider-specific runtime
checks and model mounts arrive with the corresponding implemented subsystem.

## Alternatives considered

Separate application runtimes increase compatibility branches. Installing
unimplemented inference dependencies would increase the foundation's dependency
surface and imply unsupported capabilities. Both are outside the current scope.
