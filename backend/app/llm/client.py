from __future__ import annotations
import re
import time
import unicodedata
from typing import Dict, Any, Tuple, Optional
import httpx

try:
    from app.config import settings
    from app.llm.prompts import build_rag_prompt
    from app.utils.logger import logger
except ImportError:
    from backend.app.config import settings
    from backend.app.llm.prompts import build_rag_prompt
    from backend.app.utils.logger import logger

# Keyword sets for deterministic classification and safety boundaries
PROFANITY_KEYWORDS = {
    "gonorrea", "hp", "hdp", "puta", "puto", "mierda", "marica", "maricon",
    "pirobo", "malparido", "carechimba", "chimba", "verga", "pendejo", "idiota",
    "estupido", "imbecil", "culiao", "fuck", "shit", "bitch", "asshole", "bastard",
    "dick", "pussy", "cunt", "motherfucker", "fucker", "damn"
}

KEYBOARD_PATTERNS = [
    "asdf", "qwer", "zxcv", "hjkl", "jkl;", "1234", "abcd", "qazw", "wsxe",
    "edcr", "rfvt", "tgby", "yhn", "ujm", "ik,", "ol.", "plñ"
]

COMMON_NAMES = {
    "diego", "valentina", "carlos", "juancha", "viviana", "maria", "juan", "andres",
    "camila", "felipe", "laura", "daniel", "mateo", "sofia", "santiago", "alejandro",
    "sebastian", "nicolas", "natalia", "gabriela", "paula", "juliana", "david", "john",
    "sarah", "michael", "emily", "james", "robert", "emma", "olivia", "william"
}

GREETING_WORDS_ES = {
    "hola", "buenos dias", "buenas tardes", "buenas noches", "saludos", "que mas",
    "buenas", "que tal", "buen día", "buenos días", "hola buenos dias", "hola buenas tardes",
    "pana", "parce", "amigo"
}

GREETING_WORDS_EN = {
    "hello", "hi", "good morning", "good afternoon", "good evening", "greetings", "howdy",
    "bro", "dude", "buddy", "friend", "hi there", "hello there"
}

NONSENSE_KEYWORDS_ES = {
    "pizza", "hamburguesa", "perro", "gato", "auto", "carro", "moto", "computador", "pc",
    "futbol", "musica", "comida", "almuerzo", "cena", "plato", "asdf", "test_nonsense",
    "manzana", "agua", "cerveza", "vino", "ropa", "zapato", "clima", "chiste", "mesa", "silla",
    "cosa", "objeto", "ventana", "puerta", "lapiz", "cuaderno"
}

NONSENSE_KEYWORDS_EN = {
    "burger", "dog", "cat", "car", "motorcycle", "computer", "pc",
    "soccer", "football", "music", "food", "lunch", "dinner", "plate",
    "apple", "water", "beer", "wine", "clothes", "shoes", "weather", "joke", "table", "chair",
    "pizza", "whatever", "nonsense", "thing", "stuff", "building", "window", "door", "pencil"
}

IN_SCOPE_KEYWORDS = {
    "precio", "precios", "costo", "costos", "vale", "valen", "cuota", "cuotas", "pago", "pagos",
    "descuento", "descuentos", "promocion", "promociones", "financ", "financiacion", "tarifa", "tarifas",
    "price", "prices", "cost", "costs", "fee", "fees", "tuition", "discount", "discounts", "financing", "payment",
    "horario", "horarios", "sabado", "sabados", "domingo", "domingos", "jornada", "jornadas", "noche", "noches", "manana", "mananas", "tarde", "tardes",
    "schedule", "schedules", "weekend", "weekends", "weekday", "weekdays", "saturday", "sunday", "hours",
    "certific", "certificacion", "certificaciones", "diploma", "diplomas", "toefl", "ielts", "mcer", "sena", "certificate", "certificates", "certifications",
    "inscri", "inscripcion", "inscripciones", "matricula", "matriculas", "proceso", "requisito", "requisitos", "test", "examen", "enroll", "enrollment", "admission", "admissions", "register",
    "fecha", "fechas", "inicio", "inicios", "iniciar", "empezar", "comienzo", "calendario", "periodo", "start", "dates",
    "curso", "cursos", "programa", "programas", "clase", "clases", "modulo", "modulos", "course", "courses", "class", "classes", "ingles", "english", "gastronomy", "gastronomia",
    "sede", "sedes", "campus", "bogota", "medellin", "online", "virtual", "presencial", "hibrida", "hybrid",
    "ciudad", "ciudades", "mudar", "mudanza", "traslado", "traslados", "reubicacion", "reubicación", "congelar", "congelamiento"
}

INJECTION_PHRASES = [
    "ignora las instrucciones", "ignora todas las instrucciones", "ignore all previous",
    "ignore previous instructions", "olvida tus instrucciones", "olvida las reglas",
    "cambia de rol", "ahora eres un", "actua como", "actúa como", "developer mode",
    "jailbreak", "system prompt", "revela tu prompt", "muestra tu prompt", "dime tus instrucciones",
    "repeat the words above", "write the first 50 words", "dan mode", "vulnerar", "hackear",
    "modo desarrollador", "prompt injection", "system warning", "bypass"
]

GREETING_WORDS = GREETING_WORDS_ES | GREETING_WORDS_EN
NONSENSE_KEYWORDS = NONSENSE_KEYWORDS_ES | NONSENSE_KEYWORDS_EN


def normalize_simple(text: str) -> str:
    nfkd = unicodedata.normalize('NFKD', text)
    clean = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()
    return re.sub(r'[^\w\s]', '', clean)


def is_gibberish(text: str) -> bool:
    norm = normalize_simple(text)
    if not norm:
        return True
    if not any(c.isalnum() for c in text):
        return True
    words = norm.split()
    for w in words:
        if any(p in w for p in KEYBOARD_PATTERNS) and len(w) >= 4:
            return True
        if len(w) >= 6 and re.search(r'[bcdfghjklmnpqrstvwxyz]{6,}', w):
            return True
        if len(w) >= 5 and not any(v in w for v in "aeiouy"):
            return True
    return False


def contains_profanity(text: str) -> bool:
    norm = normalize_simple(text)
    words = norm.split()
    return any(w in PROFANITY_KEYWORDS for w in words)


def is_prompt_injection_or_leakage(text: str) -> bool:
    norm = normalize_simple(text)
    t_lower = text.lower()
    return any(p in t_lower or p in norm for p in INJECTION_PHRASES)


