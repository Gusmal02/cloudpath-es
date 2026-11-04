from whatif.prompt_builder import build_prompt


def test_prompt_includes_service_labels():
    nodes = [
        {"id": "n1", "data": {"label": "EC2", "category": "Cómputo", "description": "Instancias virtuales"}},
        {"id": "n2", "data": {"label": "RDS", "category": "Base de datos", "description": "Bases de datos relacionales"}},
    ]
    edges = [{"source": "n1", "target": "n2"}]
    prompt = build_prompt(nodes, edges, "AWS")
    assert "EC2" in prompt
    assert "RDS" in prompt
    assert "AWS" in prompt


def test_prompt_mentions_connections():
    nodes = [
        {"id": "n1", "data": {"label": "Lambda", "category": "Cómputo", "description": "Funciones serverless"}},
        {"id": "n2", "data": {"label": "DynamoDB", "category": "Base de datos", "description": "NoSQL serverless"}},
    ]
    edges = [{"source": "n1", "target": "n2"}]
    prompt = build_prompt(nodes, edges, "AWS")
    assert "Lambda" in prompt
    assert "DynamoDB" in prompt
    assert any(w in prompt.lower() for w in ["conecta", "conectado", "→", "->"])


def test_prompt_requests_three_sections():
    nodes = [{"id": "n1", "data": {"label": "S3", "category": "Almacenamiento", "description": "Objetos"}}]
    prompt = build_prompt(nodes, [], "AWS")
    assert "costo" in prompt.lower()
    assert "riesgo" in prompt.lower()
    assert "sugerencia" in prompt.lower()
