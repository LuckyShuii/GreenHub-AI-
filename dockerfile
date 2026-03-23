FROM python:3.13-slim-trixie

WORKDIR /greener
COPY ./src ./src 
COPY main.py .
COPY .env .
COPY pyproject.toml .
COPY uv.lock .
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN uv sync
CMD uv run python main.py

