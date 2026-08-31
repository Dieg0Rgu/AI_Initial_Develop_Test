import pytest
from app.rag.retriever import RAGRetriever
from app.llm.client import (
    OllamaClient,
    extract_name_intent,
    contains_profanity,
    is_gibberish,
    is_grupo_a_intent,
    classify_grupo_a_intent
)
from app.config import settings
from app.api.routers.documents import ingest_all_documents


@pytest.fixture(scope="module", autouse=True)
def setup_knowledge():
    ingest_all_documents()


def test_extract_name_intent():
    assert extract_name_intent("Diego") == "Diego"
    assert extract_name_intent("valentina") == "Valentina"
    assert extract_name_intent("juancha viviana") == "Juancha Viviana"
    assert extract_name_intent("soy Carlos Gomez") == "Carlos Gomez"
    assert extract_name_intent("My name is Sarah Connor") == "Sarah Connor"
    assert extract_name_intent("precio del curso") is None
    assert extract_name_intent("pizza") is None
    assert extract_name_intent("puta") is None
    assert extract_name_intent("mierda") is None
    assert extract_name_intent("fuck") is None
    assert extract_name_intent("}") is None
    assert extract_name_intent("table") is None
    assert extract_name_intent("car") is None
    assert extract_name_intent("asdfghj") is None


def test_contains_profanity():
    assert contains_profanity("hola gonorrea") is True
    assert contains_profanity("mierda") is True
    assert contains_profanity("what the fuck") is True
    assert contains_profanity("Diego") is False
    assert contains_profanity("Buenos días") is False


def test_is_gibberish():
    assert is_gibberish("asdfghj") is True
    assert is_gibberish("qwerty") is True
    assert is_gibberish("}") is True
    assert is_gibberish("Diego") is False
    assert is_gibberish("Valentina") is False


def test_grupo_a_intent_classification():
    # Case 1: Refund
    q1 = "Pagué el curso completo la semana pasada pero me transfirieron de empresa y no podré asistir. Exijo la devolución total de mi dinero a mi cuenta bancaria."
    assert is_grupo_a_intent(q1) is True
    assert classify_grupo_a_intent(q1) == "REFUND"

    # Case 2: Corporate
    q2 = "Soy el director de Recursos Humanos de Crepes & Waffles, queremos matricular a 50 cocineros y requerimos una tarifa corporativa del 50% y factura electrónica a 60 días."
    assert is_grupo_a_intent(q2) is True
    assert classify_grupo_a_intent(q2) == "CORPORATE"

    # Case 3: Tech 403
    q3 = "Hice el pago por PSE hace 3 días, pero cuando intento entrar al campus virtual me sale error 403 y no me deja ver las grabaciones de las clases."
    assert is_grupo_a_intent(q3) is True
    assert classify_grupo_a_intent(q3) == "TECHNICAL"

    # Case 4: Recipes
    q4 = "¿Me puedes enseñar a preparar salsa bearnesa paso a paso y decirme qué vinos chilenos combinan mejor?"
    assert is_grupo_a_intent(q4) is True
    assert classify_grupo_a_intent(q4) == "RECIPES"

    # Case 5: Visa / Immigration
    q5 = "¿Ustedes me ayudan a tramitar la visa de trabajo o me dan patrocinio para irme a un restaurante en Australia?"
    assert is_grupo_a_intent(q5) is True
    assert classify_grupo_a_intent(q5) == "IMMIGRATION"

    # Academic valid query should NOT be Grupo A
    q_valid = "¿Cuáles son los horarios y precios de los cursos de inglés?"
    assert is_grupo_a_intent(q_valid) is False

    # City transfer is an in-scope academic policy query
    q_city = "Me voy a mudar de Bogotá a Medellín el próximo mes. ¿Qué opciones tengo para continuar mi curso?"
    assert is_grupo_a_intent(q_city) is False