def classify_grupo_a_intent(text: str) -> Optional[str]:
    """
    Evaluates if user query belongs to GRUPO A (Mandatory Human Escalation).
    Returns the intent type ('REFUND', 'TECHNICAL', 'CORPORATE', 'IMMIGRATION', 'RECIPES', 'HUMAN', 'INJECTION') or None.
    """
    t_lower = text.lower()
    norm = normalize_simple(text)
    words = norm.split()

    if is_prompt_injection_or_leakage(text):
        return "INJECTION"

    # 1. Reembolsos / Cancelaciones / Reclamaciones de Dinero
    refund_indicators = [
        "reembolso", "devolucion", "devolver", "cancelar", "cancelacion", "exijo la devolucion",
        "exijo mi dinero", "devolucion total", "devolucion de mi dinero", "cuenta bancaria",
        "transfirieron de empresa", "no podre asistir", "no puedo asistir", "reclamacion",
        "reclamo", "disputa", "dinero devuelto", "restitucion", "anular pago", "anulacion",
        "refund", "chargeback", "cancel subscription", "money back"
    ]
    if any(ind in t_lower or ind in norm for ind in refund_indicators):
        return "REFUND"

    # 2. Soporte Técnico de Plataforma / Errores 403 / Acceso al Campus Virtual
    tech_indicators = [
        "error 403", "403", "acceso denegado", "campus virtual", "grabacion", "grabaciones",
        "login", "credenciales", "contrasena", "contraseña", "bloqueado", "no me deja entrar",
        "no puedo entrar", "falla tecnica", "falla de login", "problema con el campus",
        "acceso a plataforma", "technical issue", "access denied", "password reset"
    ]
    if any(ind in t_lower or ind in norm for ind in tech_indicators):
        return "TECHNICAL"

    # 3. Convenios Corporativos / Tarifas Empresariales / Factura a Crédito
    corp_indicators = [
        "convenio corporativo", "tarifa corporativa", "empresarial", "factura a 60", "factura a 30",
        "facturacion a credito", "cotizacion empresarial", "crepes & waffles", "crepes and waffles",
        "crepes", "recursos humanos", "50 cocineros", "capacitar al equipo", "alianza corporativa",
        "propuesta formal", "tarifa corporativa del 50%", "descuento corporativo", "corporate agreement",
        "b2b quote", "company training"
    ]
    if any(ind in t_lower or ind in norm for ind in corp_indicators):
        return "CORPORATE"

    # 4. Trámites Migratorios / Visas / Empleo Exterior / Patrocinio
    imm_indicators = [
        "visa", "visado", "migratorio", "embajada", "trabajo en el extranjero", "empleo en crucero",
        "patrocinio laboral", "work visa", "immigration", "pedir visa", "tramitar visa", "sacar visa"
    ]
    if any(ind in t_lower or ind in norm for ind in imm_indicators):
        return "IMMIGRATION"

    # 5. Recetas Prácticas / Cocina no lingüística / Vinos
    recipe_indicators = [
        "salsa bearnesa", "bearnesa", "preparar salsa", "receta", "recetas", "vinos chilenos",
        "vino chileno", "maridaje", "como preparar pizza", "como cocinar", "recipe", "cook practical"
    ]
    if any(ind in t_lower or ind in norm for ind in recipe_indicators):
        return "RECIPES"

    # 6. Solicitud Explícita de Asesor Humano
    human_indicators = [
        "asesor humano", "hablar con humano", "persona real", "agente humano", "atencion al cliente",
        "representante humano", "quiero un asesor", "comunicarme con una persona", "speak to human",
        "human agent", "live representative", "equipo humano"
    ]
    if any(ind in t_lower or ind in norm for ind in human_indicators):
        return "HUMAN"

    # 7. Otros temas complejos fuera de alcance explícitos
    off_scope_indicators = ["bitcoin", "crypto", "criptomoneda", "criptomonedas", "trading", "mecanica", "abogado", "yamaha", "carburador"]
    if any(ind in t_lower or ind in norm for ind in off_scope_indicators) and len(words) >= 2:
        return "HUMAN"

    return None


def is_grupo_a_intent(text: str) -> bool:
    norm = normalize_simple(text)
    words = norm.split()

    # If it's isolated 1-2 words nonsense or pure greeting, let standard nonsense/greeting handler process it
    if len(words) <= 2 and (norm in NONSENSE_KEYWORDS or any(w in NONSENSE_KEYWORDS for w in words)) and not any(ind in norm for ind in ["403", "reembolso", "devolucion", "crepes", "visa", "bearnesa"]):
        return False

    return classify_grupo_a_intent(text) is not None


def has_exact_keyword(words: list[str], keyword_set: set[str]) -> bool:
    for w in words:
        if w in keyword_set or any(w.startswith(kw) for kw in ["financ", "certific", "inscri", "matricul", "program", "curs", "horari", "preci", "fech", "inici", "clase", "ciud", "mudan", "traslad"]):
            return True
    return False


def extract_name_intent(query: str) -> Optional[str]:
    raw = query.strip()
    clean_words = normalize_simple(raw).split()

    if contains_profanity(raw) or is_gibberish(raw) or is_prompt_injection_or_leakage(raw) or is_grupo_a_intent(raw):
        return None

    patterns = [
        r'^(?:hola\s*,?\s*)?(?:soy|me llamo|mi nombre es)\s+([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)$',
        r'^(?:hello\s*,?\s*|hi\s*,?\s*)?(?:i am|i\'m|my name is)\s+([a-zA-Z\s]+)$',
    ]
    for pattern in patterns:
        m = re.match(pattern, raw, re.IGNORECASE)
        if m:
            name = m.group(1).strip()
            name_words = normalize_simple(name).split()
            if 2 <= len(name) <= 40 and not has_exact_keyword(name_words, IN_SCOPE_KEYWORDS) and not any(w in PROFANITY_KEYWORDS for w in name_words):
                return name.title()

    if len(clean_words) == 1:
        w = clean_words[0]
        if w in COMMON_NAMES and w not in GREETING_WORDS and w not in NONSENSE_KEYWORDS:
            return raw.strip().title()

    if 2 <= len(clean_words) <= 3:
        clean_text = " ".join(clean_words)
        if (
            all(w.isalpha() for w in clean_words)
            and any(w in COMMON_NAMES for w in clean_words)
            and clean_text not in GREETING_WORDS
            and clean_text not in NONSENSE_KEYWORDS
            and not any(w in clean_words for w in NONSENSE_KEYWORDS_EN)
            and not any(w in clean_words for w in NONSENSE_KEYWORDS_ES)
            and not any(w in PROFANITY_KEYWORDS for w in clean_words)
            and not has_exact_keyword(clean_words, IN_SCOPE_KEYWORDS)
            and not is_grupo_a_intent(raw)
            and not is_gibberish(clean_text)
            and len(clean_text) >= 4
        ):
            return " ".join(raw.split()).title()

    return None


def is_english_query(norm_q: str, words: list[str], language: Optional[str] = None) -> bool:
    if language == 'en':
        return True
    if language == 'es':
        return False
    en_signals = {
        "hello", "hi", "good", "morning", "afternoon", "evening", "what", "how", "when",
        "where", "much", "cost", "price", "prices", "schedules", "classes", "enrollment",
        "course", "courses", "apple", "burger", "dog", "cat", "car", "computer", "bro",
        "dude", "table", "chair", "shoes", "window", "door"
    }
    return any(w in en_signals for w in words) or norm_q in GREETING_WORDS_EN or norm_q in NONSENSE_KEYWORDS_EN


