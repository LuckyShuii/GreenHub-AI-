FROM python:3.13-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /greener
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen --no-install-project

COPY ./src ./src
COPY main.py ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen

FROM python:3.13-slim-trixie
WORKDIR /greener
COPY --from=builder /greener/.venv /greener/.venv
COPY --from=builder /greener/src /greener/src
COPY --from=builder /greener/main.py /greener/main.py
ENV PATH="/greener/.venv/bin:$PATH"

ENTRYPOINT ["python", "main.py"]
