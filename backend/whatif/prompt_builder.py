def build_prompt(nodes: list[dict], edges: list[dict], provider: str) -> str:
    """Convert a diagram (nodes + edges) into a Spanish prompt requesting structured JSON analysis."""
    # Build node id → label map for connection descriptions
    id_to_label: dict[str, str] = {}
    service_lines: list[str] = []

    for node in nodes:
        data = node.get("data", {})
        label = data.get("label", node.get("id", "?"))
        category = data.get("category", "")
        description = data.get("description", "")
        node_id = node.get("id", "")
        id_to_label[node_id] = label
        service_lines.append(f"- {label} ({category}): {description}")

    services_text = "\n".join(service_lines) if service_lines else "- (sin servicios)"

    connection_lines: list[str] = []
    for edge in edges:
        src = id_to_label.get(edge.get("source", ""), edge.get("source", "?"))
        tgt = id_to_label.get(edge.get("target", ""), edge.get("target", "?"))
        connection_lines.append(f"- {src} → {tgt}")

    if connection_lines:
        connections_text = "\n".join(connection_lines)
    else:
        connections_text = "- (sin conexiones explícitas)"

    n = len(nodes)

    return f"""Eres un arquitecto cloud senior experto en {provider}. Analiza la siguiente arquitectura cloud:

PROVEEDOR: {provider}

SERVICIOS ({n} nodo{"s" if n != 1 else ""}):
{services_text}

CONEXIONES:
{connections_text}

Responde ÚNICAMENTE en este formato JSON exacto, sin texto adicional antes ni después, sin markdown:
{{
  "costo": {{
    "nivel": "bajo|medio|alto|muy alto",
    "estimacion_mensual": "descripción breve con rangos en USD por mes",
    "detalle": [
      {{"servicio": "nombre del servicio", "rango_usd": "$X - $Y/mes", "justificacion": "breve razón"}}
    ]
  }},
  "riesgos": [
    {{"titulo": "título corto del riesgo", "descripcion": "descripción del problema y su impacto", "severidad": "baja|media|alta|crítica"}}
  ],
  "sugerencias": [
    {{"titulo": "título corto de la mejora", "descripcion": "qué agregar o cambiar y por qué", "prioridad": "baja|media|alta"}}
  ]
}}

Incluye al menos un elemento en riesgos y uno en sugerencias. Responde en español."""
