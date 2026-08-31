from __future__ import annotations
import unittest.mock as mock
import pytest

class MockOllamaResponse:
    def __init__(self, content: str, status_code: int = 200, prompt_eval_count: int = 45, eval_count: int = 60):
        self._content = content
        self.status_code = status_code
        self._prompt_eval_count = prompt_eval_count
        self._eval_count = eval_count

    def json(self):
        return {
            "model": "qwen2.5:7b",
            "message": {
                "role": "assistant",
                "content": self._content
            },
            "prompt_eval_count": self._prompt_eval_count,
            "eval_count": self._eval_count,
            "done": True
        }

@pytest.fixture
def mock_ollama_llm():
    """
    PyTest fixture that completely mocks external HTTP calls to Ollama daemon.
    Guarantees deterministic, fast, and fully isolated test runs.
    """
    with mock.patch("httpx.AsyncClient.post") as mocked_post:
        async def _mock_post(url, json=None, **kwargs):
            last_msg = ""
            if json and isinstance(json, dict) and "messages" in json and json["messages"]:
                last_msg = json["messages"][-1].get("content", "").lower()
            else:
                last_msg = str(json).lower()

            if "moto" in last_msg or "visa" in last_msg:
                return MockOllamaResponse(
                    content="[ESCALATE_HUMAN] Hola, para atender esta solicitud de visado debes comunicarte con soporte.",
                    status_code=200
                )
            return MockOllamaResponse(
                content="En Gastroteacher Academy contamos con horarios flexibles entre semana y fines de semana.",
                status_code=200
            )

        mocked_post.side_effect = _mock_post
        yield mocked_post

@pytest.fixture
def mock_ollama_error():
    """
    PyTest fixture simulating Ollama service outage / timeout.
    """
    with mock.patch("httpx.AsyncClient.post", side_effect=Exception("Ollama daemon connection refused")):
        yield
