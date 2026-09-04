from typing import Dict, Any, Optional
from fastapi import APIRouter, Header, HTTPException

try:
    from app.metrics.metrics_tracker import metrics_tracker
    from app.config import settings
    from app.api.routers.auth import get_optional_current_user
except ImportError:
    from backend.app.metrics.metrics_tracker import metrics_tracker
    from backend.app.config import settings
    from backend.app.api.routers.auth import get_optional_current_user

router = APIRouter(prefix="/api/metrics", tags=["Metrics & Analytics"])


@router.get("")
async def get_metrics(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Returns real-time analytics on processed queries, tokens, costs, cache savings, and escalation rate.
    Requires authentication if METRICS_AUTH_REQUIRED is enabled.
    """
    user = get_optional_current_user(authorization)
    if settings.METRICS_AUTH_REQUIRED and not user:
        raise HTTPException(
            status_code=401,
            detail="Autenticación requerida para visualizar las métricas del sistema."
        )

    summary = metrics_tracker.get_summary()
    if user:
        summary["viewer"] = {
            "username": user["username"],
            "role": user["role"],
            "email": user["email"]
        }
    return summary


@router.post("/reset")
async def reset_metrics(authorization: Optional[str] = Header(None)) -> Dict[str, str]:
    """
    Resets all metrics counters and clears the cache.
    """
    user = get_optional_current_user(authorization)
    if settings.METRICS_AUTH_REQUIRED and not user:
        raise HTTPException(
            status_code=401,
            detail="Autenticación requerida para reiniciar las métricas del sistema."
        )

    metrics_tracker.reset()
    return {"status": "success", "message": "Metrics and cache reset successfully"}
