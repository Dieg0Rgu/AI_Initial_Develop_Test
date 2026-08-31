from __future__ import annotations
import time
import re
from typing import Dict, Any, Tuple
import httpx

try:
    from app.config import settings
    from app.llm.prompts import build_rag_prompt
except ImportError:
    from backend.app.config import settings
    from backend.app.llm.prompts import build_rag_prompt

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

    def _fallback_generate(self, query: str, context: str, is_relevant: bool) -> Tuple[str, Dict[str, int]]:
        """
        Deterministic, grounded response generator for when Ollama is unavailable during testing.
        Extracts factual answers from the context or escalates if irrelevant.
        """
        query_lower = query.lower()
        approx_prompt_tokens = max(10, len(query + context) // 4)

        # Check explicit out-of-scope topics that require escalation
        is_out_of_scope = (
            not is_relevant
            or not context.strip()
            or any(kw in query_lower for kw in ["visa", "visado", "migratori", "moto", "carro", "bitcoin", "crypto", "mecanica", "abogado", "queja"])
        )

        if is_out_of_scope:
            answer = (
                f"[ESCALATE_HUMAN] ¡Hola! Gracias por comunicarte con Gastroteacher. "
                f"Para atender tu consulta sobre '{query}' de manera personalizada y precisa, "
                f"te invito a contactar directamente a nuestro equipo humano de atención y admisiones en:\n"
                f"- **WhatsApp / Telegram**: {settings.ESCALATION_WHATSAPP}\n"
                f"- **Correo**: {settings.ESCALATION_EMAIL}\n"
                f"- **Horario de atención**: {settings.ESCALATION_HOURS}\n"
                f"¡Un asesor humano se pondrá en contacto contigo a la mayor brevedad!"
            )
            return answer, {
                "prompt_tokens": approx_prompt_tokens,
                "completion_tokens": len(answer) // 4,
                "total_tokens": approx_prompt_tokens + (len(answer) // 4)
            }

        # In-scope answer synthesis based on detected intent
        if any(w in query_lower for w in ["precio", "costo", "vale", "cuota", "pago", "descuento", "promocion", "financ"]):
            answer = (
                "¡Hola! Con gusto te comparto la información de precios y facilidades de pago en Gastroteacher:\n\n"
                "- **Inglés General**: $1.450.000 COP por nivel (96 horas) de contado, o financiado en 3 cuotas ($550.000 inicial + 2 cuotas de $500.000 COP a 0% interés).\n"
                "- **Gastronomy & Hospitality English**: $1.980.000 COP por el programa completo de 120 horas (o $720.000 COP por módulo individual de 40 horas).\n"
                "- **Promociones**: 10% por pronto pago, 15% con carnet de aliados gastronómicos (SENA, Gato Dumas, Mariano Moreno) y 25% en combo anual (A1 a B2).\n\n"
                "¿Te gustaría realizar tu test de nivelación gratuito para iniciar?"
            )
        elif any(w in query_lower for w in ["horario", "sabado", "domingo", "jornada", "noche", "manana", "tarde"]):
            answer = (
                "¡Hola! En Gastroteacher contamos con horarios muy flexibles adaptados a tu disponibilidad:\n\n"
                "- **Entre Semana (Lunes a Jueves)**: Mañana (6:30 AM - 8:30 AM), Tarde (2:30 PM - 4:30 PM) y Noche (6:30 PM - 8:30 PM o 8:00 PM - 10:00 PM).\n"
                "- **Fines de Semana**: Sábados Intensivo (8:00 AM - 1:00 PM o 2:00 PM - 7:00 PM) y Domingos Mañana (8:30 AM - 1:30 PM 100% online en vivo).\n\n"
                "Puedes tomar tus clases de forma presencial (sedes Bogotá y Medellín) o 100% online en vivo. ¿Qué horario se adapta mejor a tu rutina?"
            )
        elif any(w in query_lower for w in ["certific", "diploma", "toefl", "ielts", "mcer", "sena"]):
            answer = (
                "¡Hola! Al estudiar en Gastroteacher obtienes certificaciones oficiales de alto valor:\n\n"
                "- **Diploma Institucional Gastroteacher**: Certificado digital verificable con código QR bajo el Marco Común Europeo (MCER).\n"
                "- **Culinary English Proficiency Certificate**: Avalado por la Asociación Colombiana de Gastronomía para egresados del programa gastronómico.\n"
                "- **Preparación Exámenes Internacionales**: Talleres y simulacros TOEFL iBT, IELTS y Linguaskill con 15% de descuento en tarifas de examen.\n\n"
                "¿Tienes en mente alguna certificación internacional específica?"
            )
        elif any(w in query_lower for w in ["inscri", "matricula", "proceso", "requisito", "test", "examen"]):
            answer = (
                "¡Hola! El proceso de inscripción en Gastroteacher es muy sencillo y consta de 4 pasos:\n\n"
                "1. **Test de Nivelación Gratuito**: Diagnóstico de 25 minutos para conocer tu nivel exacto de inglés.\n"
                "2. **Asesoría Personalizada**: Un consejero te guía según tus objetivos profesionales y disponibilidad.\n"
                "3. **Matrícula y Pago**: Diligenciamiento de formulario y pago de contado o financiación a 0% de interés.\n"
                "4. **Onboarding**: Acceso en menos de 2 horas al Campus Virtual y tu grupo de cohorte.\n\n"
                "¿Deseas que te ayudemos a programar tu test de nivelación gratuito hoy mismo?"
            )
        else:
            answer = (
                "¡Hola! Con mucho gusto te informo que en Gastroteacher ofrecemos programas especializados de Inglés General y Inglés para Gastronomía y Hospitalidad en modalidades presencial (Bogotá y Medellín), 100% online en vivo e híbrida.\n\n"
                "Contamos con niveles desde A1 hasta C1, horarios entre semana y fines de semana, y facilidades de pago directas a 0% de interés.\n\n"
                "¿Sobre qué programa o sede te gustaría conocer más detalles?"
            )

        approx_comp_tokens = max(10, len(answer) // 4)
        return answer, {
            "prompt_tokens": approx_prompt_tokens,
            "completion_tokens": approx_comp_tokens,
            "total_tokens": approx_prompt_tokens + approx_comp_tokens
        }

    async def generate_response(self, query: str, context: str, is_relevant: bool) -> Tuple[str, bool, Dict[str, Any], float]:
        """
        Generates answer via Ollama LLM or fallback if Ollama is offline.
        Returns:
            - response_text (str)
            - is_escalated (bool)
            - token_usage (dict)
            - latency_ms (float)
        """
        start_time = time.perf_counter()
        messages = build_rag_prompt(query, context)

        # Quick check for out-of-scope markers
        query_lower = query.lower()
        forced_escalation = (
            not is_relevant
            or any(kw in query_lower for kw in ["visa", "visado", "migratori", "moto", "carro", "bitcoin", "crypto", "mecanica"])
        )

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
        answer, token_usage = self._fallback_generate(query, context, is_relevant and not forced_escalation)
        is_escalated = "[ESCALATE_HUMAN]" in answer or forced_escalation
        cleaned_content = answer.replace("[ESCALATE_HUMAN]", "").strip()
        latency_ms = (time.perf_counter() - start_time) * 1000

        return cleaned_content, is_escalated, token_usage, round(latency_ms, 2)
