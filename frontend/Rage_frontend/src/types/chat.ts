export interface SourceDocument {
  id: string
  source: string
  title: string
  category: string
  similarity_score: number
  excerpt: string
}

export interface TokenUsage {
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  is_escalated?: boolean
  cached?: boolean
  sources?: SourceDocument[]
  token_usage?: TokenUsage
  latency_ms?: number
  error?: boolean
}

export interface MetricsSummary {
  total_queries: number
  escalated_queries: number
  resolved_by_ai_queries: number
  escalation_rate_pct: number
  tokens: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
    tokens_saved_by_cache: number
  }
  costs: {
    estimated_cost_usd: number
    estimated_cost_cop: number
    savings_by_cache_usd: number
    savings_by_cache_cop: number
    local_ollama_actual_cost: string
  }
  performance: {
    avg_latency_ms: number
    cache: {
      cache_size: number
      max_size: number
      hits: number
      misses: number
      hit_rate_pct: number
      tokens_saved: number
      enabled: boolean
    }
    uptime_seconds: number
  }
  intents?: Record<string, number>
}

export interface ChatSessionSummary {
  id: string
  channel: string
  user_id: string | null
  created_at: string
  last_activity_at: string
  message_count: number
  escalated_count: number
  last_message: string | null
}

export interface SessionMessage {
  id: number
  session_id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  is_escalated: number
  created_at: string
}

export interface EscalationTicket {
  id: number
  session_id: string
  intent: string
  contact_reason: string | null
  status: 'abierto' | 'en_proceso' | 'cerrado'
  created_at: string
  updated_at: string
  channel?: string | null
}

export interface HealthStatus {
  status: string
  service: string
  environment: string
  chromadb: {
    status: string
    indexed_chunks: number
    ready: boolean
  }
  ollama: {
    model: string
    base_url: string
    connected: boolean
  }
}