@pytest.mark.asyncio
async def test_symbols_and_nonsense_in_both_languages():
    llm = OllamaClient()
    # English symbols and nonsense
    for nonsense_en in ["}", "{", "???", "pizza", "car", "apple", "table", "chair", "whatever", "asdfghj"]:
        res_en, is_esc_en, _, _ = await llm.generate_response(nonsense_en, "", is_relevant=False, language='en')
        assert is_esc_en is False
        assert "System Notice" in res_en
        assert "exclusively designed" in res_en.lower() or "interested in" in res_en.lower()
        assert "Hello, **" not in res_en

    # Spanish symbols and nonsense
    for nonsense_es in ["}", "{", "???", "pizza", "carro", "manzana", "mesa", "silla", "asdfghj", "qwerty"]:
        res_es, is_esc_es, _, _ = await llm.generate_response(nonsense_es, "", is_relevant=False, language='es')
        assert is_esc_es is False
        assert "Aviso del Sistema" in res_es
        assert "exclusivamente" in res_es.lower() or "interesadas" in res_es.lower()
        assert "¡Hola, **" not in res_es


@pytest.mark.asyncio
async def test_profanity_triggers_warning_notice():
    llm = OllamaClient()
    for vulgar in ["mierda", "puta", "gonorrea", "carechimba", "hijueputa"]:
        res_es, is_esc_es, _, _ = await llm.generate_response(vulgar, "", is_relevant=False, language='es')
        assert is_esc_es is False
        assert "Aviso del Sistema" in res_es
        assert "respetuoso" in res_es.lower() or "interesadas" in res_es.lower() or "exclusivamente" in res_es.lower()
        assert "¡Hola, **" not in res_es

    for vulgar_en in ["fuck", "bitch", "shit"]:
        res_en, is_esc_en, _, _ = await llm.generate_response(vulgar_en, "", is_relevant=False, language='en')
        assert is_esc_en is False
        assert "System Notice" in res_en
        assert "respectful" in res_en.lower() or "interested" in res_en.lower()
        assert "Hello, **" not in res_en


@pytest.mark.asyncio
async def test_name_greeting_responses():
    llm = OllamaClient()
    res_es, is_esc_es, _, _ = await llm.generate_response("juancha viviana", "", is_relevant=False, language='es')
    assert is_esc_es is False
    assert "Juancha Viviana" in res_es
    assert ("interés" in res_es.lower() or "interes" in res_es.lower())
    assert "85%" in res_es

    res_en, is_esc_en, _, _ = await llm.generate_response("Diego", "", is_relevant=False, language='en')
    assert is_esc_en is False
    assert "Diego" in res_en
    assert "85%" in res_en
    assert "English" in res_en


@pytest.mark.asyncio
async def test_greeting_handling():
    llm = OllamaClient()
    for greeting in ["hola", "buenos días", "buenas tardes"]:
        response_text, is_escalated, tokens, latency = await llm.generate_response(greeting, "", is_relevant=False, language='es')
        assert is_escalated is False
        assert ("bienvenido" in response_text.lower()) or ("gastroteacher" in response_text.lower())

    for greeting_en in ["hello", "hi", "good morning"]:
        response_text, is_escalated, tokens, latency = await llm.generate_response(greeting_en, "", is_relevant=False, language='en')
        assert is_escalated is False
        assert ("welcome" in response_text.lower()) or ("gastroteacher" in response_text.lower())


@pytest.mark.asyncio
async def test_escalation_on_unrelated_query():
    retriever = RAGRetriever()
    llm = OllamaClient()

    query = "¿Cómo reparar el carburador de una motocicleta Yamaha?"
    chunks, is_relevant, context = retriever.retrieve(query)

    response_text, is_escalated, tokens, latency = await llm.generate_response(query, context, is_relevant=False, language='es')

    assert is_escalated is True
    assert (settings.ESCALATION_EMAIL in response_text) or (settings.ESCALATION_WHATSAPP in response_text) or ("asesor" in response_text.lower()) or ("humano" in response_text.lower())


