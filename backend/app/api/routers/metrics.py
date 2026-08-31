from __future__ import annotations
from typing import Dict, Any
from fastapi import APIRouter

try:
    from app.metrics.metrics_tracker import metrics_tracker
except ImportError:
    from backend.app.metrics.metrics_tracker import metrics_tracker

router = APIRouter(prefix="/api/metrics", tags=["Metrics & Analytics"])

@router.get("")
async def get_metrics() -> Dict[str, Any]:
    """
    Returns real-time analytics on processed queries, tokens, costs, cache savings, and escalation rate.
    """
    return metrics_tracker.get_summary()

@router.post("/reset")
async def reset_metrics() -> Dict[str, str]:
    """
    Resets all metrics counters and clears the cache.
    """
    metrics_tracker.reset()
    return {"status": "success", "message": "Metrics and cache reset successfully"}
