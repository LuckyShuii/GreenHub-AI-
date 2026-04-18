FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /greener

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync --no-dev

COPY ./src ./src 
COPY main.py .

CMD ["uv", "run", "python", "main.py"]
