<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import type { ChatMessage } from './types/chat'
import { translations, type Language } from './i18n/translations'
import { sendChatMessage, fetchHealth, fetchMetrics } from './services/api'
import Navbar from './components/Navbar.vue'
import QuickPrompts from './components/QuickPrompts.vue'
import ChatMessageItem from './components/ChatMessage.vue'
import MetricsModal from './components/MetricsModal.vue'
import ExportPdfModal from './components/ExportPdfModal.vue'

// State
const isDark = ref(true)
const currentLang = ref<Language>('es')
const isOnline = ref(true)
const totalQueries = ref(0)
const showMetrics = ref(false)
const showExportPdf = ref(false)

const inputMessage = ref('')
const isLoading = ref(false)
const bypassCache = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

// Current locale dictionary
const t = computed(() => translations[currentLang.value])

const messages = ref<ChatMessage[]>([
  {
    id: 'welcome-1',
    role: 'assistant',
    content: translations.es.welcomeMessage,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
])

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
  // If only the welcome message is present, update it dynamically
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
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  messages.value.push(userMsg)
  inputMessage.value = ''
  isLoading.value = true
  scrollToBottom()

  try {
    const result = await sendChatMessage(text, 'web_session', bypassCache.value, currentLang.value)

    const botMsg: ChatMessage = {
      id: `bot-${Date.now()}`,
      role: 'assistant',
      content: result.response,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      is_escalated: result.is_escalated,
      cached: result.cached,
      sources: result.sources,
      token_usage: result.token_usage,
      latency_ms: result.latency_ms
    }

    messages.value.push(botMsg)
    totalQueries.value += 1
  } catch (err: any) {
    const errorMsg: ChatMessage = {
      id: `err-${Date.now()}`,
      role: 'assistant',
      content: `${t.value.connectionError} (${err.message || 'Error'}).`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      error: true
    }
    messages.value.push(errorMsg)
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

function clearChat() {
  if (!confirm(t.value.clearChatConfirm)) return
  messages.value = [
    {
      id: `welcome-reset-${Date.now()}`,
      role: 'assistant',
      content: t.value.welcomeReset,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]
}

onMounted(() => {
  if (isDark.value) {
    document.documentElement.classList.add('dark')
  }
  checkSystemHealth()
})
</script>

<template>
  <div
    class="min-h-screen flex flex-col font-sans transition-colors duration-300 antialiased"
    :class="
      isDark
        ? 'bg-stone-950 text-stone-100'
        : 'bg-stone-100/70 text-stone-900'
    "
  >
    <!-- Background Ambient Gradients -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <div
        class="absolute -top-40 -right-40 w-96 h-96 rounded-full blur-3xl opacity-30 transition-all duration-700"
        :class="isDark ? 'bg-amber-600/30' : 'bg-amber-400/40'"
      ></div>
      <div
        class="absolute top-1/3 -left-40 w-96 h-96 rounded-full blur-3xl opacity-20 transition-all duration-700"
        :class="isDark ? 'bg-orange-700/20' : 'bg-orange-300/30'"
      ></div>
      <div
        class="absolute -bottom-40 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-25 transition-all duration-700"
        :class="isDark ? 'bg-amber-900/30' : 'bg-stone-300/50'"
      ></div>
    </div>

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
      @open-metrics="showMetrics = true"
      @open-export-pdf="showExportPdf = true"
    />

    <!-- Main Container -->
    <main class="relative z-10 flex-1 max-w-5xl w-full mx-auto p-3 sm:p-6 flex flex-col gap-4">
      <!-- Chat Card Window -->
      <div
        class="flex-1 flex flex-col rounded-3xl backdrop-blur-2xl border shadow-xl transition-all duration-300 overflow-hidden min-h-[580px] max-h-[calc(100vh-140px)]"
        :class="
          isDark
            ? 'bg-stone-900/60 border-stone-800/80 shadow-black/40'
            : 'bg-white/70 border-stone-200/90 shadow-stone-300/30'
        "
      >
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
          />

          <!-- Loading Indicator -->
          <div v-if="isLoading" class="flex items-center gap-3 p-4 rounded-2xl w-fit backdrop-blur-md border animate-pulse"
            :class="isDark ? 'bg-stone-900/80 border-stone-800 text-stone-300' : 'bg-white/80 border-stone-200 text-stone-600'"
          >
            <div class="flex space-x-1.5">
              <div class="w-2 h-2 rounded-full bg-amber-600 animate-bounce" style="animation-delay: 0ms"></div>
              <div class="w-2 h-2 rounded-full bg-amber-600 animate-bounce" style="animation-delay: 150ms"></div>
              <div class="w-2 h-2 rounded-full bg-amber-600 animate-bounce" style="animation-delay: 300ms"></div>
            </div>
            <span class="text-xs font-medium">{{ t.loadingText }}</span>
          </div>
        </div>

        <!-- Chat Bottom Control Area -->
        <div
          class="p-3 sm:p-5 border-t backdrop-blur-xl transition-colors duration-300 space-y-3"
          :class="isDark ? 'bg-stone-900/85 border-stone-800' : 'bg-white/85 border-stone-200'"
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
                class="w-full pl-4 pr-10 py-3 rounded-2xl text-sm transition-all duration-200 outline-hidden border shadow-inner"
                :class="
                  isDark
                    ? 'bg-stone-950/70 border-stone-800 text-stone-100 placeholder-stone-500 focus:border-amber-600 focus:ring-1 focus:ring-amber-600'
                    : 'bg-stone-50 border-stone-300 text-stone-900 placeholder-stone-400 focus:border-amber-600 focus:ring-1 focus:ring-amber-600'
                "
              />
              <!-- Clear chat inside input -->
              <button
                v-if="messages.length > 2"
                type="button"
                @click="clearChat"
                :title="t.clearChatTitle"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-stone-600 dark:hover:text-stone-200 cursor-pointer"
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
                class="flex items-center gap-1.5 text-[11px] font-medium text-stone-500 dark:text-stone-400 cursor-pointer select-none px-2 py-1.5 rounded-xl hover:bg-stone-200/50 dark:hover:bg-stone-800/50 transition-colors"
                :title="t.noCacheTitle"
              >
                <input
                  type="checkbox"
                  v-model="bypassCache"
                  class="rounded text-amber-600 focus:ring-amber-500"
                />
                <span>{{ t.noCache }}</span>
              </label>

              <!-- Send Button -->
              <button
                type="submit"
                :disabled="!inputMessage.trim() || isLoading"
                class="flex items-center justify-center gap-2 px-5 py-3 rounded-2xl text-sm font-semibold transition-all duration-200 shadow-md hover:scale-102 active:scale-98 disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
                :class="
                  isDark
                    ? 'bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white shadow-amber-900/20'
                    : 'bg-gradient-to-r from-amber-700 to-orange-700 hover:from-amber-600 hover:to-orange-600 text-white shadow-amber-900/10'
                "
              >
                <span>{{ t.sendBtn }}</span>
                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
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
      @close="showMetrics = false"
    />

    <!-- PDF Export Modal -->
    <ExportPdfModal
      :is-open="showExportPdf"
      :is-dark="isDark"
      :messages="messages"
      session-id="web_session"
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