@pytest.mark.asyncio
async def test_escalation_on_crypto_query():
    retriever = RAGRetriever()
    llm = OllamaClient()

    query = "¿Ustedes aceptan pagos en Bitcoin y dan cursos de trading de criptomonedas?"
    chunks, is_relevant, context = retriever.retrieve(query)

    response_text, is_escalated, tokens, latency = await llm.generate_response(query, context, is_relevant=False, language='es')

    assert is_escalated is True
    assert ("soporte" in response_text.lower()) or ("asesor" in response_text.lower()) or ("escalado" in response_text.lower())


@pytest.mark.asyncio
async def test_realistic_escalation_cases():
    llm = OllamaClient()

    # Case 1: Refund
    q1 = "Pagué el curso completo la semana pasada pero me transfirieron de empresa y no podré asistir. Exijo la devolución total de mi dinero a mi cuenta bancaria."
    r1, is_esc1, _, _ = await llm.generate_response(q1, "", is_relevant=False, language='es')
    assert is_esc1 is True
    assert "reembolso" in r1.lower() or "cancelaciones" in r1.lower()
    assert settings.ESCALATION_EMAIL in r1

    # Case 2: Corporate
    q2 = "Soy el director de Recursos Humanos de Crepes & Waffles, queremos matricular a 50 cocineros y requerimos una tarifa corporativa del 50% y factura electrónica a 60 días."
    r2, is_esc2, _, _ = await llm.generate_response(q2, "", is_relevant=False, language='es')
    assert is_esc2 is True
    assert "corporativo" in r2.lower() or "alianzas" in r2.lower()
    assert settings.ESCALATION_EMAIL in r2

    # Case 3: Tech 403
    q3 = "Hice el pago por PSE hace 3 días, pero cuando intento entrar al campus virtual me sale error 403 y no me deja ver las grabaciones de las clases."
    r3, is_esc3, _, _ = await llm.generate_response(q3, "", is_relevant=False, language='es')
    assert is_esc3 is True
    assert "403" in r3 or "soporte técnico" in r3.lower() or "campus virtual" in r3.lower()
    assert settings.ESCALATION_EMAIL in r3

    # Case 4: Recipes
    q4 = "¿Me puedes enseñar a preparar salsa bearnesa paso a paso y decirme qué vinos chilenos combinan mejor?"
    r4, is_esc4, _, _ = await llm.generate_response(q4, "", is_relevant=False, language='es')
    assert is_esc4 is True
    assert "lingüística" in r4.lower() or "recetarios" in r4.lower() or "culinario" in r4.lower()


@pytest.mark.asyncio
async def test_visa_immigration_escalation_case():
    llm = OllamaClient()
    q = "¿Ustedes me ayudan para pedir visa de trabajo o patrocinio para irme a un restaurante en Australia?"
    res, is_esc, _, _ = await llm.generate_response(q, "", is_relevant=False, language='es')
    assert is_esc is True
    assert ("visa" in res.lower() or "visados" in res.lower() or "consulares" in res.lower() or "admisiones" in res.lower())
    assert settings.ESCALATION_EMAIL in res


@pytest.mark.asyncio
async def test_city_transfer_query():
    llm = OllamaClient()
    q = "Me voy a mudar de Bogotá a Medellín el próximo mes. ¿Qué opciones tengo para continuar mi curso allá?"
    res, is_esc, _, _ = await llm.generate_response(q, "Política de traslado de sede presencial entre Bogotá y Medellín...", is_relevant=True, language='es')
    assert is_esc is False
    assert ("traslado" in res.lower() or "sede" in res.lower() or "bogotá" in res.lower() or "medellín" in res.lower())
    assert ("online" in res.lower() or "virtual" in res.lower() or "congelamiento" in res.lower())
