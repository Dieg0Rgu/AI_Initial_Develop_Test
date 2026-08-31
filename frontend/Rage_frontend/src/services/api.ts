import type { MetricsSummary, HealthStatus } from '../types/chat'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export async function sendChatMessage(
  message: string,
  sessionId = 'frontend_user',
  bypassCache = false
): Promise<{
  response: string
  is_escalated: boolean
  cached: boolean
  sources: any[]
  token_usage: any
  latency_ms: number
  session_id: string
}> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      bypass_cache: bypassCache
    })
  })

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}))
    throw new Error(errorData.detail || `Server error: ${res.status}`)
  }

  return await res.json()
}

export async function sendWebhookMessage(
  message: string,
  senderId = 'web_form_user',
  channel = 'web_form'
) {
  const res = await fetch(`${API_BASE}/api/webhook`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      sender_id: senderId,
      channel
    })
  })

  if (!res.ok) {
    throw new Error(`Webhook error: ${res.status}`)
  }

  return await res.json()
}

export async function fetchMetrics(): Promise<MetricsSummary> {
  const res = await fetch(`${API_BASE}/api/metrics`)
  if (!res.ok) {
    throw new Error('Failed to fetch metrics')
  }
  return await res.json()
}

export async function resetMetrics(): Promise<void> {
  await fetch(`${API_BASE}/api/metrics/reset`, { method: 'POST' })
}

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/api/health`)
  if (!res.ok) {
    throw new Error('Health check failed')
  }
  return await res.json()
}
