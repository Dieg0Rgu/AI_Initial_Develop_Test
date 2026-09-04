import type { MetricsSummary, HealthStatus } from '../types/chat'

// If running in production with external backend (Render/Railway/túnel), use VITE_API_URL or VITE_API_BASE_URL.
// In same-domain Vercel deployment, defaults to '' (relative paths /api/...).
// In local Vite dev server, defaults to 'http://localhost:8000'.
const rawUrl = (import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')).trim()
const API_BASE = rawUrl.endsWith('/api') ? rawUrl.slice(0, -4) : rawUrl.replace(/\/+$/, '')

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
  const token = getAuthToken()
  const headers: Record<string, string> = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}/api/metrics`, { headers })
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('401_UNAUTHORIZED')
    }
    throw new Error('Failed to fetch metrics')
  }
  return await res.json()
}

export async function resetMetrics(): Promise<void> {
  const token = getAuthToken()
  const headers: Record<string, string> = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}/api/metrics/reset`, { method: 'POST', headers })
  if (!res.ok) {
    if (res.status === 401) {
      throw new Error('401_UNAUTHORIZED')
    }
    throw new Error('Failed to reset metrics')
  }
}

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${API_BASE}/api/health`)
  if (!res.ok) {
    throw new Error('Health check failed')
  }
  return await res.json()
}

// -------------------------------------------------------------
// Authentication Services (Login & Register for Metrics)
// -------------------------------------------------------------
const AUTH_TOKEN_KEY = 'gastroteacher_auth_token'
const AUTH_USER_KEY = 'gastroteacher_auth_user'

export function getAuthToken(): string | null {
  try {
    return localStorage.getItem(AUTH_TOKEN_KEY)
  } catch {
    return null
  }
}

export function setAuthSession(token: string, user: any) {
  try {
    localStorage.setItem(AUTH_TOKEN_KEY, token)
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user))
  } catch {}
}

export function getStoredUser(): any | null {
  try {
    const raw = localStorage.getItem(AUTH_USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function clearAuthSession() {
  try {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    localStorage.removeItem(AUTH_USER_KEY)
  } catch {}
}

export async function loginUser(usernameOrEmail: string, password: string): Promise<{ token: string; user: any }> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username_or_email: usernameOrEmail,
      password: password
    })
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al iniciar sesión.')
  }

  const data = await res.json()
  setAuthSession(data.token, data.user)
  return data
}

export async function registerUser(payload: {
  email: string
  username: string
  password: string
  full_name: string
  role?: string
}): Promise<{ token: string; user: any }> {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || 'Error al registrar la cuenta.')
  }

  const data = await res.json()
  setAuthSession(data.token, data.user)
  return data
}

export async function fetchCurrentUser(): Promise<any | null> {
  const token = getAuthToken()
  if (!token) return null

  try {
    const res = await fetch(`${API_BASE}/api/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (!res.ok) {
      clearAuthSession()
      return null
    }
    const data = await res.json()
    return data.user
  } catch {
    return null
  }
}

