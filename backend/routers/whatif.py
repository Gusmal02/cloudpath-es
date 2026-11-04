from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import get_settings
from whatif.ollama_client import OllamaUnavailableError, call_ollama
from whatif.prompt_builder import build_prompt
from whatif.response_parser import parse_whatif_response

router = APIRouter(prefix="/whatif", tags=["whatif"])


class WhatIfRequest(BaseModel):
    nodes: list[dict]
    edges: list[dict]
    provider: str = "AWS"


@router.post("")
async def whatif_analysis(req: WhatIfRequest):
    if not req.nodes:
        raise HTTPException(
            status_code=400,
            detail="El diagrama no tiene nodos. Agrega al menos un servicio antes de analizar.",
        )
    settings = get_settings()
    prompt = build_prompt(req.nodes, req.edges, req.provider)
    try:
        raw = await call_ollama(
            prompt,
            model=settings.ollama_model,
            base_url=settings.ollama_url,
        )
    except OllamaUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="El servicio de IA local no está disponible. Inicia Ollama y ejecuta: ollama pull llama3.2:3b",
        )
    return parse_whatif_response(raw)
