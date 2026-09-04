<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import Swal from 'sweetalert2'
import moment from 'moment'
import 'moment/locale/es'
import type { ChatMessage } from './types/chat'
import { translations, type Language } from './i18n/translations'
import {
  sendChatMessage,
  fetchHealth,
  fetchMetrics,
  fetchCurrentUser,
  clearAuthSession,
  exportChatPdf
} from './services/api'
import Navbar from './components/Navbar.vue'
import QuickPrompts from './components/QuickPrompts.vue'
import ChatMessageItem from './components/ChatMessage.vue'
import MetricsModal from './components/MetricsModal.vue'
import ExportPdfModal from './components/ExportPdfModal.vue'
import EscalationToast from './components/EscalationToast.vue'
import AuthModal from './components/AuthModal.vue'

// State
const isDark = ref(true)
const currentLang = ref<Language>('es')
const isOnline = ref(true)
const totalQueries = ref(0)
const showMetrics = ref(false)
const showExportPdf = ref(false)
const showAuthModal = ref(false)
const currentUser = ref<any | null>(null)
const isExportingDirectPdf = ref(false)

// Escalation Toast notification state
const showEscalationToast = ref(false)
const escalationToastType = ref<'whatsapp' | 'email' | 'auto_escalate'>('auto_escalate')
let toastTimer: number | null = null

const inputMessage = ref('')
const isLoading = ref(false)
const bypassCache = ref(false)
const chatContainer = ref<HTMLElement | null>(null)
const currentSessionId = ref('sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7))

// Current locale dictionary
const t = computed(() => translations[currentLang.value])

const messages = ref<ChatMessage[]>([
  {
    id: 'welcome-1',
    role: 'assistant',
    content: translations.es.welcomeMessage,
    timestamp: moment().format('LT')
  }
])

function triggerEscalationToast(type: 'whatsapp' | 'email' | 'auto_escalate') {
  escalationToastType.value = type
  showEscalationToast.value = true
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    showEscalationToast.value = false
  }, 6000)
}

function handleEscalationAction(payload: { type: 'whatsapp' | 'email'; contact: string }) {
  triggerEscalationToast(payload.type)
}

function toggleTheme() {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

function toggleLanguage() {
  currentLang.value = currentLang.value === 'es' ? 'en' : 'es'
  moment.locale(currentLang.value)
  if (messages.value.length === 1 && messages.value[0].role === 'assistant') {
    messages.value[0].content = t.value.welcomeMessage
  }
}

async function checkSystemHealth() {
  try {
    const health = await fetchHealth()
    isOnline.value = health.chromadb.ready
    const metrics = await fetchMetrics()
    totalQueries.value = metrics.total_queries
  } catch {
    isOnline.value = false
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

async function handleSendMessage(customText?: string) {
  const text = (customText || inputMessage.value).trim()
  if (!text || isLoading.value) return

  const userMsg: ChatMessage = {
    id: `user-${Date.now()}`,
    role: 'user',
    content: text,
    timestamp: moment().format('LT')
  }

  messages.value.push(userMsg)
  inputMessage.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const result = await sendChatMessage(text, currentSessionId.value, bypassCache.value, currentLang.value)

    const botMsg: ChatMessage = {
      id: `bot-${Date.now()}`,
      role: 'assistant',
      content: result.response,
      timestamp: moment().format('LT'),
      is_escalated: result.is_escalated,
      cached: result.cached,
      sources: result.sources,
      token_usage: result.token_usage,
      latency_ms: result.latency_ms
    }

    messages.value.push(botMsg)
    totalQueries.value += 1

    if (result.is_escalated) {
      triggerEscalationToast('auto_escalate')
    }
  } catch (err: any) {
    const errorMsg: ChatMessage = {
      id: `err-${Date.now()}`,
      role: 'assistant',
      content: `${t.value.connectionError} (${err.message || 'Error'}).`,
      timestamp: moment().format('LT'),
      error: true
    }
    messages.value.push(errorMsg)
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

async function clearChat() {
  const result = await Swal.fire({
    title: currentLang.value === 'es' ? '¿Limpiar historial?' : 'Clear conversation?',
    text: currentLang.value === 'es' ? 'Se restablecerá la conversación actual.' : 'The conversation will be reset.',
    icon: 'question',
    showCancelButton: true,
    confirmButtonColor: '#d97706',
    cancelButtonColor: isDark.value ? '#44403c' : '#78716c',
    confirmButtonText: currentLang.value === 'es' ? 'Sí, limpiar' : 'Yes, clear',
    cancelButtonText: currentLang.value === 'es' ? 'Cancelar' : 'Cancel',
    background: isDark.value ? '#1c1917' : '#ffffff',
    color: isDark.value ? '#f5f5f4' : '#1c1917',
    iconColor: '#d97706'
  })

  if (result.isConfirmed) {
    currentSessionId.value = 'sess_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7)
    messages.value = [
      {
        id: `welcome-reset-${Date.now()}`,
        role: 'assistant',
        content: t.value.welcomeReset,
        timestamp: moment().format('LT')
      }
    ]
  }
}

function openMetricsProtected() {
  if (currentUser.value) {
    showMetrics.value = true
  } else {
    showAuthModal.value = true
  }
}

function handleAuthenticated(user: any) {
  currentUser.value = user
  showAuthModal.value = false
  showMetrics.value = true
}

function handleLogout() {
  clearAuthSession()
  currentUser.value = null
  showMetrics.value = false
  Swal.fire({
    toast: true,
    position: 'top-end',
    icon: 'info',
    title: 'Sesión Finalizada',
    text: 'Has cerrado sesión correctamente.',
    showConfirmButton: false,
    timer: 2500,
    background: isDark.value ? '#1c1917' : '#ffffff',
    color: isDark.value ? '#f5f5f4' : '#1c1917'
  })
}

async function handleDirectExportPdf() {
  if (isExportingDirectPdf.value || messages.value.length === 0) return
  isExportingDirectPdf.value = true
  try {
    const filename = `gastroteacher_chat_${Date.now()}.pdf`
    const blob = await exportChatPdf(messages.value, currentSessionId.value)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    setTimeout(() => {
      try {
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)
      } catch {}
    }, 2500)

    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: '¡PDF Descargado!',
      text: `Archivo guardado: ${filename}`,
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true,
      background: isDark.value ? '#1c1917' : '#ffffff',
      color: isDark.value ? '#f5f5f4' : '#1c1917',
      iconColor: '#10b981'
    })
  } catch (err: any) {
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'error',
      title: 'Error de exportación',
      text: err.message || 'No se pudo generar el archivo PDF.',
      showConfirmButton: false,
      timer: 4000,
      background: isDark.value ? '#1c1917' : '#ffffff',
      color: isDark.value ? '#f5f5f4' : '#1c1917'
    })
  } finally {
    isExportingDirectPdf.value = false
  }
}

