from __future__ import annotations
import json
import time
import re
import unicodedata
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FAQ_PATH = BASE_DIR / "backend" / "data" / "faq.json"
if not FAQ_PATH.exists():
    FAQ_PATH = BASE_DIR / "data" / "faq.json"


def normalize_text(text: str) -> str:
    nfkd = unicodedata.normalize('NFKD', text)
    clean = "".join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()
    clean = re.sub(r'[^\w\s]', '', clean)
    return re.sub(r'\s+', ' ', clean)


class FAQService:
    """
    High-speed, zero-LLM, zero-DB FAQ and Multi-level Support Service.
    Handles immediate responses for FAQs and progressive 3-level escalation for payment/registration issues.
    """

    def __init__(self, faq_file: Optional[Path] = None, session_ttl_seconds: int = 1800):
        self.faq_file = faq_file or FAQ_PATH
        self.session_ttl = session_ttl_seconds
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self.data: Dict[str, Any] = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        try:
            if self.faq_file.exists():
                with open(self.faq_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {"multi_level_support": {}, "static_faqs": []}

    def _cleanup_expired_sessions(self):
        now = time.time()
        expired_keys = [
            sid for sid, sdata in self._sessions.items()
            if now - sdata.get("updated_at", now) > self.session_ttl
        ]
        for sid in expired_keys:
            self._sessions.pop(sid, None)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        self._cleanup_expired_sessions()
        return self._sessions.get(session_id)

    def set_session_level(self, session_id: str, topic: str, level: int):
        self._cleanup_expired_sessions()
        self._sessions[session_id] = {
            "topic": topic,
            "level": level,
            "updated_at": time.time()
        }

    def clear_session(self, session_id: str):
        self._sessions.pop(session_id, None)

    def _is_payment_issue(self, norm_q: str) -> bool:
        problem_terms = {
            "problema", "problemas", "error", "errores", "falla", "fallas", "fallo", "falló",
            "no puedo", "no he podido", "no me deja", "rechazo", "rechazada", "rechazado",
            "inconveniente", "inconvenientes", "issue", "problem", "cannot", "failed", "dificultad",
            "ayuda para pagar", "ayuda con el pago", "ayuda con mi pago"
        }
        payment_terms = {
            "pago", "pagos", "pagar", "pse", "tarjeta", "tarjetas", "pasarela", "wompi",
            "transaccion", "transacción", "pay", "payment", "checkout", "debito", "crédito", "credito"
        }
        has_prob = any(p in norm_q for p in problem_terms)
        has_pay = any(t in norm_q for t in payment_terms)
        return has_prob and has_pay

    def _is_registration_issue(self, norm_q: str) -> bool:
        problem_terms = {
            "problema", "problemas", "error", "errores", "falla", "fallas", "fallo",
            "no puedo", "no he podido", "no me deja", "inconveniente", "inconvenientes",
            "issue", "problem", "cannot", "failed", "dificultad"
        }
        reg_terms = {
            "registro", "registros", "registrarme", "registrarse", "formulario",
            "inscripcion", "inscripción", "inscribirme", "crear cuenta", "mi cuenta",
            "register", "registration", "signup"
        }
        has_prob = any(p in norm_q for p in problem_terms)
        has_reg = any(r in norm_q for r in reg_terms)
        return has_prob and has_reg

    def _is_followup_insistence(self, norm_q: str, topic_data: Dict[str, Any]) -> bool:
        custom_kws = [normalize_text(k) for k in topic_data.get("followup_keywords", [])]
        if any(kw in norm_q for kw in custom_kws):
            return True

        generic_followup = [
            "aun tengo", "aún tengo", "todavia tengo", "todavía tengo", "sigue el problema",
            "sigue igual", "no pude solucionar", "no he podido solucionar", "no funciona",
            "no me funciono", "no me funcionó", "no me sirvio", "no me sirvió", "no sirvio",
            "no sirvió", "persiste", "continua", "continúa", "aun no puedo", "aún no puedo",
            "todavia no puedo", "todavía no puedo", "still have", "still not working",
            "did not solve", "not resolved", "same error", "mismo error", "no soluciono",
            "no solucionó", "persiste el error", "no logro", "sigue fallando", "aun persiste"
        ]
        return any(p in norm_q for p in generic_followup)

    def match_faq(self, query: str, session_id: str = "default_session", language: str = "es") -> Optional[Tuple[str, bool]]:
        """
        Evaluates user query against:
        1. Follow-up progression on active multi-level support sessions (Level 1 -> Level 2 -> Level 3 Escalation).
        2. New multi-level support trigger (Level 1).
        3. Pre-canned static FAQs.

        Returns: (answer_text, is_escalated) or None if no direct match.
        """
        norm_q = normalize_text(query)
        if not norm_q:
            return None

        lang = "en" if (language or "es").lower() == "en" else "es"
        multi_level = self.data.get("multi_level_support", {})

        # --- 1. CHECK ACTIVE SESSION FOLLOW-UP ---
        session = self.get_session(session_id)
        if session:
            topic = session.get("topic")
            current_level = session.get("level", 1)
            topic_data = multi_level.get(topic)

            if topic_data:
                is_followup = self._is_followup_insistence(norm_q, topic_data)
                # Also if the user repeats the payment/registration problem query on the active session
                if not is_followup:
                    if topic == "payment_issues" and self._is_payment_issue(norm_q):
                        is_followup = True
                    elif topic == "registration_issues" and self._is_registration_issue(norm_q):
                        is_followup = True

                if is_followup:
                    if topic == "payment_issues":
                        if current_level == 1:
                            self.set_session_level(session_id, topic, 2)
                            return topic_data["level_2"].get(lang, topic_data["level_2"]["es"]), False
                        else:
                            # Level 3 Escalation to Human Support (Strictly after Level 2)
                            self.clear_session(session_id)
                            return topic_data["level_3"].get(lang, topic_data["level_3"]["es"]), True

                    elif topic == "registration_issues":
                        # Level 2 Escalation to Human Admissions
                        self.clear_session(session_id)
                        return topic_data["level_2"].get(lang, topic_data["level_2"]["es"]), True

        # --- 2. CHECK MULTI-LEVEL TRIGGERS (INITIAL LEVEL 1) ---
        if self._is_payment_issue(norm_q) and "payment_issues" in multi_level:
            self.set_session_level(session_id, "payment_issues", 1)
            lvl1 = multi_level["payment_issues"].get("level_1", {})
            return lvl1.get(lang, lvl1.get("es", "")), False

        if self._is_registration_issue(norm_q) and "registration_issues" in multi_level:
            self.set_session_level(session_id, "registration_issues", 1)
            lvl1 = multi_level["registration_issues"].get("level_1", {})
            return lvl1.get(lang, lvl1.get("es", "")), False

        for topic, topic_data in multi_level.items():
            trigger_kws = [normalize_text(k) for k in topic_data.get("keywords", [])]
            if any(kw in norm_q for kw in trigger_kws):
                self.set_session_level(session_id, topic, 1)
                lvl1 = topic_data.get("level_1", {})
                return lvl1.get(lang, lvl1.get("es", "")), False

        # --- 3. CHECK STATIC PRE-CANNED FAQS ---
        static_faqs = self.data.get("static_faqs", [])
        for faq in static_faqs:
            faq_kws = [normalize_text(k) for k in faq.get("keywords", [])]
            if any(kw in norm_q for kw in faq_kws):
                ans_key = f"answer_{lang}"
                ans = faq.get(ans_key) or faq.get("answer_es", "")
                return ans, False

        return None


# Global singleton
faq_service = FAQService()

