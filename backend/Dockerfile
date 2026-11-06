FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install uv --quiet

# Copy dependency manifest first for layer caching
COPY pyproject.toml uv.lock ./

# Install all project dependencies from the lock file (no pytest in prod)
RUN uv pip install --system --no-cache \
    "fastapi>=0.162.0" \
    "uvicorn>=0.54.0" \
    "chromadb>=1.5.9" \
    "pydantic>=2.14.2" \
    "httpx>=0.28.1"

COPY . .

RUN mkdir -p data/questions data/chroma data/db

EXPOSE 8000

CMD ["python", "main.py"]
