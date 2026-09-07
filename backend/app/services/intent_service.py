"""
Clasificador ligero de categorías de intención.

Alimenta el dashboard de métricas con la distribución de temas más
consultados (horarios, precios, matrícula, certificaciones, traslados,
saludos, escalamientos y otros).
"""
from __future__ import annotations

from typing import List, Optional

# Palabras y prefijos por categoría (normalizadas: sin tildes, minúsculas)
_HORARIOS = {
    "horario", "horarios", "jornada", "jornadas", "sabado", "sabados",
    "domingo", "domingos", "noche", "noches", "manana", "mananas",
    "tarde", "tardes", "schedule", "schedules", "weekend", "weekends",
    "saturday", "sunday", "morning", "night",
}
_HORARIOS_PREFIX = ("horari", "jornad", "sabad", "doming")

_PRECIOS = {
    "precio", "precios", "costo", "costos", "vale", "valen", "cuota",
    "cuotas", "pago", "pagos", "descuento", "descuentos", "promocion",
    "promociones", "financiacion", "tarifa", "tarifas", "price", "prices",
    "cost", "costs", "fee", "fees", "tuition", "discount", "discounts",
    "financing", "payment", "beca", "becas", "scholarship",
}
_PRECIOS_PREFIX = ("preci", "cost", "financ", "pago", "descuent", "tarif")

_MATRICULA = {
    "inscripcion", "inscripciones", "matricula", "matriculas", "requisito",
    "requisitos", "proceso", "test", "examen", "enroll", "enrollment",
    "admission", "admissions", "register", "fecha", "fechas", "inicio",
    "inicios", "iniciar", "empezar", "comienzo", "calendario", "periodo",
    "start", "dates",
}
_MATRICULA_PREFIX = ("inscri", "matricul", "fech", "inici", "proces", "enroll")

_CERTIFICACIONES = {
    "certificacion", "certificaciones", "diploma", "diplomas", "toefl",
    "ielts", "mcer", "sena", "certificate", "certificates",
    "certifications",
}
_CERTIFICACIONES_PREFIX = ("certific", "diplom", "toefl", "ielts", "mcer")

_TRASLADOS = {
    "ciudad", "ciudades", "mudar", "mudanza", "traslado", "traslados",
    "reubicacion", "reubicación", "congelar", "congelamiento", "campus",
    "sede", "sedes", "bogota", "medellin", "online", "virtual",
    "presencial", "hibrida", "hybrid", "transfer",
}
_TRASLADOS_PREFIX = ("ciud", "mudan", "traslad", "congel", "sede")

_INTENT_MAP = [
    ("horarios", _HORARIOS, _HORARIOS_PREFIX),
    ("precios", _PRECIOS, _PRECIOS_PREFIX),
    ("matricula", _MATRICULA, _MATRICULA_PREFIX),
    ("certificaciones", _CERTIFICACIONES, _CERTIFICACIONES_PREFIX),
    ("traslados", _TRASLADOS, _TRASLADOS_PREFIX),
]

# Orden canónico para el frontend
INTENT_ORDER = [
    "horarios", "precios", "matricula", "certificaciones",
    "traslados", "saludo", "escalamiento", "otros",
]


def classify_intent_category(
    norm_q: str,
    words: Optional[List[str]] = None,
    is_greeting: bool = False,
    is_grupo_a: bool = False,
    is_escalated: bool = False,
) -> str:
    """
    Returns the metric category for a query: one of INTENT_ORDER.

    Priority: escalamiento > saludo > keywords (horarios, precios, ...) > otros.
    """
    if is_grupo_a or is_escalated:
        return "escalamiento"
    if is_greeting:
        return "saludo"

    words = words or (norm_q.split() if norm_q else [])
    for category, exact, prefixes in _INTENT_MAP:
        if any(w in exact for w in words) or any(
            w.startswith(prefix) for w in words for prefix in prefixes
        ):
            return category
    return "otros"
