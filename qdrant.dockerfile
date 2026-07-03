# ==============================================================================
# Dockerfile for Qdrant Vector Database
# ==============================================================================
# Build args:
#   --build-arg QDRANT_VERSION=v1.18.2
#
# Environment variables (inherited at runtime via docker-compose):
#   QDRANT_VERSION   - mirrors the build arg inside the image for traceability
#   QDRANT__SERVICE__HTTP_PORT  - REST API port (default 6333)
#   QDRANT__SERVICE__GRPC_PORT  - gRPC API port (default 6334)
#   QDRANT__SERVICE__MAX_REQUEST_SIZE_MB - max request size in MB
#   QDRANT__LOG_LEVEL - log level (default: INFO)
#
# Ports exposed:
#   6333  - REST API
#   6334  - gRPC
#
# Persistence:
#   Data is stored in /qdrant/storage and must be mounted from a named volume
#   defined in docker-compose.yml (see qdrant_storage). No VOLUME directive
#   is set here so that the compose file owns the lifecycle of the mount point.
#
# Security:
#   - Runs as non-root user "qdrant" (UID 1000), defined in the base image.
#   - No RUN apt-get / apk add commands (layers are kept minimal).
#   - Minimal attack surface; only the official Qdrant binary is present.
# ==============================================================================

# 1. Build argument: Qdrant version
# Defaults to v1.18.2; override with --build-arg QDRANT_VERSION=<version>
ARG QDRANT_VERSION=v1.18.2
ARG HOST = ${QDRANT_HOST}

# 2. Base image: official Qdrant runtime image
# Uses multi-arch manifest (amd64/arm64) and a pinned semantic version tag.
FROM qdrant/qdrant:${QDRANT_VERSION} AS base

# 3. Re-declare the build arg as an environment variable inside the image.
# ARGs defined before FROM are scoped to that stage and are NOT available
# after the FROM line, so we re-expose it here for runtime traceability.
ARG QDRANT_VERSION
ENV QDRANT_VERSION=${QDRANT_VERSION}

# 4. Switch to non-root user "qdrant" (UID 1000) for security.
# The qdrant user is created in the base image; we simply switch to it.
USER qdrant

# 5. Expose REST and gRPC ports.
# - 6333: REST API (http + openapi-ui)
# - 6334: gRPC (binary protocol, lower latency)
EXPOSE 6333
EXPOSE 6334

# 6. Health check using wget --spider (guaranteed present in distroless/base).
# Probes the /healthz endpoint which returns HTTP 200 when Qdrant is ready.
# --spider: do not download the body. --no-check-certificate: skip TLS validation
# for the loopback probe. Retries every 30s, times out after 5s.
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=10s \
    CMD wget --spider --no-check-certificate http://localhost:6333/healthz \
    || exit 1

# 7. Data directory: Qdrant writes collection snapshots and WAL files here.
# This path is the canonical storage location inside the container. Mount
# the named volume 'qdrant_storage' from docker-compose.yml onto this path.
# No VOLUME directive is declared here to avoid an anonymous volume being
# created automatically; the compose file is the single source of truth for
# the volume mount.
WORKDIR /qdrant

# 8. Default command: launch the Qdrant server binary with all env vars.
# The qdrant entrypoint reads QDRANT__* variables to configure the server.
# When using this Dockerfile in a compose service with a 'command:' override,
# you can pass additional arguments (e.g. --snapshot-threads 4).
ENTRYPOINT ["/entrypoint.sh"]
CMD []
