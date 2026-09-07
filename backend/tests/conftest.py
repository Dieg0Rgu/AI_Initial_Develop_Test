import httpx
import pytest  # noqa: F401
from qa_ecosystem.mocks.ollama_mock import mock_ollama_llm, mock_ollama_error  # noqa: F401


class _IsolatedAsyncClient:
    """
    Fail-fast replacement for ``httpx.AsyncClient`` during tests.

    Connecting to a closed loopback port on Windows can take ~2s per attempt
    (the firewall delays the RST), which made every unmocked LLM call pay a
    multi-second penalty and slowed the suite down to several minutes. This
    fake raises ``ConnectError`` immediately, so all unmocked calls to
    ``generate_response()`` / ``is_healthy()`` fall into the deterministic
    fallback right away, exactly like CI.

    Tests that mock ``httpx.AsyncClient.post`` / ``get`` keep working:
    their ``mock.patch`` resolves against this class and overrides the
    methods on it.
    """

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def get(self, *args, **kwargs):
        raise httpx.ConnectError("LLM calls disabled in tests")

    async def post(self, *args, **kwargs):
        raise httpx.ConnectError("LLM calls disabled in tests")


class _IsolatedSyncClient:
    """Fail-fast replacement for ``httpx.Client`` (used by embeddings)."""

    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def get(self, *args, **kwargs):
        raise httpx.ConnectError("LLM calls disabled in tests")

    def post(self, *args, **kwargs):
        raise httpx.ConnectError("LLM calls disabled in tests")


@pytest.fixture(autouse=True)
def isolate_live_llms(monkeypatch):
    """
    Aísla la suite de tests de los LLMs en vivo (Groq / Gemini / OpenAI / Ollama).

    Cuando el `.env` local incluye API keys de proveedores cloud, los tests que
    invocan ``generate_response()`` sin mocks obtienen respuestas reales no
    deterministas y fallan. Este fixture:
      1. Vacía las keys de proveedores cloud.
      2. Apunta Ollama a un puerto inalcanzable (127.0.0.1:9).
      3. Reemplaza ``httpx.AsyncClient`` por una clase fail-fast para que las
         conexiones reales fallen al instante (en Windows, conectar a un puerto
         cerrado tarda ~2s por intento).

    De esta forma, todos los tests sin mock caen en el fallback determinista
    (``_fallback_generate``), exactamente como en CI. Los tests que sí mockean
    ``httpx`` (``mock_ollama_llm``, ``test_llm_routing``) no se ven afectados,
    porque inyectan sus propias respuestas sobre la clase sustituta y/o
    configuran el cliente explícitamente.
    """
    from app.config import settings

    monkeypatch.setattr(settings, "GROQ_API_KEYS", [])
    monkeypatch.setattr(settings, "GEMINI_API_KEYS", [])
    monkeypatch.setattr(settings, "OPENAI_API_KEYS", [])
    monkeypatch.setattr(settings, "OLLAMA_BASE_URL", "http://127.0.0.1:9")
    monkeypatch.setattr(httpx, "AsyncClient", _IsolatedAsyncClient)
    monkeypatch.setattr(httpx, "Client", _IsolatedSyncClient)
