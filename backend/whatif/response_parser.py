import json
import re


def parse_whatif_response(raw: str) -> dict:
    """Extract JSON from LLM response. Tolerates markdown fences. Never raises."""
    text = raw.strip()

    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
    text = text.strip()

    # Try to find the first {...} block in case there's preamble text
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "costo": {
                "nivel": "desconocido",
                "estimacion_mensual": "No se pudo parsear la respuesta del modelo",
                "detalle": [],
            },
            "riesgos": [],
            "sugerencias": [],
            "_parse_error": True,
        }
