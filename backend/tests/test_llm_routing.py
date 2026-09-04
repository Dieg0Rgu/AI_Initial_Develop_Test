import pytest
import unittest.mock as mock
from app.llm.client import LLMClient, OllamaClient
from app.config import Settings


def test_client_alias_backward_compatibility():
    assert OllamaClient is LLMClient
    client = OllamaClient()
    assert isinstance(client, LLMClient)


def test_is_healthy_with_external_keys():
    client = LLMClient()
    client.groq_api_keys = ["gsk_test_key_1"]
    assert client.is_cloud_available() is True


@pytest.mark.asyncio
async def test_groq_successful_call():
    client = LLMClient()
    client.providers = ["groq"]
    client.groq_api_keys = ["gsk_key_1"]

    mock_resp = mock.MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "Respuesta generada por Groq"}}],
        "usage": {"prompt_tokens": 15, "completion_tokens": 25, "total_tokens": 40}
    }

    with mock.patch("httpx.AsyncClient.post", return_value=mock_resp):
        res, is_esc, usage, lat = await client.generate_response(
            query="¿Cuáles son los horarios?",
            context="Horarios de Gastroteacher",
            is_relevant=True,
            language="es"
        )
        assert res == "Respuesta generada por Groq"
        assert is_esc is False
        assert usage["total_tokens"] == 40
        assert lat >= 0


@pytest.mark.asyncio
async def test_key_rotation_on_rate_limit_429():
    client = LLMClient()
    client.providers = ["groq"]
    client.groq_api_keys = ["gsk_exhausted_key", "gsk_backup_key"]

    resp_429 = mock.MagicMock(status_code=429, text="Rate limit exceeded")
    resp_200 = mock.MagicMock(status_code=200)
    resp_200.json.return_value = {
        "choices": [{"message": {"content": "Respuesta desde clave de respaldo"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    }

    # First call returns 429, second call with next key returns 200
    with mock.patch("httpx.AsyncClient.post", side_effect=[resp_429, resp_200]):
        res, is_esc, usage, _ = await client.generate_response(
            query="¿Cuáles son los horarios?",
            context="Contexto",
            is_relevant=True,
            language="es"
        )
        assert res == "Respuesta desde clave de respaldo"
        assert client._provider_indices["groq"] == 1


@pytest.mark.asyncio
async def test_failover_from_groq_to_gemini():
    client = LLMClient()
    client.providers = ["groq", "gemini"]
    client.groq_api_keys = ["gsk_key_dead"]
    client.gemini_api_keys = ["gemini_key_active"]

    resp_groq_err = mock.MagicMock(status_code=500, text="Internal error")
    resp_gemini_ok = mock.MagicMock(status_code=200)
    resp_gemini_ok.json.return_value = {
        "choices": [{"message": {"content": "Respuesta desde Google Gemini"}}],
        "usage": {"prompt_tokens": 12, "completion_tokens": 18, "total_tokens": 30}
    }

    with mock.patch("httpx.AsyncClient.post", side_effect=[resp_groq_err, resp_gemini_ok]):
        res, is_esc, usage, _ = await client.generate_response(
            query="¿Cuáles son los horarios?",
            context="Contexto",
            is_relevant=True,
            language="es"
        )
        assert res == "Respuesta desde Google Gemini"


@pytest.mark.asyncio
async def test_all_providers_exhausted_triggers_deterministic_fallback():
    client = LLMClient()
    client.providers = ["groq", "gemini"]
    client.groq_api_keys = ["gsk_key"]
    client.gemini_api_keys = ["gemini_key"]

    resp_err = mock.MagicMock(status_code=500, text="Error")

    with mock.patch("httpx.AsyncClient.post", side_effect=[resp_err, resp_err]):
        res, is_esc, usage, _ = await client.generate_response(
            query="¿Cuáles son los precios del curso de inglés?",
            context="Precio 1.450.000 COP",
            is_relevant=True,
            language="es"
        )
        assert "1.450.000" in res or "precios" in res.lower()
        assert is_esc is False


def test_config_comma_separated_keys_validator():
    # Test validator parsing string to list
    res = Settings.parse_comma_separated_list("key1, key2, key3")
    assert res == ["key1", "key2", "key3"]

    res_empty = Settings.parse_comma_separated_list("")
    assert res_empty == []

    res_list = Settings.parse_comma_separated_list(["k1", "k2"])
    assert res_list == ["k1", "k2"]