onMounted(async () => {
  moment.locale('es')
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  }
  checkSystemHealth()
  try {
    const user = await fetchCurrentUser()
    if (user) {
      currentUser.value = user
    }
  } catch {}
})
</script>

<template>
  <div
    class="min-h-screen flex flex-col font-sans transition-colors duration-200 antialiased relative selection:bg-amber-600 selection:text-white"
    :class="
      isDark
        ? 'bg-stone-950 text-stone-100'
        : 'bg-stone-100 text-stone-950'
    "
  >
    <!-- Background Constructivist Blueprint Grid & Angular Accents -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <!-- Architectural Drafting Grid -->
      <div
        class="absolute inset-0 opacity-40 dark:opacity-25"
        style="background-image: linear-gradient(to right, rgba(217, 119, 6, 0.12) 1px, transparent 1px), linear-gradient(to bottom, rgba(217, 119, 6, 0.12) 1px, transparent 1px); background-size: 32px 32px;"
      ></div>
      <!-- Asymmetric diagonal background color planes -->
      <div
        class="absolute -top-32 right-0 w-125 h-125 bg-amber-600/10 dark:bg-amber-500/10 rotate-12 -skew-x-12 blur-2xl pointer-events-none"
      ></div>
      <div
        class="absolute bottom-0 -left-20 w-100 h-100 bg-orange-700/10 dark:bg-orange-600/10 -rotate-12 skew-y-6 blur-2xl pointer-events-none"
      ></div>
    </div>

    <!-- Escalation Toast Notification (Anime.js + Moment.js) -->
    <EscalationToast
      :show="showEscalationToast"
      :type="escalationToastType"
      :is-dark="isDark"
      :lang="currentLang"
      @close="showEscalationToast = false"
    />

    <!-- Header Navbar -->
    <Navbar
      :is-dark="isDark"
      :is-online="isOnline"
      :total-queries="totalQueries"
      :current-lang="currentLang"
      :labels="{
        subtitle: t.subtitle,
        statusOnline: t.statusOnline,
        statusOffline: t.statusOffline,
        metricsBtn: t.metricsBtn,
        exportPdfBtn: t.exportPdfBtn,
        themeLight: t.themeLight,
        themeDark: t.themeDark
      }"
      @toggle-theme="toggleTheme"
      @toggle-lang="toggleLanguage"
      @open-metrics="openMetricsProtected"
      @open-export-pdf="showExportPdf = true"
    />

    <!-- Main Container -->
    <main class="relative z-10 flex-1 max-w-5xl w-full mx-auto p-3 sm:p-6 flex flex-col gap-4">
      <!-- Constructivist Chat Card Window -->
      <div
        class="flex-1 flex flex-col border-2 transition-all duration-200 overflow-hidden min-h-145 max-h-[calc(100vh-130px)] relative"
        :class="
          isDark
            ? 'bg-stone-900 border-stone-700 shadow-[6px_6px_0px_0px_#d97706]'
            : 'bg-white border-stone-900 shadow-[6px_6px_0px_0px_#1c1917]'
        "
      >
        <!-- Constructivist Top Action Bar -->
        <div
          class="px-4 sm:px-6 py-2.5 border-b-2 flex items-center justify-between gap-3 font-mono text-xs font-black shrink-0"
          :class="isDark ? 'border-stone-700 bg-stone-950 text-stone-300' : 'border-stone-900 bg-stone-100 text-stone-900'"
        >
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 bg-emerald-500 animate-pulse"></span>
            <span class="tracking-wider uppercase">// CANAL ACTIVO // REGISTRO OFICIAL</span>
            <span class="text-[10px] px-1.5 py-0.2 bg-amber-600 text-white">[MSG: {{ messages.length }}]</span>
          </div>

          <div class="flex items-center gap-2">
            <!-- Direct PDF Export Button -->
            <button
              type="button"
              @click="handleDirectExportPdf"
              :disabled="isExportingDirectPdf || messages.length === 0"
              class="flex items-center gap-1.5 px-3 py-1 font-mono text-xs font-black border-2 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 disabled:opacity-50 cursor-pointer shadow-[2px_2px_0px_0px_#e11d48]"
              :class="isDark ? 'bg-stone-800 text-rose-300 border-rose-500' : 'bg-white text-rose-900 border-stone-900'"
              title="Descargar conversación actual en PDF con 1 clic"
            >
              <svg v-if="!isExportingDirectPdf" class="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="12" y1="18" x2="12" y2="12"/>
                <line x1="9" y1="15" x2="12" y2="18"/>
                <line x1="15" y1="15" x2="12" y2="18"/>
              </svg>
              <svg v-else class="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
              </svg>
              <span>{{ isExportingDirectPdf ? 'PROCESANDO...' : 'DESCARGAR PDF' }}</span>
            </button>
          </div>
        </div>

        <!-- Conversation Area -->
        <div
          ref="chatContainer"
          class="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4 scroll-smooth"
        >
          <!-- Messages List -->
          <ChatMessageItem
            v-for="msg in messages"
            :key="msg.id"
            :message="msg"
            :is-dark="isDark"
            :labels="{
              you: t.you,
              assistant: t.assistant,
              escalatedTitle: t.escalatedTitle,
              escalatedDesc: t.escalatedDesc,
              whatsappBtn: t.whatsappBtn,
              emailBtn: t.emailBtn,
              cachedBadge: t.cachedBadge,
              viewSources: t.viewSources,
              hideSources: t.hideSources,
              officialDocs: t.officialDocs
            }"
            @escalation-action="handleEscalationAction"
          />

          <!-- Loading Indicator (Constructivist Square LED) -->
          <div v-if="isLoading" class="flex items-center gap-3 p-3 border-2 border-amber-600 bg-amber-50 dark:bg-stone-900 text-stone-950 dark:text-amber-300 w-fit font-mono text-xs font-black shadow-[3px_3px_0px_0px_#d97706]">
            <div class="flex space-x-1.5">
              <div class="w-2 h-2 bg-amber-600 animate-pulse" style="animation-delay: 0ms"></div>
              <div class="w-2 h-2 bg-amber-600 animate-pulse" style="animation-delay: 150ms"></div>
              <div class="w-2 h-2 bg-amber-600 animate-pulse" style="animation-delay: 300ms"></div>
            </div>
            <span>// PROCESANDO RESPUESTA...</span>
          </div>
        </div>

        <!-- Chat Bottom Control Area -->
        <div
          class="p-3 sm:p-5 border-t-2 transition-colors duration-200 space-y-3"
          :class="isDark ? 'bg-stone-950 border-stone-700' : 'bg-stone-100 border-stone-900'"
        >
          <!-- Quick Suggestions -->
          <QuickPrompts
            :label-title="t.frequentQuestions"
            :prompts="t.prompts"
            @select-prompt="handleSendMessage"
          />

          <!-- Input Box & Actions Form -->
          <form @submit.prevent="() => handleSendMessage()" class="flex flex-col sm:flex-row items-center gap-2">
            <!-- Text Input -->
            <div class="relative flex-1 w-full">
              <input
                v-model="inputMessage"
                type="text"
                :placeholder="t.inputPlaceholder"
                :disabled="isLoading"
                class="w-full pl-4 pr-10 py-3 text-sm outline-hidden border-2 font-mono font-medium transition-colors"
                :class="
                  isDark
                    ? 'bg-stone-900 border-stone-700 text-stone-100 placeholder-stone-500 focus:border-amber-500'
                    : 'bg-white border-stone-900 text-stone-950 placeholder-stone-600 focus:border-amber-600'
                "
              />
              <!-- Clear chat inside input -->
              <button
                v-if="messages.length > 2"
                type="button"
                @click="clearChat"
                :title="t.clearChatTitle"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-stone-500 hover:text-stone-950 dark:text-stone-400 dark:hover:text-stone-200 cursor-pointer"
              >
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>

            <!-- Action Buttons Group -->
            <div class="flex items-center gap-2 w-full sm:w-auto justify-between sm:justify-start">
              <!-- Bypass cache toggle -->
              <label
                class="flex items-center gap-1.5 font-mono text-[11px] font-black text-stone-900 dark:text-stone-300 cursor-pointer select-none px-2.5 py-2 border-2 border-stone-800 dark:border-stone-700 bg-white dark:bg-stone-900 transition-colors"
                :title="t.noCacheTitle"
              >
                <input
                  type="checkbox"
                  v-model="bypassCache"
                  class="accent-amber-600 w-3.5 h-3.5"
                />
                <span>{{ t.noCache.toUpperCase() }}</span>
              </label>

              <!-- Send Button -->
              <button
                type="submit"
                :disabled="!inputMessage.trim() || isLoading"
                class="flex items-center justify-center gap-2 px-5 py-3 font-mono text-xs font-black uppercase tracking-wider border-2 border-stone-900 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 disabled:opacity-50 disabled:pointer-events-none cursor-pointer shadow-[3px_3px_0px_0px_#1c1917] dark:shadow-[3px_3px_0px_0px_#f59e0b]"
                :class="
                  isDark
                    ? 'bg-amber-600 hover:bg-amber-500 text-white'
                    : 'bg-amber-600 hover:bg-amber-700 text-white'
                "
              >
                <span>{{ t.sendBtn }}</span>
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>

    <!-- Metrics Modal -->
    <MetricsModal
      v-if="showMetrics"
      :is-dark="isDark"
      :current-user="currentUser"
      :labels="{
        metricsTitle: t.metricsTitle,
        metricsSubtitle: t.metricsSubtitle,
        loadingMetrics: t.loadingMetrics,
        totalQueries: t.totalQueries,
        resolvedByAI: t.resolvedByAI,
        humanEscalation: t.humanEscalation,
        cacheHits: t.cacheHits,
        tokenSectionTitle: t.tokenSectionTitle,
        totalTokens: t.totalTokens,
        savedTokens: t.savedTokens,
        localCost: t.localCost,
        freeLocal: t.freeLocal,
        avgLatency: t.avgLatency,
        cacheSize: t.cacheSize,
        uptime: t.uptime,
        resetMetricsBtn: t.resetMetricsBtn,
        resettingBtn: t.resettingBtn,
        resetConfirm: t.resetConfirm,
        closeBtn: t.closeBtn,
        sweetAlertWarningTitle: t.sweetAlertWarningTitle,
        sweetAlertWarningText: t.sweetAlertWarningText,
        sweetAlertConfirmBtn: t.sweetAlertConfirmBtn,
        sweetAlertCancelBtn: t.sweetAlertCancelBtn,
        sweetAlertSuccessTitle: t.sweetAlertSuccessTitle,
        sweetAlertSuccessText: t.sweetAlertSuccessText,
        sweetAlertOkBtn: t.sweetAlertOkBtn
      }"
      @metrics-reset="totalQueries = 0"
      @logout="handleLogout"
      @unauthorized="showMetrics = false; showAuthModal = true"
      @close="showMetrics = false"
    />

    <!-- Authentication Modal (Login & Register for Metrics) -->
    <AuthModal
      :is-open="showAuthModal"
      :is-dark="isDark"
      @authenticated="handleAuthenticated"
      @close="showAuthModal = false"
    />

    <!-- PDF Export Modal -->
    <ExportPdfModal
      :is-open="showExportPdf"
      :is-dark="isDark"
      :messages="messages"
      :session-id="currentSessionId"
      :labels="{
        exportModalTitle: t.exportModalTitle,
        exportModalSubtitle: t.exportModalSubtitle,
        exportChatTitle: t.exportChatTitle,
        exportChatDesc: t.exportChatDesc,
        exportChatAction: t.exportChatAction,
        exportDocsTitle: t.exportDocsTitle,
        exportDocsDesc: t.exportDocsDesc,
        exportSuccessAlertTitle: t.exportSuccessAlertTitle,
        exportSuccessAlertText: t.exportSuccessAlertText,
        closeBtn: t.closeBtn
      }"
      @close="showExportPdf = false"
    />
  </div>
</template>
