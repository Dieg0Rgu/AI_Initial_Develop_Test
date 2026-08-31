from __future__ import annotations
import time
import re
import unicodedata
from typing import Dict, Any, Tuple, Optional
import httpx

try:
    from app.config import settings
    from app.llm.prompts import build_rag_prompt
except ImportError:
    from backend.app.config import settings
    from backend.app.llm.prompts import build_rag_prompt

# Profanity and inappropriate language blocklist (ES & EN)
PROFANITY_KEYWORDS = {
    # Spanish vulgarities / insults
    "mierda", "puta", "puto", "putas", "putos", "gonorrea", "gonorreas", "marica", "maricas",
    "hijueputa", "hijueputas", "hijadeputa", "hijoeputa", "hp", "malparido", "malparida",
    "pendejo", "pendeja", "pendejos", "idiota", "idiotas", "estupido", "estupida", "imbecil",
    "carechimba", "chimba", "culiao", "culiada", "verga", "vergas", "pito", "tetas", "culo",
    "huevon", "huevona", "guevon", "guevona", "guevada", "coño", "carajo", "chingar", "cabron",
    # English vulgarities / insults
    "fuck", "fucking", "fucked", "fucker", "bitch", "bitches", "asshole", "assholes", "shit",
    "bullshit", "dick", "dicks", "cunt", "cunts", "bastard", "bastards", "slut", "sluts",
    "whore", "whores", "retard", "nigger", "faggot", "piss", "crap", "damn"
}

KEYBOARD_PATTERNS = ["qwerty", "qwert", "asdf", "zxcv", "1234", "hjkl", "yuio"]

COMMON_NAMES = {
    "diego", "valentina", "carlos", "juan", "maria", "andres", "camila", "felipe", "laura",
    "sofia", "santiago", "mateo", "daniel", "daniela", "alejandro", "alejandra", "sebastian",
    "sarah", "john", "michael", "david", "james", "emily", "jessica", "viviana", "juancha",
    "ana", "pablo", "lucas", "gabriel", "pedro", "valeria", "paula", "esteban", "nicolas"
}

GREETING_WORDS_ES = {
    "hola", "buen dia", "buenos dias", "buenas tardes", "buenas noches", "hey", "saludos",
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
    "sede", "sedes", "campus", "bogota", "medellin", "online", "virtual", "presencial", "hibrida", "hybrid"
}

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

def has_exact_keyword(words: list[str], keyword_set: set[str]) -> bool:
    for w in words:
        if w in keyword_set or any(w.startswith(kw) for kw in ["financ", "certific", "inscri", "matricul", "program", "curs", "horari", "preci", "fech", "inici", "clase"]):
            return True
    return False

