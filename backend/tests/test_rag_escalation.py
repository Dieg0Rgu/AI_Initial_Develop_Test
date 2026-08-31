import pytest
import asyncio
from app.rag.retriever import RAGRetriever
from app.llm.client import OllamaClient, extract_name_intent, contains_profanity, is_gibberish
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

    for vulgar_en in ["fuck", "bitch", "asshole", "shit"]:
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
