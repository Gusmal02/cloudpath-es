FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
RUN uv pip install --system --no-cache \
    "fastapi>=0.162.0" \
    "uvicorn>=0.54.0" \
    "chromadb>=1.5.9" \
    "pydantic>=2.14.2" \
    "httpx>=0.28.1"

COPY . .

RUN mkdir -p data/questions data/chroma

EXPOSE 8000

CMD ["python", "main.py"]
