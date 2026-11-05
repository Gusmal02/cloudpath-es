"""
Validación rápida de mensajes del usuario — Python puro, sin llamadas externas.
Ajusta BLOCKED_PATTERNS para cambiar qué se bloquea.
"""

import re

MAX_MESSAGE_LENGTH = 500

BLOCKED_PATTERNS = [
    r"\b(dame|dime|cu[aá]l es|qu[eé] es)\s+(la\s+)?respuesta\s+correcta\b",
    r"\brespuesta\s+(correcta|es la|es el)\b",
    r"\bignora\s+(estas|tus|las)\s+instrucciones\b",
    r"\bact[uú]a como\b",
    r"\bpretende\s+(ser|que eres)\b",
    r"\bolvida\s+(todo|las instrucciones)\b",
]

_compiled = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]


def check_message(message: str, answered: bool) -> tuple[bool, str | None]:
    """
    Devuelve (allowed, reason).
    allowed=False significa que el mensaje debe bloquearse.
    """
    if not message or not message.strip():
        return False, "El mensaje está vacío."

    if len(message) > MAX_MESSAGE_LENGTH:
        return False, f"El mensaje es demasiado largo (máximo {MAX_MESSAGE_LENGTH} caracteres)."

    if not answered:
        for pattern in _compiled:
            if pattern.search(message):
                return False, "Durante el examen no puedo darte la respuesta directa, pero sí puedo explicarte el concepto."

    return True, None