def clean_markdown_response(text: str) -> str:
    """
    Cleans up LLM/API responses:
    - Removes reasoning tags (<think>...</think>).
    - Converts markdown tables into clean, readable bullet points without pipes '|'.
    - Removes markdown horizontal dividers (---, ***, ___).
    - Collapses 3+ consecutive newlines to 2.
    - Removes empty or orphan list dashes.
    - Balances unclosed formatting tags (** or `) to prevent eaten text in frontend.
    - Trims unnecessary whitespace.
    - Strips stray pipe characters and trims whitespace.
    """
    if not text:
        return ""

    # 1. Strip reasoning blocks
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

    # 2. Strip horizontal divider lines
    # 2. Convert markdown tables into clean bullet points
    lines = text.split('\n')
    cleaned_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Check if line is a table divider line like |---|---| or |:---|:---| or ---|---
        if re.match(r'^[\|\s\-:]+$', stripped) and '-' in stripped and ('|' in stripped or len(stripped) >= 3):
            if '|' in stripped:
                i += 1
                continue

        # Check if this line looks like a table row (has pipes and cells)
        if '|' in stripped:
            cells = [c.strip() for c in stripped.strip('|').split('|') if c.strip()]
            # Look ahead: is the next line a table divider line? E.g. |---|---|
            is_followed_by_divider = False
            if i + 1 < len(lines):
                next_stripped = lines[i + 1].strip()
                if re.match(r'^[\|\s\-:]+$', next_stripped) and '-' in next_stripped and '|' in next_stripped:
                    is_followed_by_divider = True

            if is_followed_by_divider:
                # Table header row: skip it
                i += 1
                continue

            if len(cells) >= 2:
                bullet = f"- **{cells[0]}**: {cells[1]}"
                if len(cells) > 2 and any(cells[2:]):
                    bullet += f" ({', '.join([c for c in cells[2:] if c])})"
                cleaned_lines.append(bullet)
                i += 1
                continue
            elif len(cells) == 1:
                cleaned_lines.append(f"- {cells[0]}")
                i += 1
                continue

        # Non-table line with stray pipe characters: remove pipes cleanly
        if '|' in line:
            clean_l = re.sub(r'^\s*\|\s*', '', line)
            clean_l = re.sub(r'\s*\|\s*$', '', clean_l)
            clean_l = clean_l.replace('|', ' - ')
            cleaned_lines.append(clean_l)
        else:
            cleaned_lines.append(line)

        i += 1

    text = '\n'.join(cleaned_lines)

    # 3. Strip horizontal divider lines
    text = re.sub(r'^[ \t]*[-*_]{3,}[ \t]*$', '', text, flags=re.MULTILINE)

    # 3. Strip orphan bullet dashes
    # 4. Strip orphan bullet dashes
    text = re.sub(r'^[ \t]*[-*]\s*$', '', text, flags=re.MULTILINE)

    # 4. Collapse 3+ newlines to 2
    # 5. Collapse 3+ newlines to 2
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 5. Balance unclosed bold or backtick tags to prevent formatting corruption
    # 6. Balance unclosed bold or backtick tags to prevent formatting corruption
    if text.count("**") % 2 != 0:
        text += "**"
    if text.count("```") % 2 != 0:
        text += "\n```"
    elif text.count("`") % 2 != 0:
        text += "`"

    return text.strip()


