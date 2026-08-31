import type { MetricsSummary, HealthStatus } from '../types/chat'

const API_BASE = import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')

export async function sendChatMessage(
  message: string,
  sessionId = 'frontend_user',
  bypassCache = false,
  language: 'es' | 'en' = 'es'
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
      bypass_cache: bypassCache,
      language
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
  channel = 'web_form',
  language: 'es' | 'en' = 'es'
) {
  const res = await fetch(`${API_BASE}/api/webhook`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      sender_id: senderId,
      channel,
      metadata: { language }
    })
  })

  if (!res.ok) {
    throw new Error(`Webhook error: ${res.status}`)
  }

  return await res.json()
}

export async function exportChatPdf(
  messages: Array<{ role: string; content: string; [key: string]: any }>,
  sessionId = 'frontend_user'
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/export/chat-pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      messages: messages.map(m => ({
        role: m.role,
        content: m.content,
        is_escalated: m.is_escalated || false,
        sources: m.sources || [],
        latency_ms: m.latency_ms || 0,
        token_usage: m.token_usage || {}
      })),
      metadata: {
        exported_at: new Date().toISOString(),
        channel: 'web_frontend'
      }
    })
  })

  if (!res.ok) {
    throw new Error(`Failed to export PDF: ${res.status}`)
  }

  return await res.blob()
}

export async function exportChatMd(
  messages: Array<{ role: string; content: string; [key: string]: any }>,
  sessionId = 'frontend_user'
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/export/chat-md`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      messages: messages.map(m => ({
        role: m.role,
        content: m.content,
        is_escalated: m.is_escalated || false,
        sources: m.sources || [],
        latency_ms: m.latency_ms || 0,
        token_usage: m.token_usage || {}
      })),
      metadata: {
        exported_at: new Date().toISOString(),
        channel: 'web_frontend'
      }
    })
  })

  if (!res.ok) {
    throw new Error(`Failed to export Markdown: ${res.status}`)
  }

  return await res.blob()
}

export async function exportChatTxt(
  messages: Array<{ role: string; content: string; [key: string]: any }>,
  sessionId = 'frontend_user'
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/export/chat-txt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      messages: messages.map(m => ({
        role: m.role,
        content: m.content,
        is_escalated: m.is_escalated || false,
        sources: m.sources || [],
        latency_ms: m.latency_ms || 0,
        token_usage: m.token_usage || {}
      })),
      metadata: {
        exported_at: new Date().toISOString(),
        channel: 'web_frontend'
      }
    })
  })

  if (!res.ok) {
    throw new Error(`Failed to export TXT: ${res.status}`)
  }

  return await res.blob()
}

export async function fetchOfficialDocuments(): Promise<Array<{
  id: string
  title: string
  filename: string
  md_filename?: string
  size_kb: number
  download_url: string
}>> {
  const res = await fetch(`${API_BASE}/api/export/documents`)
  if (!res.ok) {
    throw new Error('Failed to list documents')
  }
  const data = await res.json()
  return data.documents || []
}

export async function downloadOfficialDocFile(filename: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/export/documents/${filename}`)
  if (!res.ok) {
    throw new Error(`Failed to download ${filename}`)
  }
  return await res.blob()
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
