FROM mcr.microsoft.com/playwright/python:v1.65.2-noble

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install project dependencies first (better layer caching)
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --upgrade pip && pip install -e ".[dev]"

# Copy the rest of the project
COPY . .

# Default: run offline/unit+contract tests (no external sites required)
CMD ["pytest", "-m", "not live", "-q"]
