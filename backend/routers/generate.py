import json
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from config import get_settings
from whatif.ollama_client import call_ollama, OllamaUnavailableError

router = APIRouter(prefix="/generate", tags=["generate"])

PROVIDER_SERVICES = {
    "AWS": "EC2, S3, RDS, Lambda, CloudFront, IAM, VPC, ECS, DynamoDB, SQS, SNS, CloudWatch",
    "GCP": "Compute Engine, Cloud Storage, Cloud SQL, Cloud Functions, Cloud CDN, IAM, VPC, GKE, Firestore, Pub/Sub, Cloud Monitoring",
    "AZURE": "Virtual Machines, Blob Storage, SQL Database, Azure Functions, CDN, IAM, VNet, AKS, Cosmos DB, Service Bus, Monitor",
}

DOMAINS = {
    "AWS": ["Cloud Concepts", "Security", "Cloud Technology", "Billing and Pricing"],
    "GCP": ["Cloud Concepts", "Storage", "Compute", "Networking", "Security"],
    "AZURE": ["Cloud Concepts", "Core Services", "Security", "Pricing and Support"],
}


class GenerateRequest(BaseModel):
    provider: str = "AWS"
    domain: str | None = None
    count: int = 5


def _build_prompt(provider: str, domain: str | None, count: int) -> str:
    services = PROVIDER_SERVICES.get(provider, PROVIDER_SERVICES["AWS"])
    domains = DOMAINS.get(provider, DOMAINS["AWS"])
    domain_hint = f'del dominio "{domain}"' if domain else f"de los dominios: {', '.join(domains)}"

    return f"""Genera exactamente {count} preguntas de práctica para el examen de certificación {provider} Cloud Practitioner, {domain_hint}.

Servicios relevantes: {services}.

Responde SOLO con un array JSON válido, sin texto adicional, sin markdown. Formato exacto:
[
  {{
    "question": "Texto completo de la pregunta",
    "options": ["Opción A", "Opción B", "Opción C", "Opción D"],
    "correct_index": 0,
    "explanation": "Explicación breve de por qué es correcta y por qué las demás no"
  }}
]

Reglas:
- Cada pregunta tiene exactamente 4 opciones
- correct_index es 0, 1, 2 o 3
- Las preguntas deben ser realistas, basadas en escenarios reales
- En español
- No repitas preguntas obvias
- Genera exactamente {count} preguntas"""


def _salvage_partial_json(text: str) -> list:
    """Intenta rescatar objetos JSON individuales de un array incompleto."""
    objects = []
    for m in re.finditer(r'\{[^{}]*\}', text, re.DOTALL):
        try:
            obj = json.loads(m.group(0))
            if "question" in obj and "options" in obj:
                objects.append(obj)
        except json.JSONDecodeError:
            pass
    return objects


def _parse_questions(raw: str, provider: str, domain: str | None) -> list[dict]:
    text = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE).strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if not match:
        # Try salvaging individual objects
        questions = _salvage_partial_json(text)
        if not questions:
            raise ValueError("No se encontró un array JSON en la respuesta")
    else:
        try:
            questions = json.loads(match.group(0))
        except json.JSONDecodeError:
            # Partial JSON — try to salvage complete objects
            questions = _salvage_partial_json(match.group(0))
            if not questions:
                raise
    result = []
    for i, q in enumerate(questions):
        if not all(k in q for k in ("question", "options", "correct_index")):
            continue
        result.append({
            "id": f"ai-{provider.lower()}-{domain or 'general'}-{i}".replace(" ", "-"),
            "provider": provider,
            "domain": domain or "General",
            "question": q["question"],
            "options": q["options"],
            "correct_index": int(q["correct_index"]),
            "explanation": q.get("explanation", ""),
            "ai_generated": True,
        })
    return result


@router.post("/questions")
async def generate_questions(req: GenerateRequest):
    if req.count < 1 or req.count > 20:
        raise HTTPException(400, "count debe estar entre 1 y 20")
    if req.provider not in PROVIDER_SERVICES:
        raise HTTPException(400, f"provider debe ser uno de: {', '.join(PROVIDER_SERVICES)}")

    settings = get_settings()
    prompt = _build_prompt(req.provider, req.domain, req.count)

    try:
        raw = await call_ollama(
            prompt,
            model=settings.ollama_model,
            base_url=settings.ollama_url,
            timeout=120.0,
        )
    except OllamaUnavailableError:
        raise HTTPException(
            503,
            "Ollama no está disponible. Instálalo desde https://ollama.com y ejecuta: ollama pull llama3.2:3b",
        )

    try:
        questions = _parse_questions(raw, req.provider, req.domain)
    except Exception as e:
        raise HTTPException(422, f"No se pudo parsear la respuesta de la IA: {e}")

    if not questions:
        raise HTTPException(422, "La IA no generó preguntas válidas")

    return {"questions": questions, "count": len(questions), "model": settings.ollama_model}
