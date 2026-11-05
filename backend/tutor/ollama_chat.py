"""
Cliente de chat multi-turno para Ollama.
Usa /api/chat (distinto de /api/generate que usa WhatIf).
"""

import httpx
from whatif.ollama_client import OllamaUnavailableError


async def call_ollama_chat(
    system_prompt: str,
    messages: list[dict],
    model: str = "llama3.2:3b",
    base_url: str = "http://localhost:11434",
    timeout: float = 90.0,
) -> str:
    """
    Llama a /api/chat de Ollama con historial de mensajes.
    messages: lista de {"role": "user"|"assistant", "content": str}
    Raises OllamaUnavailableError si Ollama no está disponible.
    """
    payload = {
        "model": model,
        "stream": False,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(f"{base_url}/api/chat", json=payload)
            r.raise_for_status()
            return r.json()["message"]["content"]
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        raise OllamaUnavailableError(str(e)) from e
