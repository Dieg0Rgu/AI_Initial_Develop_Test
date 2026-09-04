from __future__ import annotations
import re
import unicodedata
from typing import Dict, Any, Tuple, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/nonsense", tags=["Out of Scope & Nonsense Filter"])

OUT_OF_SCOPE_TOPICS = [
    {
        "category": "Personajes Históricos / Políticos",
        "examples": ["¿Quién es Adolf Hitler?", "¿Quién fue Napoleón?", "Política nacional o internacional"],
        "reason": "El asistente está especializado exclusivamente en los programas académicos, sedes y admisiones de Gastroteacher."
    },
    {
        "category": "Recetas Culinarias Particulares",
        "examples": ["Pásame la receta de lasagna", "¿Cómo preparar sushi?", "Ingredientes para ajíaco"],
        "reason": "Gastroteacher enseña inglés técnico para cocina y hotelería, no es un recetario ni chef virtual de cocina diaria."
    },
    {
        "category": "Criptomonedas / Inversiones / Apuestas",
        "examples": ["¿Cómo compro Bitcoin?", "¿Qué opinas del trading?", "Casinos online"],
        "reason": "Temáticas financieras externas totalmente ajenas a la academia."
    },
    {
        "category": "Programación / Desarrollo de Software",
        "examples": ["Escribe un script en Python", "Ayuda con React", "Corrige este código"],
        "reason": "Gastroteacher no ofrece cursos de informática ni programación."
    }
]

# Patterns and keywords for high-speed lexical detection
HISTORICAL_POLITICAL_PATTERNS = [
    "hitler", "adolf hitler", "stalin", "mussolini", "napoleon", "lenin",
    "guerra mundial", "nazismo", "comunismo", "partido politico", "elecciones presidenciales"
]

RECIPE_PATTERNS = [
    "pasame la receta", "dame la receta", "receta de", "como se prepara",
    "como preparar", "como cocinar", "como hacer una sopa", "como hacer un pastel",
    "ingredientes para", "preparacion de", "give me the recipe", "recipe for",
    "recipe of", "how to cook", "how to prepare", "ingredients for"
]

EXTERNAL_TECH_PATTERNS = [
    "codigo python", "script en python", "programar en", "javascript", "react", "html",
    "bitcoin", "crypto", "criptomoneda", "trading", "forex", "apuestas"
]


def normalize_str(text: str) -> str:
    nfkd = unicodedata.normalize('NFKD', text)
    clean = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()
    return re.sub(r'[^\w\s]', '', clean)


def check_out_of_scope(query: str, language: str = "es") -> Tuple[bool, Optional[str]]:
    """
    Evaluates if user query is out of scope (historical figures, cooking recipes, crypto, coding, etc.).
    Returns (True, message) if out-of-scope, else (False, None).
    """
    norm = normalize_str(query)
    lang = (language or "es").lower()

    # 1. Historical / Political figures
    if any(p in norm for p in HISTORICAL_POLITICAL_PATTERNS):
        if lang == "en":
            msg = (
                "⚠️ **Out-of-Scope Query**: I am an assistant specialized exclusively in Gastroteacher "
                "(English programs for Hospitality & Culinary Arts, schedules, tuition, and enrollment). "
                "I do not provide historical, biographical, or political information."
            )
        else:
            msg = (
                "⚠️ **Consulta Fuera de Alcance**: Soy el asistente especializado exclusivamente en Gastroteacher "
                "(programas de inglés para gastronomía y hotelería, costos, horarios, sedes y matrículas). "
                "No brindo información biográfica, histórica ni de política general."
            )
        return True, msg

    # 2. Cooking recipes (clarify Gastroteacher teaches vocational English, not a recipe book)
    if any(p in norm for p in RECIPE_PATTERNS):
        if lang == "en":
            msg = (
                "🍳 **Gastroteacher Academy Scope**: Gastroteacher teaches **Vocational Culinary English** "
                "(kitchen communication, front-of-house service, international menus, and bar terminology), "
                "not cooking recipes. If you want to master kitchen English to work internationally, let us know!"
            )
        else:
            msg = (
                "🍳 **Alcance Institucional de Gastroteacher**: En Gastroteacher enseñamos **Inglés Vocacional Culinario** "
                "(comunicación en cocina, servicio de mesa, brigadas internacionales y hospitalidad), no recetas de cocina individuales. "
                "¿Te gustaría conocer nuestros cursos de inglés para gastronomía para impulsar tu carrera culinaria en el exterior?"
            )
        return True, msg

    # 3. Programming or Crypto
    if any(p in norm for p in EXTERNAL_TECH_PATTERNS):
        if lang == "en":
            msg = (
                "⚠️ **Topic Not Supported**: I can only assist with Gastroteacher language programs, "
                "placement tests, and enrollment procedures."
            )
        else:
            msg = (
                "⚠️ **Temática Fuera de Ámbito**: Mi conocimiento se enfoca exclusivamente en los cursos de inglés, "
                "sedes, aranceles y certificaciones de Gastroteacher."
            )
        return True, msg

    return False, None


class CheckQueryRequest(BaseModel):
    query: str = Field(..., description="Texto de la consulta a verificar")
    language: Optional[str] = Field("es", description="Idioma ('es' o 'en')")


@router.get("")
async def get_out_of_scope_policy() -> Dict[str, Any]:
    """
    Returns guidance and examples of out-of-scope queries filtered before reaching LLM models.
    """
    return {
        "status": "active",
        "service": "Gastroteacher Out-of-Scope & Nonsense Filter",
        "purpose": "Filtrar y responder velozmente a consultas no pertinentes sin consumir llamadas a la IA o base de datos.",
        "institutional_scope": "Academia Gastroteacher: Cursos de Inglés General y Culinario, Precios, Horarios, Sedes (Bogotá y Medellín) y Matrículas.",
        "out_of_scope_categories": OUT_OF_SCOPE_TOPICS,
        "sample_filtered_queries": [
            "¿Quién es Adolf Hitler?",
            "Pásame la receta de la torta de chocolate",
            "¿Cómo programar en Python?",
            "¿Cuánto vale el Bitcoin hoy?"
        ]
    }


@router.post("/check")
async def evaluate_query(payload: CheckQueryRequest) -> Dict[str, Any]:
    """
    Direct endpoint to evaluate whether a text belongs to out-of-scope topics.
    """
    is_oos, message = check_out_of_scope(payload.query, payload.language)
    return {
        "query": payload.query,
        "is_out_of_scope": is_oos,
        "response_message": message
    }
