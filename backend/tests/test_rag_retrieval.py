import pytest
from app.rag.retriever import RAGRetriever
from app.api.routers.documents import ingest_all_documents

@pytest.fixture(scope="module", autouse=True)
def setup_vector_db():
    ingest_all_documents()

def test_retrieval_for_schedules():
    retriever = RAGRetriever()
    chunks, is_relevant, context = retriever.retrieve("¿Cuáles son los horarios de clases los sábados y entre semana?")
    assert len(chunks) > 0
    assert is_relevant is True
    assert "horario" in context.lower() or "sábado" in context.lower()
    assert any("02_pricing_schedules_promotions.md" in c["source"] or "01_courses_modalities_levels.md" in c["source"] for c in chunks)

def test_retrieval_for_pricing():
    retriever = RAGRetriever()
    chunks, is_relevant, context = retriever.retrieve("¿Cuánto cuesta el curso de inglés y qué facilidades de pago tienen?")
    assert len(chunks) > 0
    assert is_relevant is True
    assert "cop" in context.lower() or "precio" in context.lower() or "contado" in context.lower()

def test_retrieval_for_certifications():
    retriever = RAGRetriever()
    chunks, is_relevant, context = retriever.retrieve("¿Qué certificación internacional otorgan al finalizar y tienen TOEFL o IELTS?")
    assert len(chunks) > 0
    assert is_relevant is True
    assert "certific" in context.lower() or "toefl" in context.lower() or "ielts" in context.lower()

def test_retrieval_for_enrollment_process():
    retriever = RAGRetriever()
    chunks, is_relevant, context = retriever.retrieve("¿Cómo es el proceso de inscripción y cuándo inician las clases?")
    assert len(chunks) > 0
    assert is_relevant is True
    assert "inscripci" in context.lower() or "test" in context.lower() or "cohorte" in context.lower()
