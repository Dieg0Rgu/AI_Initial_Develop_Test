from __future__ import annotations
import time
from typing import Dict, Any, List

try:
    from app.cache.cache_service import response_cache
except ImportError:
    from backend.app.cache.cache_service import response_cache

# Reference commercial rate for token savings calculation ($0.0015 / 1k tokens)
COST_PER_1K_TOKENS_USD = 0.0015
USD_TO_COP_RATE = 4000.0

class MetricsTracker:
    def __init__(self):
        self.start_time = time.time()
        self.total_queries: int = 0
        self.escalated_queries: int = 0
        self.total_prompt_tokens: int = 0
        self.total_completion_tokens: int = 0
        self.latencies_ms: List[float] = []

    def record_query(self, is_escalated: bool, prompt_tokens: int, completion_tokens: int, latency_ms: float):
        """
        Records a completed query interaction.
        """
        self.total_queries += 1
        if is_escalated:
            self.escalated_queries += 1

        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        self.latencies_ms.append(latency_ms)

        # Keep rolling window of last 100 latencies
        if len(self.latencies_ms) > 100:
            self.latencies_ms.pop(0)

    def get_summary(self) -> Dict[str, Any]:
        """
        Returns full metrics dashboard summary.
        """
        total_tokens = self.total_prompt_tokens + self.total_completion_tokens
        escalation_rate = (self.escalated_queries / self.total_queries * 100) if self.total_queries > 0 else 0.0
        avg_latency = (sum(self.latencies_ms) / len(self.latencies_ms)) if self.latencies_ms else 0.0

        # Cost calculations
        cost_usd = (total_tokens / 1000.0) * COST_PER_1K_TOKENS_USD
        cost_cop = cost_usd * USD_TO_COP_RATE

        cache_stats = response_cache.get_stats()
        saved_tokens = cache_stats["tokens_saved"]
        saved_usd = (saved_tokens / 1000.0) * COST_PER_1K_TOKENS_USD
        saved_cop = saved_usd * USD_TO_COP_RATE

        uptime_seconds = int(time.time() - self.start_time)

        return {
            "total_queries": self.total_queries,
            "escalated_queries": self.escalated_queries,
            "resolved_by_ai_queries": self.total_queries - self.escalated_queries,
            "escalation_rate_pct": round(escalation_rate, 2),
            "tokens": {
                "prompt_tokens": self.total_prompt_tokens,
                "completion_tokens": self.total_completion_tokens,
                "total_tokens": total_tokens,
                "tokens_saved_by_cache": saved_tokens
            },
            "costs": {
                "estimated_cost_usd": round(cost_usd, 5),
                "estimated_cost_cop": round(cost_cop, 2),
                "savings_by_cache_usd": round(saved_usd, 5),
                "savings_by_cache_cop": round(saved_cop, 2),
                "local_ollama_actual_cost": "$0.00 (Local Open-Source Execution)"
            },
            "performance": {
                "avg_latency_ms": round(avg_latency, 2),
                "cache": cache_stats,
                "uptime_seconds": uptime_seconds
            }
        }

    def reset(self):
        """Resets all metrics counters."""
        self.start_time = time.time()
        self.total_queries = 0
        self.escalated_queries = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.latencies_ms = []
        response_cache.clear()


# Global singleton tracker
metrics_tracker = MetricsTracker()