class LLMClient:
    def __init__(self, base_url: str = None, model: str = None, **kwargs):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS

        # External Providers & Models Configuration
        self.providers = list(getattr(settings, "LLM_PROVIDERS", ["groq", "gemini", "openai", "ollama"]))
        self.groq_api_keys = list(getattr(settings, "GROQ_API_KEYS", []))
        self.groq_model = getattr(settings, "GROQ_MODEL", "llama-3.1-8b-instant")
        self.gemini_api_keys = list(getattr(settings, "GEMINI_API_KEYS", []))
        self.gemini_model = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        self.openai_api_keys = list(getattr(settings, "OPENAI_API_KEYS", []))
        self.openai_model = getattr(settings, "OPENAI_MODEL", "gpt-3.5-turbo")
        self.openai_base_url = getattr(settings, "OPENAI_BASE_URL", "https://api.openai.com/v1")

        # Circular rotation index per provider
        self._provider_indices: Dict[str, int] = {
            "groq": 0,
            "gemini": 0,
            "openai": 0
        }

    async def is_healthy(self) -> bool:
        """Check if local Ollama daemon is reachable and running."""
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=2.0) as client:
                res = await client.get("/api/tags")
                return res.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    def is_cloud_available(self) -> bool:
        """Returns True if external providers have configured API keys."""
        return bool(self.groq_api_keys or self.gemini_api_keys or self.openai_api_keys)

    def _fallback_generate(self, query: str, context: str, is_relevant: bool, language: str = 'es') -> Tuple[str, bool, Dict[str, int]]:
        """
        Deterministic, grounded response generator implementing strict Grupo A / Grupo B classification.
        """
        norm_q = normalize_simple(query)
        words = norm_q.split()
        approx_prompt_tokens = max(10, len(query + context) // 4)
        is_en = is_english_query(norm_q, words, language)
        grupo_a = classify_grupo_a_intent(query)
        has_vulgarity = contains_profanity(query)
        gibberish = is_gibberish(query)

        # ---------------------------------------------------------
        # GRUPO A: ESCALAMIENTO HUMANO INMEDIATO CON EMPATÍA PUNTUAL
        # ---------------------------------------------------------
        if grupo_a:
            logger.info(f"Classified query as GRUPO A Escalation (intent={grupo_a}): '{query}'")

            if grupo_a == "REFUND":
                if is_en:
                    answer = (
                        f"[ESCALATE_HUMAN] I completely understand your situation regarding your cancellation or refund request. "
                        f"To process formal refunds and administrative balance adjustments, your request must be handled directly by our Finance & Admissions Department. "
                        f"Please contact our team at:\n"
                        f"- **Email**: {settings.ESCALATION_EMAIL}\n"
                        f"- **WhatsApp**: {settings.ESCALATION_WHATSAPP}\n"
                        f"- **Business Hours**: {settings.ESCALATION_HOURS}\n"
                        f"Please attach your payment receipt and ID number for expedited processing."
                    )
                else:
                    answer = (
                        f"[ESCALATE_HUMAN] Comprendo completamente tu situación debido al cambio laboral o motivo de cancelación. "
                        f"Para tramitar solicitudes de reembolso y cancelaciones, tu caso debe ser gestionado formalmente por nuestra área administrativa y financiera. "
                        f"Puedes comunicarte directamente con nuestro equipo humano en el correo {settings.ESCALATION_EMAIL} o vía WhatsApp al {settings.ESCALATION_WHATSAPP} "
                        f"(Horario: {settings.ESCALATION_HOURS}) adjuntando tu comprobante de pago para darte pronta solución."
                    )

            elif grupo_a == "TECHNICAL":
                if is_en:
                    answer = (
                        f"[ESCALATE_HUMAN] I am very sorry for the technical inconvenience you are experiencing with platform access or class recordings. "
                        f"To immediately resolve error 403 and validate your credentials, please reach out to our Technical Support Desk at:\n"
                        f"- **Email**: {settings.ESCALATION_EMAIL}\n"
                        f"- **WhatsApp**: {settings.ESCALATION_WHATSAPP}\n"
                        f"- **Business Hours**: {settings.ESCALATION_HOURS}\n"
                        f"Please include your document ID and payment voucher so we can restore your access right away."
                    )
                else:
                    answer = (
                        f"[ESCALATE_HUMAN] Lamento mucho el inconveniente técnico que estás experimentando con el acceso al campus virtual y las grabaciones. "
                        f"Para resolver el error 403 y validar el estado de tus credenciales de inmediato, por favor contacta a nuestra mesa de soporte técnico en {settings.ESCALATION_EMAIL} "
                        f"o vía WhatsApp al {settings.ESCALATION_WHATSAPP} (Horario: {settings.ESCALATION_HOURS}) con tu número de documento y soporte de pago."
                    )

            elif grupo_a == "CORPORATE":
                if is_en:
                    answer = (
                        f"[ESCALATE_HUMAN] Thank you for your interest in training your team with Gastroteacher Academy. "
                        f"For massive corporate agreements, custom B2B pricing, and flexible invoice terms, I am transferring your request to our Corporate Partnerships Commercial Direction. "
                        f"Please contact us at {settings.ESCALATION_EMAIL} or WhatsApp {settings.ESCALATION_WHATSAPP} to coordinate a formal customized proposal."
                    )
                else:
                    answer = (
                        f"[ESCALATE_HUMAN] ¡Hola! Agradecemos el interés en capacitar a tu equipo con nuestros programas de inglés gastronómico. "
                        f"Al tratarse de un convenio corporativo masivo con condiciones especiales de facturación y tarifas empresariales, "
                        f"transferiré tu solicitud a nuestra Dirección Comercial de Alianzas Corporativas. "
                        f"Por favor escríbenos a {settings.ESCALATION_EMAIL} o al WhatsApp {settings.ESCALATION_WHATSAPP} para coordinar una propuesta formal y personalizada."
                    )

            elif grupo_a == "RECIPES":
                if is_en:
                    answer = (
                        f"[ESCALATE_HUMAN] Hello! At Gastroteacher Academy, we specialize exclusively in linguistic training and certification for culinary technical English and hospitality, "
                        f"not in practical cooking recipes or wine pairings through this support channel. "
                        f"If you wish to explore our culinary English syllabus or contact an admissions counselor, feel free to write to us at {settings.ESCALATION_EMAIL}."
                    )
                else:
                    answer = (
                        f"[ESCALATE_HUMAN] ¡Hola! En Gastroteacher Academy nos especializamos en la formación lingüística y certificación en inglés técnico culinario y hospitalidad, "
                        f"not en recetarios ni clases prácticas de cocina directamente por este canal. "
                        f"Si deseas conocer nuestro plan de estudios de inglés gastronómico o contactar a un asesor, puedes escribirnos a {settings.ESCALATION_EMAIL} o al WhatsApp {settings.ESCALATION_WHATSAPP}."
                    )

            elif grupo_a == "IMMIGRATION":
                if is_en:
                    answer = (
                        f"[ESCALATE_HUMAN] Hello! At Gastroteacher Academy we specialize in linguistic training and preparation for international exams (IELTS, TOEFL, Linguaskill) required by embassies, "
                        f"but we do not process consular visas or direct employment sponsorship. "
                        f"For guidance regarding official language certifications or international partnership evaluations, please contact our human advising team at:\n"
                        f"- **Email**: {settings.ESCALATION_EMAIL}\n"
                        f"- **WhatsApp**: {settings.ESCALATION_WHATSAPP}\n"
                        f"- **Hours**: {settings.ESCALATION_HOURS}"
                    )
                else:
                    answer = (
                        f"[ESCALATE_HUMAN] ¡Hola! En Gastroteacher Academy nos especializamos en la formación lingüística y preparación para exámenes oficiales internacionales (IELTS, TOEFL, Linguaskill) exigidos por embajadas, "
                        f"pero no realizamos trámites consulares ni patrocinio directo de visados. "
                        f"Para orientarte sobre certificaciones oficiales o evaluar convenios internacionales con nuestro equipo humano de admisiones, te invito a escribirnos a:\n"
                        f"- **Correo**: {settings.ESCALATION_EMAIL}\n"
                        f"- **WhatsApp**: {settings.ESCALATION_WHATSAPP}\n"
                        f"- **Horario**: {settings.ESCALATION_HOURS}"
                    )

            elif grupo_a == "INJECTION":
                if is_en:
                    answer = (
                        f"[ESCALATE_HUMAN] Hello. As the official virtual advisor for Gastroteacher Academy, "
                        f"my purpose is strictly to assist you with inquiries about our academic programs, schedules, tuition, certifications, and admissions. "
                        f"I am not authorized to modify system directives or change operational roles. "
                        f"If you require specialized assistance, please contact our team at:\n"
                        f"- **Email**: {settings.ESCALATION_EMAIL}\n"
                        f"- **WhatsApp**: {settings.ESCALATION_WHATSAPP}"
                    )
                else:
                    answer = (
                        f"[ESCALATE_HUMAN] Hola. Como asesor virtual de Gastroteacher Academy, "
                        f"mi función exclusiva es orientarte sobre nuestros programas de idiomas, horarios, precios, certificaciones y matrículas. "
                        f"No tengo autorización para modificar directivas internas del sistema ni cambiar de rol. "
                        f"Para consultas administrativas o soporte especializado, te invito a contactar a nuestro equipo humano:\n"
                        f"- **Correo**: {settings.ESCALATION_EMAIL}\n"
                        f"- **WhatsApp**: {settings.ESCALATION_WHATSAPP}"
                    )

            else:  # General HUMAN intent
                if is_en:
                    answer = (
                        f"[ESCALATE_HUMAN] Hello! Thank you for reaching out to Gastroteacher. "
                        f"To assist you with your inquiry regarding '{query}' with a dedicated advisor and human team, "
                        f"please connect directly with our support staff at:\n"
                        f"- **WhatsApp**: {settings.ESCALATION_WHATSAPP}\n"
                        f"- **Email**: {settings.ESCALATION_EMAIL}\n"
                        f"- **Hours**: {settings.ESCALATION_HOURS}"
                    )
                else:
                    answer = (
                        f"[ESCALATE_HUMAN] ¡Hola! Gracias por comunicarte con Gastroteacher. "
                        f"Para atender tu consulta sobre '{query}' de manera personalizada y precisa con un asesor y equipo humano de soporte, "
                        f"te invito a contactar directamente a nuestro equipo en:\n"
                        f"- **WhatsApp / Telegram**: {settings.ESCALATION_WHATSAPP}\n"
                        f"- **Correo**: {settings.ESCALATION_EMAIL}\n"
                        f"- **Horario de atención**: {settings.ESCALATION_HOURS}"
                    )

            tokens = {"prompt_tokens": approx_prompt_tokens, "completion_tokens": len(answer) // 4, "total_tokens": approx_prompt_tokens + (len(answer) // 4)}
            return answer, True, tokens

        # 1. Empty, Symbols Only, Single Punctuation, or Gibberish
        if not norm_q or not any(c.isalnum() for c in query) or gibberish:
            if is_en:
                answer = (
                    "System Notice: The Gastroteacher Virtual Assistant is exclusively designed to answer inquiries from individuals interested in our language and gastronomy academy's academic programs, schedules, pricing, certifications, and admissions.\n\n"
                    "If you are interested in our courses, please ask about:\n"
                    "- Available class schedules (weekdays and weekends)\n"
                    "- Pricing, promotions, and flexible payment plans in COP\n"
                    "- General English or Gastronomy & Hospitality English programs\n"
                    "- Enrollment process and free placement test"
                )
            else:
                answer = (
                    "Aviso del Sistema: El Asistente Virtual de Gastroteacher está diseñado exclusivamente para responder consultas de personas interesadas en los programas académicos, horarios, precios, certificaciones y admisiones de nuestra academia de idiomas y gastronomía.\n\n"
                    "Si deseas información sobre nuestros cursos, por favor indícame tu consulta sobre:\n"
                    "- Horarios de clases disponibles (entre semana y fines de semana)\n"
                    "- Precios, promociones y facilidades de pago en COP\n"
                    "- Programas de Inglés General o Inglés para Gastronomía y Hospitalidad\n"
                    "- Proceso de matrícula y test de nivelación gratuito"
                )
            tokens = {"prompt_tokens": approx_prompt_tokens, "completion_tokens": len(answer) // 4, "total_tokens": approx_prompt_tokens + (len(answer) // 4)}
            return answer, False, tokens

        # 2. Immediate Profanity / Inappropriate Language Interception
        if has_vulgarity:
            if is_en:
                answer = (
                    "System Notice: The Gastroteacher Virtual Assistant is exclusively designed to assist individuals interested in our language and gastronomy academy's academic programs, schedules, pricing, certifications, and admissions.\n\n"
                    "Please maintain respectful communication. If you are interested in our courses, you can ask about:\n"
                    "- Available class schedules (weekdays and weekends)\n"
                    "- Pricing, promotions, and flexible payment plans in COP\n"
                    "- General English or Gastronomy & Hospitality English programs\n"
                    "- Enrollment process and free placement test"
                )
            else:
                answer = (
                    "Aviso del Sistema: El Asistente Virtual de Gastroteacher está diseñado exclusivamente para responder consultas de personas interesadas en los programas académicos, horarios, precios, certificaciones y admisiones de nuestra academia de idiomas y gastronomía.\n\n"
                    "Por favor mantén un lenguaje respetuoso. Si deseas información sobre nuestros cursos, puedes consultar sobre:\n"
                    "- Horarios de clases disponibles (entre semana y fines de semana)\n"
                    "- Precios, promociones y facilidades de pago en COP\n"
                    "- Programas de Inglés General o Inglés para Gastronomía y Hospitalidad\n"
                    "- Proceso de matrícula y test de nivelación gratuito"
                )
            tokens = {"prompt_tokens": approx_prompt_tokens, "completion_tokens": len(answer) // 4, "total_tokens": approx_prompt_tokens + (len(answer) // 4)}
            return answer, False, tokens

        # 3. Name Detection
        detected_name = extract_name_intent(query)
        if detected_name:
            if is_en:
                answer = (
                    f"Hello, **{detected_name}**! It looks like you are very interested in mastering English with us at **Gastroteacher Academy**.\n\n"
                    f"You are more than welcome to explore all official documents regarding our **General English** and **Gastronomy & Hospitality English** programs, flexible schedules, tuition and 0% interest payment plans in COP, international certifications, and admissions.\n\n"
                    f"💡 *Did you know that 85% of high gastronomy and international hospitality leadership positions require fluent English? We are here to prepare you to lead!*\n\n"
                    f"What program, schedule, or pricing details would you like to discover first?"
                )
            else:
                answer = (
                    f"¡Hola, **{detected_name}**! Veo que tienes un gran interés en dominar el inglés con nosotros en **Gastroteacher Academy**.\n\n"
                    f"Puedes consultar con total confianza todos los documentos oficiales sobre nuestros programas de **Inglés General** e **Inglés Gastronómico**, horarios flexibles, tarifas y facilidades de pago a 0% de interés en COP, certificaciones y proceso de admisión.\n\n"
                    f"💡 *¿Sabías que el 85% de las oportunidades en alta cocina y hotelería internacional exigen inglés fluido? ¡Aquí te preparamos para liderarlas con éxito!*\n\n"
                    f"¿Qué programa, sede o temática académica te gustaría consultar primero?"
                )
            tokens = {"prompt_tokens": approx_prompt_tokens, "completion_tokens": len(answer) // 4, "total_tokens": approx_prompt_tokens + (len(answer) // 4)}
            return answer, False, tokens

        # 4. Pure Greeting Detection
        has_academic_intent = has_exact_keyword(words, IN_SCOPE_KEYWORDS) or is_relevant
        if norm_q in GREETING_WORDS or (len(words) <= 2 and any(w in GREETING_WORDS for w in words) and not has_academic_intent):
            if is_en:
                answer = (
                    "Hello! Welcome to the **Gastroteacher Academy** Virtual Assistant.\n\n"
                    "I am here to guide you with information about our **General English** and **Gastronomy & Hospitality English** programs, flexible schedules (weekdays and weekends), tuition and payment options in COP, study modalities (in-person in Bogota/Medellin and live online), official certifications, and the admissions process.\n\n"
                    "How can I assist you today?"
                )
            else:
                answer = (
                    "¡Hola! Bienvenido al Asistente Virtual de **Gastroteacher Academy**.\n\n"
                    "Estoy a tu disposición para orientarte sobre nuestros programas de formación en **Inglés General** y **Gastronomy & Hospitality English**, horarios flexibles (entre semana y fines de semana), tarifas e inversión en COP con facilidades de pago, modalidades presenciales (Bogotá y Medellín) y online en vivo, certificaciones oficiales y proceso de admisión.\n\n"
                    "¿Qué información te gustaría consultar el día de hoy?"
                )
            tokens = {"prompt_tokens": approx_prompt_tokens, "completion_tokens": len(answer) // 4, "total_tokens": approx_prompt_tokens + (len(answer) // 4)}
            return answer, False, tokens

        # 5. Isolated Nonsense Word Warning
        is_isolated_nonsense = (
            (len(words) <= 2 and (norm_q in NONSENSE_KEYWORDS or any(w in NONSENSE_KEYWORDS for w in words)))
            or (len(words) == 1 and not is_relevant and not has_academic_intent and not detected_name)
        )

        if is_isolated_nonsense and not has_academic_intent and not is_relevant:
            if is_en:
                answer = (
                    "System Notice: The Gastroteacher Virtual Assistant is exclusively designed to answer inquiries from individuals interested in our language and gastronomy academy's academic programs, schedules, pricing, certifications, and admissions.\n\n"
                    "If you are interested in our courses, please ask about:\n"
                    "- Available class schedules (weekdays and weekends)\n"
                    "- Pricing, promotions, and flexible payment plans in COP\n"
                    "- General English or Gastronomy & Hospitality English programs\n"
                    "- Enrollment process and free placement test"
                )
            else:
                answer = (
                    "Aviso del Sistema: El Asistente Virtual de Gastroteacher está diseñado exclusivamente para responder consultas de personas interesadas en los programas académicos, horarios, precios, certificaciones y admisiones de nuestra academia de idiomas y gastronomía.\n\n"
                    "Si deseas información sobre nuestros cursos, por favor indícame tu consulta sobre:\n"
                    "- Horarios de clases disponibles (entre semana y fines de semana)\n"
                    "- Precios, promociones y facilidades de pago en COP\n"
                    "- Programas de Inglés General o Inglés para Gastronomía y Hospitalidad\n"
                    "- Proceso de matrícula y test de nivelación gratuito"
                )
            tokens = {"prompt_tokens": approx_prompt_tokens, "completion_tokens": len(answer) // 4, "total_tokens": approx_prompt_tokens + (len(answer) // 4)}
            return answer, False, tokens

        # 6. Explicit Out-of-scope / Complex Escalation Check
        if not is_relevant and not has_academic_intent:
            if is_en:
                answer = (
                    f"[ESCALATE_HUMAN] Hello! Thank you for contacting Gastroteacher. "
                    f"To assist you with your inquiry regarding '{query}' in a personalized manner with a dedicated advisor and human support team, "
                    f"please reach out directly to our team at:\n"
                    f"- **WhatsApp / Telegram**: {settings.ESCALATION_WHATSAPP}\n"
                    f"- **Email**: {settings.ESCALATION_EMAIL}\n"
                    f"- **Business Hours**: {settings.ESCALATION_HOURS}\n"
                    f"A human counselor will assist you shortly!"
                )
            else:
                answer = (
                    f"[ESCALATE_HUMAN] ¡Hola! Gracias por comunicarte con Gastroteacher. "
                    f"Para atender tu consulta sobre '{query}' de manera personalizada y precisa con un asesor y equipo humano de soporte, "
                    f"te invito a contactar directamente a nuestro equipo en:\n"
                    f"- **WhatsApp / Telegram**: {settings.ESCALATION_WHATSAPP}\n"
                    f"- **Correo**: {settings.ESCALATION_EMAIL}\n"
                    f"- **Horario de atención**: {settings.ESCALATION_HOURS}"
                )
            tokens = {"prompt_tokens": approx_prompt_tokens, "completion_tokens": len(answer) // 4, "total_tokens": approx_prompt_tokens + (len(answer) // 4)}
            return answer, True, tokens

        # ---------------------------------------------------------
        # GRUPO B: CONSULTAS ACADÉMICAS Y COMERCIALES VÁLIDAS
        # ---------------------------------------------------------
        # Policy on City Change, Campus Transfer and Relocation
        if any(w in ["ciudad", "ciudades", "mudar", "mudanza", "traslado", "traslados", "reubicacion", "reubicación", "congelar", "congelamiento"] or any(w.startswith(kw) for kw in ["ciud", "mudan", "traslad", "congel"]) for w in words):
            if is_en:
                answer = (
                    "Hello! At Gastroteacher Academy, we offer full flexibility if you relocate or change cities:\n\n"
                    "1. **Campus Transfer**: You can request a transfer between our Bogota and Medellin campuses with no extra administrative fees and without losing your academic progress.\n"
                    "2. **Switch to 100% Live Online**: You can transition directly to our Virtual Campus to continue with live online classes, keeping all your accumulated hours and grades.\n"
                    "3. **Temporary Freeze**: You can freeze your enrollment for up to 90 calendar days while you settle into your new city.\n\n"
                    f"To request your transfer, simply notify academic support at least 3 business days in advance via email ({settings.ESCALATION_EMAIL}) or WhatsApp ({settings.ESCALATION_WHATSAPP}) with your ID document."
                )
            else:
                answer = (
                    "¡Hola! En Gastroteacher Academy contamos con total flexibilidad ante cambios de ciudad, mudanza o reubicación:\n\n"
                    "1. **Traslado de Sede Presencial**: Puedes solicitar el traslado entre nuestras sedes de Bogotá y Medellín sin costo administrativo adicional ni pérdida de avance académico.\n"
                    "2. **Paso a Modalidad Online en Vivo**: Puedes migrar a nuestro Campus Virtual 100% online en vivo conservando tus horas acumuladas y notas.\n"
                    "3. **Congelamiento Preventivo**: Puedes congelar tu matrícula hasta por 90 días calendario mientras te instalas en tu nueva ciudad.\n\n"
                    f"Para coordinar tu traslado de sede o modalidad, notifícalo con al menos 3 días hábiles a soporte académico ({settings.ESCALATION_EMAIL} o WhatsApp {settings.ESCALATION_WHATSAPP}) adjuntando tu documento de identidad."
                )
        elif any(w in ["inscri", "inscripcion", "inscripciones", "matricula", "matriculas", "proceso", "requisito", "requisitos", "test", "examen", "enroll", "admission", "register"] or any(w.startswith(kw) for kw in ["inscri", "matricul", "fech", "inici", "proces"]) for w in words):
            if is_en:
                answer = (
                    "Hello! The enrollment process at Gastroteacher is simple and consists of 4 steps:\n\n"
                    "1. **Free Placement Test**: A 25-minute diagnostic to determine your exact English proficiency level.\n"
                    "2. **Personalized Academic Advising**: A counselor guides you based on your career goals and schedule.\n"
                    "3. **Registration and Payment**: Online enrollment form and upfront payment or 0% interest direct financing.\n"
                    "4. **Onboarding**: Access to the Virtual Campus and your cohort community in less than 2 hours.\n\n"
                    "📅 **Class Start Dates**:\n"
                    "- **Weekday Programs (Monday to Thursday)**: Start the first Monday of each month.\n"
                    "- **Weekend Programs (Saturdays/Sundays)**: Start the first Saturday of each month.\n"
                    "- **Bimonthly Cohorts**: January, March, May, July, September, and November.\n\n"
                    "Would you like us to help you schedule your free placement test today?"
                )
            else:
                answer = (
                    "¡Hola! El proceso de inscripción en Gastroteacher es muy sencillo y consta de 4 pasos:\n\n"
                    "1. **Test de Nivelación Gratuito**: Diagnóstico de 25 minutos para conocer tu nivel exacto de inglés.\n"
                    "2. **Asesoría Personalizada**: Un consejero académico te guía según tus objetivos profesionales y disponibilidad.\n"
                    "3. **Matrícula y Pago**: Diligenciamiento de formulario y pago de contado o financiación a 0% de interés.\n"
                    "4. **Onboarding**: Acceso en menos de 2 horas al Campus Virtual y tu grupo de cohorte.\n\n"
                    "📅 **Fechas de Inicio de Clases**:\n"
                    "- **Cursos Entre Semana (Lunes a Jueves)**: Inician el primer lunes de cada mes.\n"
                    "- **Cursos Fines de Semana (Sábados/Domingos)**: Inician el primer sábado de cada mes.\n"
                    "- **Nuevas Cohortes Bimestrales**: Enero, Marzo, Mayo, Julio, Septiembre y Noviembre.\n\n"
                    "¿Deseas que te ayudemos a programar tu test de nivelación gratuito para iniciar en la próxima fecha?"
                )
        elif any(w in ["precio", "precios", "costo", "costos", "vale", "valen", "cuota", "cuotas", "pago", "pagos", "descuento", "promocion", "financ", "price", "prices", "cost", "costs", "fee", "fees", "tuition", "discount", "pay", "plan"] or any(w.startswith(kw) for kw in ["preci", "cost", "financ", "pago", "descuent"]) for w in words):
            if is_en:
                answer = (
                    "Hello! Here is the pricing and payment options information for Gastroteacher Academy:\n\n"
                    "- **General English**: $1,450,000 COP per level (96 hours) upfront, or direct financing in 3 installments ($550,000 initial + 2 monthly payments of $500,000 COP at 0% interest).\n"
                    "- **Gastronomy & Hospitality English**: $1,980,000 COP for the complete 120-hour program (or $720,000 COP per individual 40-hour module).\n"
                    "- **Promotions**: 10% early-bird discount, 15% discount with culinary partner ID (SENA, Gato Dumas, Mariano Moreno), and 25% for annual combo (A1 to B2).\n\n"
                    "Would you like to schedule your free placement test to get started?"
                )
            else:
                answer = (
                    "¡Hola! Con gusto te comparto la información de precios y facilidades de pago en Gastroteacher:\n\n"
                    "- **Inglés General**: $1.450.000 COP por nivel (96 horas) de contado, o financiado en 3 cuotas ($550.000 inicial + 2 cuotas de $500.000 COP a 0% interés).\n"
                    "- **Gastronomy & Hospitality English**: $1.980.000 COP por el programa completo de 120 horas (o $720.000 COP por módulo individual de 40 horas).\n"
                    "- **Promociones**: 10% por pronto pago, 15% con carnet de aliados gastronómicos (SENA, Gato Dumas, Mariano Moreno) y 25% en combo anual (A1 a B2).\n\n"
                    "¿Te gustaría realizar tu test de nivelación gratuito para iniciar?"
                )
        elif any(w in ["horario", "horarios", "sabado", "sabados", "domingo", "domingos", "jornada", "jornadas", "noche", "noches", "manana", "mananas", "tarde", "tardes", "schedule", "schedules", "weekend", "weekends", "weekday", "weekdays", "saturday", "sunday", "morning", "night"] or any(w.startswith(kw) for kw in ["horari", "sabad", "doming", "jornad"]) for w in words):
            if is_en:
                answer = (
                    "Hello! Gastroteacher offers flexible schedules tailored to your routine:\n\n"
                    "- **Weekdays (Monday to Thursday)**: Morning (6:30 AM - 8:30 AM), Afternoon (2:30 PM - 4:30 PM), and Evening (6:30 PM - 8:30 PM or 8:00 PM - 10:00 PM).\n"
                    "- **Weekends**: Saturday Intensive (8:00 AM - 1:00 PM or 2:00 PM - 7:00 PM) and Sunday Morning (8:30 AM - 1:30 PM 100% live online).\n\n"
                    "You can take classes in person (Bogota & Medellin campuses) or 100% live online. Which schedule fits you best?"
                )
            else:
                answer = (
                    "¡Hola! En Gastroteacher contamos con horarios muy flexibles adaptados a tu disponibilidad:\n\n"
                    "- **Entre Semana (Lunes a Jueves)**: Mañana (6:30 AM - 8:30 AM), Tarde (2:30 PM - 4:30 PM) y Noche (6:30 PM - 8:30 PM o 8:00 PM - 10:00 PM).\n"
                    "- **Fines de Semana**: Sábados Intensivo (8:00 AM - 1:00 PM o 2:00 PM - 7:00 PM) y Domingos Mañana (8:30 AM - 1:30 PM 100% online en vivo).\n\n"
                    "Puedes tomar tus clases de forma presencial (sedes Bogotá y Medellín) o 100% online en vivo. ¿Qué horario se adapta mejor a tu rutina?"
                )
        elif any(w in ["certific", "certificacion", "certificaciones", "diploma", "diplomas", "toefl", "ielts", "mcer", "sena"] or any(w.startswith(kw) for kw in ["certific", "diplom", "toefl", "ielts", "mcer"]) for w in words):
            if is_en:
                answer = (
                    "Hello! Studying at Gastroteacher provides you with official high-value certifications:\n\n"
                    "- **Gastroteacher Institutional Diploma**: Digital certificate with verifiable QR code aligned with the CEFR (Common European Framework).\n"
                    "- **Culinary English Proficiency Certificate**: Endorsed by the Colombian Gastronomy Association for gastronomy program graduates.\n"
                    "- **International Exam Preparation**: Workshops and official mock tests for TOEFL iBT, IELTS, and Linguaskill with a 15% discount on exam registration fees.\n\n"
                    "Do you have a specific international exam in mind?"
                )
            else:
                answer = (
                    "¡Hola! Al estudiar en Gastroteacher obtienes certificaciones oficiales de alto valor:\n\n"
                    "- **Diploma Institucional Gastroteacher**: Certificado digital verificable con código QR bajo el Marco Común Europeo (MCER).\n"
                    "- **Culinary English Proficiency Certificate**: Avalado por la Asociación Colombiana de Gastronomía para egresados del programa gastronómico.\n"
                    "- **Preparación Exámenes Internacionales**: Talleres y simulacros TOEFL iBT, IELTS y Linguaskill con 15% de descuento en tarifas de examen.\n\n"
                    "¿Tienes en mente alguna certificación internacional específica?"
                )
        else:
            if is_en:
                answer = (
                    "Hello! Gastroteacher offers specialized General English and Gastronomy & Hospitality English programs in in-person (Bogota & Medellin), 100% live online, and hybrid modalities.\n\n"
                    "We offer levels from A1 to C1, flexible weekday and weekend schedules, and direct 0% interest financing.\n\n"
                    "Which program or campus would you like to know more about?"
                )
            else:
                answer = (
                    "¡Hola! Con mucho gusto te informo que en Gastroteacher ofrecemos programas especializados de Inglés General y Inglés para Gastronomía y Hospitalidad en modalidades presencial (Bogotá y Medellín), 100% online en vivo e híbrida.\n\n"
                    "Contamos con niveles desde A1 hasta C1, horarios entre semana y fines de semana, y facilidades de pago directas a 0% de interés.\n\n"
                    "¿Sobre qué programa o sede te gustaría conocer más detalles?"
                )

        approx_comp_tokens = max(10, len(answer) // 4)
        tokens = {
            "prompt_tokens": approx_prompt_tokens,
            "completion_tokens": approx_comp_tokens,
            "total_tokens": approx_prompt_tokens + approx_comp_tokens
        }
        return answer, False, tokens

    async def generate_response(self, query: str, context: str, is_relevant: bool, language: str = 'es') -> Tuple[str, bool, Dict[str, Any], float]:
        """
        Generates answer via Ollama LLM or fallback with strict Grupo A escalation and error handling.
        """
        start_time = time.perf_counter()
        norm_q = normalize_simple(query)
        words = norm_q.split()
        grupo_a = classify_grupo_a_intent(query)
        has_academic_intent = has_exact_keyword(words, IN_SCOPE_KEYWORDS) or is_relevant
        has_vulgarity = contains_profanity(query)
        gibberish = is_gibberish(query)
        detected_name = extract_name_intent(query) if not has_vulgarity and not gibberish and not grupo_a else None

        # Check for greeting, name, and nonsense shortcuts
        is_greeting = (
            norm_q in GREETING_WORDS
            or (len(words) <= 2 and any(w in GREETING_WORDS for w in words) and not has_academic_intent and not has_vulgarity and not gibberish and not grupo_a)
        )
        is_isolated_nonsense = (
            not norm_q
            or not any(c.isalnum() for c in query)
            or has_vulgarity
            or gibberish
            or (len(words) <= 2 and (norm_q in NONSENSE_KEYWORDS or any(w in NONSENSE_KEYWORDS for w in words)))
            or (len(words) == 1 and not is_relevant and not has_academic_intent and not detected_name)
        ) and not has_academic_intent and not detected_name and not grupo_a

        forced_escalation = (
            grupo_a is not None
            or (
                not is_relevant
                and not is_greeting
                and not is_isolated_nonsense
                and not has_academic_intent
                and not detected_name
                and not has_vulgarity
                and not gibberish
            )
        )

        messages = build_rag_prompt(query, context, language)

        # 1. Try configured providers in order of priority (e.g. ['groq', 'gemini', 'openai', 'ollama'])
        for prov in self.providers:
            prov_lower = prov.lower().strip()
            result = None

            if prov_lower == "ollama":
                result = await self._query_ollama(messages, query, context)
            elif prov_lower in ("groq", "gemini", "openai"):
                result = await self._query_external_provider(prov_lower, messages, query, context)

            if result is not None:
                raw_content, token_usage = result
                is_escalated = "[ESCALATE_HUMAN]" in raw_content or forced_escalation
                cleaned_content = raw_content.replace("[ESCALATE_HUMAN]", "")
                cleaned_content = clean_markdown_response(cleaned_content)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                logger.info(f"{prov.upper()} response generated in {latency_ms}ms (escalated: {is_escalated})")
                return cleaned_content, is_escalated, token_usage, latency_ms

        # 2. Fallback if all providers failed or are not configured
        logger.warning("All LLM providers unavailable or exhausted. Activating deterministic grounded fallback.")
        answer, is_escalated, token_usage = self._fallback_generate(query, context, is_relevant and not forced_escalation, language)
        cleaned_content = answer.replace("[ESCALATE_HUMAN]", "")
        cleaned_content = clean_markdown_response(cleaned_content)
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(f"Fallback response generated in {latency_ms:.2f}ms (escalated: {is_escalated})")
        return cleaned_content, is_escalated, token_usage, latency_ms

    async def _query_ollama(
        self,
        messages: list[dict],
        query: str,
        context: str
    ) -> Optional[Tuple[str, Dict[str, int]]]:
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
                res = await client.post("/api/chat", json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens
                    }
                })
                if res.status_code == 200:
                    data = res.json()
                    raw_content = data.get("message", {}).get("content", "")
                    prompt_tokens = data.get("prompt_eval_count", len(query + context) // 4)
                    completion_tokens = data.get("eval_count", len(raw_content) // 4)
                    token_usage = {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    }
                    return raw_content, token_usage
                else:
                    logger.warning(f"Ollama returned status {res.status_code}")
        except Exception as e:
            logger.warning(f"Ollama call exception: {e}")
        return None

    async def _query_external_provider(
        self,
        provider: str,
        messages: list[dict],
        query: str,
        context: str
    ) -> Optional[Tuple[str, Dict[str, int]]]:
        if provider == "groq":
            keys = self.groq_api_keys
            url = "https://api.groq.com/openai/v1/chat/completions"
            model = self.groq_model
        elif provider == "gemini":
            keys = self.gemini_api_keys
            url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
            model = self.gemini_model
        elif provider == "openai":
            keys = self.openai_api_keys
            url = f"{self.openai_base_url}/chat/completions"
            model = self.openai_model
        else:
            return None

        if not keys:
            return None

        num_keys = len(keys)
        start_idx = self._provider_indices.get(provider, 0) % num_keys

        for attempt in range(num_keys):
            curr_idx = (start_idx + attempt) % num_keys
            key = keys[curr_idx]
            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }

            try:
                async with httpx.AsyncClient(timeout=25.0) as client:
                    res = await client.post(url, json=payload, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        choices = data.get("choices", [])
                        raw_content = choices[0].get("message", {}).get("content", "") if choices else data.get("message", {}).get("content", "")
                        usage = data.get("usage", {})
                        p_tok = usage.get("prompt_tokens", len(query + context) // 4)
                        c_tok = usage.get("completion_tokens", len(raw_content) // 4)
                        token_usage = {
                            "prompt_tokens": p_tok,
                            "completion_tokens": c_tok,
                            "total_tokens": usage.get("total_tokens", p_tok + c_tok)
                        }
                        self._provider_indices[provider] = curr_idx
                        logger.info(f"Provider {provider} (key #{curr_idx + 1}) successfully generated response.")
                        return raw_content, token_usage

                    elif res.status_code in (429, 401, 403):
                        logger.warning(
                            f"Provider {provider} key #{curr_idx + 1} returned status {res.status_code}. "
                            f"Rotating to next key..."
                        )
                        self._provider_indices[provider] = (curr_idx + 1) % num_keys
                    else:
                        logger.warning(
                            f"Provider {provider} returned status {res.status_code}: {res.text[:200]}"
                        )
            except Exception as e:
                logger.warning(f"Error calling {provider} key #{curr_idx + 1}: {e}")
                self._provider_indices[provider] = (curr_idx + 1) % num_keys

        return None


# Backward compatibility alias
OllamaClient = LLMClient