def extract_name_intent(query: str) -> Optional[str]:
    """
    Detects if the user introduced themselves or provided their real name.
    Strictly excludes profanity, vulgarity, nonsense terms, and academic queries.
    """
    raw = query.strip()
    clean_words = normalize_simple(raw).split()

    # Reject immediately if any profanity/vulgarity or gibberish is present
    if contains_profanity(raw) or is_gibberish(raw):
        return None

    # Check intro prefixes (e.g. "soy Diego", "me llamo Valentina", "mi nombre es Juancha Viviana", "I am John")
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

    # Check 1-word standalone names
    if len(clean_words) == 1:
        w = clean_words[0]
        if w in COMMON_NAMES and w not in GREETING_WORDS and w not in NONSENSE_KEYWORDS:
            return raw.strip().title()

    # Check 2 to 3 words standalone full names (e.g. "Juancha Viviana", "Carlos Gomez", "Sarah Connor")
    if 2 <= len(clean_words) <= 3:
        clean_text = " ".join(clean_words)
        if (
            all(w.isalpha() for w in clean_words)
            and clean_text not in GREETING_WORDS
            and clean_text not in NONSENSE_KEYWORDS
            and not any(w in clean_words for w in NONSENSE_KEYWORDS_EN)
            and not any(w in clean_words for w in NONSENSE_KEYWORDS_ES)
            and not any(w in PROFANITY_KEYWORDS for w in clean_words)
            and not has_exact_keyword(clean_words, IN_SCOPE_KEYWORDS)
            and not any(kw in clean_words for kw in ["visa", "visado", "migratori", "moto", "carro", "bitcoin", "crypto", "mecanica", "queja", "abogado"])
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
    en_signals = {"hello", "hi", "good", "morning", "afternoon", "evening", "what", "how", "when", "where", "much", "cost", "price", "prices", "schedules", "classes", "enrollment", "course", "courses", "apple", "burger", "dog", "cat", "car", "computer", "bro", "dude", "table", "chair", "shoes", "window", "door"}
    return any(w in en_signals for w in words) or norm_q in GREETING_WORDS_EN or norm_q in NONSENSE_KEYWORDS_EN

class OllamaClient:
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.model = model or settings.OLLAMA_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.MAX_TOKENS

    async def is_healthy(self) -> bool:
        """Check if local Ollama daemon is reachable and running."""
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=2.0) as client:
                res = await client.get("/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def _fallback_generate(self, query: str, context: str, is_relevant: bool, language: str = 'es') -> Tuple[str, bool, Dict[str, int]]:
        """
        Deterministic, grounded response generator with bilingual (ES / EN) support.
        """
        norm_q = normalize_simple(query)
        words = norm_q.split()
        approx_prompt_tokens = max(10, len(query + context) // 4)
        is_en = is_english_query(norm_q, words, language)
        has_academic_intent = has_exact_keyword(words, IN_SCOPE_KEYWORDS) or is_relevant
        has_vulgarity = contains_profanity(query)
        gibberish = is_gibberish(query)

        # 0. Empty, Symbols Only, Single Punctuation, or Gibberish (e.g. "}", "{", "???", "asdfghj", "qwerty")
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

        # 1. Immediate Profanity / Inappropriate Language Interception -> System Notice Warning
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

        # 2. Name Detection & Engaging Persona Greeting (ONLY when clean and verified)
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

        # 3. Pure Greeting Detection (including informal greetings like "bro", "pana", "parce")
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

        # 4. Isolated Nonsense Word Warning (only for short 1-2 words nonsense with NO academic intent and not relevant)
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

        # 5. Explicit Out-of-scope / Complex Escalation Check
        is_out_of_scope = (
            (not is_relevant and not has_academic_intent)
            or any(kw in words for kw in ["visa", "visado", "migratori", "moto", "carro", "bitcoin", "crypto", "mecanica", "abogado", "queja", "asesor"])
        )

        if is_out_of_scope and not is_relevant:
            if is_en:
                answer = (
                    f"[ESCALATE_HUMAN] Hello! Thank you for contacting Gastroteacher. "
                    f"To assist you with your inquiry regarding '{query}' in a personalized manner with an admissions counselor, "
                    f"please reach out directly to our human support team at:\n"
                    f"- **WhatsApp / Telegram**: {settings.ESCALATION_WHATSAPP}\n"
                    f"- **Email**: {settings.ESCALATION_EMAIL}\n"
                    f"- **Business Hours**: {settings.ESCALATION_HOURS}\n"
                    f"A human counselor will assist you shortly!"
                )
            else:
                answer = (
                    f"[ESCALATE_HUMAN] ¡Hola! Gracias por comunicarte con Gastroteacher. "
                    f"Para atender tu consulta sobre '{query}' de manera personalizada y precisa con un consejero especializado, "
                    f"te invito a contactar directamente a nuestro equipo humano en:\n"
                    f"- **WhatsApp / Telegram**: {settings.ESCALATION_WHATSAPP}\n"
                    f"- **Correo**: {settings.ESCALATION_EMAIL}\n"
                    f"- **Horario de atención**: {settings.ESCALATION_HOURS}\n"
                    f"¡Un asesor humano te responderá a la mayor brevedad!"
                )
            tokens = {"prompt_tokens": approx_prompt_tokens, "completion_tokens": len(answer) // 4, "total_tokens": approx_prompt_tokens + (len(answer) // 4)}
            return answer, True, tokens

        # 6. In-Scope Structured Knowledge Answers
        if any(w in words or any(w.startswith(kw) for kw in ["inscri", "matricul", "fech", "inici", "proces"]) for w in words):
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
        elif any(w in words or any(w.startswith(kw) for kw in ["preci", "cost", "financ", "pago", "descuent"]) for w in words):
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
        elif any(w in words or any(w.startswith(kw) for kw in ["horari", "sabad", "doming", "jornad"]) for w in words):
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
        elif any(w in words or any(w.startswith(kw) for kw in ["certific", "diplom", "toefl", "ielts", "mcer"]) for w in words):
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
        Generates answer via Ollama LLM or fallback.
        Returns:
            - response_text (str)
            - is_escalated (bool)
            - token_usage (dict)
            - latency_ms (float)
        """
        start_time = time.perf_counter()
        norm_q = normalize_simple(query)
        words = norm_q.split()
        has_academic_intent = has_exact_keyword(words, IN_SCOPE_KEYWORDS) or is_relevant
        has_vulgarity = contains_profanity(query)
        gibberish = is_gibberish(query)
        detected_name = extract_name_intent(query) if not has_vulgarity and not gibberish else None

        # Check for greeting, name, and nonsense shortcuts
        is_greeting = norm_q in GREETING_WORDS or (len(words) <= 2 and any(w in GREETING_WORDS for w in words) and not has_academic_intent and not has_vulgarity and not gibberish)
        is_isolated_nonsense = (
            not norm_q
            or not any(c.isalnum() for c in query)
            or has_vulgarity
            or gibberish
            or (len(words) <= 2 and (norm_q in NONSENSE_KEYWORDS or any(w in NONSENSE_KEYWORDS for w in words)))
            or (len(words) == 1 and not is_relevant and not has_academic_intent and not detected_name)
        ) and not has_academic_intent and not detected_name

        # Forced escalation for explicit out-of-scope topics
        forced_escalation = (
            not is_relevant
            and not is_greeting
            and not is_isolated_nonsense
            and not has_academic_intent
            and not detected_name
            and not has_vulgarity
            and not gibberish
            or any(kw in words for kw in ["visa", "visado", "migratori", "moto", "carro", "bitcoin", "crypto", "mecanica"])
        )

        messages = build_rag_prompt(query, context, language)

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

                    is_escalated = "[ESCALATE_HUMAN]" in raw_content or forced_escalation
                    cleaned_content = raw_content.replace("[ESCALATE_HUMAN]", "").strip()

                    prompt_tokens = data.get("prompt_eval_count", len(query + context) // 4)
                    completion_tokens = data.get("eval_count", len(cleaned_content) // 4)

                    token_usage = {
                        "prompt_tokens": prompt_tokens,
                        "completion_tokens": completion_tokens,
                        "total_tokens": prompt_tokens + completion_tokens
                    }
                    latency_ms = (time.perf_counter() - start_time) * 1000
                    return cleaned_content, is_escalated, token_usage, round(latency_ms, 2)

        except Exception:
            pass

        # Deterministic grounded fallback
        answer, is_escalated, token_usage = self._fallback_generate(query, context, is_relevant and not forced_escalation, language)
        cleaned_content = answer.replace("[ESCALATE_HUMAN]", "").strip()
        latency_ms = (time.perf_counter() - start_time) * 1000

        return cleaned_content, is_escalated, token_usage, round(latency_ms, 2)
