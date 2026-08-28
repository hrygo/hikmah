FROM python:3.14-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy workspace and requirements
COPY pyproject.toml .
COPY apps/api apps/api

# Install dependencies using uv
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "hikmah.main:app", "--host", "0.0.0.0", "--port", "8000"]
