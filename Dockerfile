# syntax=docker/dockerfile:1
# ------------------------------------------------------------------
# Builder stage — installs dependencies with uv into a clean layer
# ------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files first (Docker layer cache)
COPY pyproject.toml uv.lock .python-version ./

# Install runtime deps only (no dev group) into a local .venv
RUN uv sync --frozen --no-dev

# ------------------------------------------------------------------
# Runtime stage — minimal final image
# ------------------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy the populated venv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application source
COPY app/ app/
COPY app.py .

# Make the venv's binaries available on PATH
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
