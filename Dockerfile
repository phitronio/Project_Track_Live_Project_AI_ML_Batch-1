# ---------- Stage 1: build dependencies ----------
FROM python:3.12-slim AS builder

# Copy the uv binary from its official image — no install script needed
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Copy ONLY the dependency manifests first (see Section C4 on caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into /app/.venv, without installing our own code yet
RUN uv sync --frozen --no-install-project --no-dev


# ---------- Stage 2: runtime ----------
FROM python:3.12-slim

# Create a non-root user to run the app
RUN groupadd --system app && useradd --system --gid app --create-home app

WORKDIR /app

# Bring the finished virtualenv across from the builder stage
COPY --from=builder /app/.venv /app/.venv

# Put the venv first on PATH so `python` and `uvicorn` resolve to it
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Now copy the application code
COPY --chown=app:app app/ ./app/
COPY --chown=app:app alembic.ini ./alembic.ini ./
COPY --chown=app:app alembic/ ./alembic/

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
