FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-cache

COPY . .
RUN uv run python -m scripts.load_universities

FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN addgroup --system uhelper && adduser --system --ingroup uhelper uhelper

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/data /app/data
COPY --from=builder /app/src /app/src
COPY --from=builder /app/main.py /app/main.py

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

RUN chown -R uhelper:uhelper /app

VOLUME ["/app/data"]

USER uhelper

CMD ["python", "main.py"]
