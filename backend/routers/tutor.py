from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from config import get_settings
from tutor.prompt_builder import TutorContext, build_system_prompt
from tutor.guardrails import check_message
from tutor.ollama_chat import call_ollama_chat
from whatif.ollama_client import OllamaUnavailableError

router = APIRouter(prefix="/tutor", tags=["tutor"])

MAX_HISTORY = 6  # últimos N mensajes enviados al modelo (3 intercambios)


class TutorContextRequest(BaseModel):
    page: str | None = None
    provider: str | None = None
    domain: str | None = None
    question_text: str | None = None
    question_options: list[str] = Field(default_factory=list)
    answered: bool = False
    canvas_services: list[str] = Field(default_factory=list)


class ChatMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    context: TutorContextRequest
    history: list[ChatMessage] = Field(default_factory=list)


@router.post("/chat")
async def tutor_chat(req: ChatRequest):
    allowed, reason = check_message(req.message, req.context.answered)
    if not allowed:
        return {"reply": reason, "blocked": True, "block_reason": reason}

    ctx = TutorContext(
        page=req.context.page,
        provider=req.context.provider,
        domain=req.context.domain,
        question_text=req.context.question_text,
        question_options=req.context.question_options,
        answered=req.context.answered,
        canvas_services=req.context.canvas_services,
    )
    system_prompt = build_system_prompt(ctx)

    trimmed_history = [{"role": m.role, "content": m.content} for m in req.history[-MAX_HISTORY:]]
    trimmed_history.append({"role": "user", "content": req.message})

    settings = get_settings()
    try:
        reply = await call_ollama_chat(
            system_prompt=system_prompt,
            messages=trimmed_history,
            model=settings.ollama_model,
            base_url=settings.ollama_url,
        )
    except OllamaUnavailableError:
        raise HTTPException(
            503,
            "Ollama no está disponible. Instálalo desde https://ollama.com y ejecuta: ollama pull llama3.2:3b",
        )

    return {"reply": reply, "blocked": False, "block_reason": None}
