import httpx


class OllamaUnavailableError(Exception):
    pass


async def call_ollama(
    prompt: str,
    model: str = "llama3.2:3b",
    base_url: str = "http://localhost:11434",
    timeout: float = 60.0,
) -> str:
    """Call Ollama generate endpoint. Raises OllamaUnavailableError if unreachable or timeout."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(
                f"{base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": False},
            )
            r.raise_for_status()
            return r.json()["response"]
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        raise OllamaUnavailableError(str(e)) from e
