# Verified linux/amd64 manifest of the guide's CUDA 13.0.3 / Ubuntu 24.04 image.
FROM nvidia/cuda:13.0.3-cudnn-runtime-ubuntu24.04@sha256:af851538a2bb05f587f27b660d61de3643d964e75ef5c04f4086ff2b36f2a12a AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

RUN test "$(dpkg --print-architecture)" = amd64 \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       python3.12 python3.12-venv ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && python3.12 -m venv /opt/venv

FROM base AS build
WORKDIR /build
COPY requirements-build.lock ./
RUN python -m pip install --no-cache-dir --require-hashes -r requirements-build.lock
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m build --wheel --no-isolation

FROM base AS runtime
WORKDIR /app
COPY requirements.lock ./
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.lock
COPY --from=build /build/dist/*.whl /app/dist/
RUN python -m pip install --no-deps /app/dist/*.whl \
    && python -m pip check \
    && rm -rf /app/dist \
    && useradd --create-home --uid 10001 simulated-singularity

USER simulated-singularity
# Suppress the CUDA base's banner so informational --json output stays parseable.
ENTRYPOINT []
CMD ["ss", "--help"]
