<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import type { ChatMessage } from './types/chat'
import { sendChatMessage, fetchHealth, fetchMetrics } from './services/api'
import Navbar from './components/Navbar.vue'
import QuickPrompts from './components/QuickPrompts.vue'
import ChatMessageItem from './components/ChatMessage.vue'
import MetricsModal from './components/MetricsModal.vue'

// State
const isDark = ref(true)
const isOnline = ref(true)
const totalQueries = ref(0)
const showMetrics = ref(false)

const inputMessage = ref('')
const isLoading = ref(false)
const bypassCache = ref(false)
const chatContainer = ref<HTMLElement | null>(null)

const messages = ref<ChatMessage[]>([
  {
    id: 'welcome-1',
    role: 'assistant',
    content: '¡Hola! Bienvenido a **Gastroteacher Academy** 👨‍🍳📚\n\nSoy tu asistente virtual con RAG. Puedo ayudarte con información precisa y verificada sobre nuestros cursos de inglés gastronómico y general, horarios, precios en COP, modalidades, certificaciones y proceso de matrícula.\n\n¿En qué te puedo colaborar hoy?',
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
    const result = await sendChatMessage(text, 'web_session', bypassCache.value)

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
      content: `⚠️ Error al conectar con el servidor: ${err.message || 'Verifica que el backend de FastAPI esté corriendo en el puerto 8000.'}`,
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
  if (!confirm('¿Deseas reiniciar la conversación?')) return
  messages.value = [
    {
      id: 'welcome-reset',
      role: 'assistant',
      content: '¡Conversación reiniciada! ¿Qué información sobre Gastroteacher deseas consultar?',
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
      @toggle-theme="toggleTheme"
      @open-metrics="showMetrics = true"
    />

    <!-- Main Container -->
    <main class="relative z-10 flex-1 max-w-5xl w-full mx-auto p-3 sm:p-6 flex flex-col gap-4">
      <!-- Chat Card Window -->
      <div
        class="flex-1 flex flex-col rounded-3xl backdrop-blur-2xl border shadow-xl transition-all duration-300 overflow-hidden min-h-145 max-h-[calc(100vh-140px)]"
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
            <span class="text-xs font-medium">Consultando base de conocimiento RAG & sintetizando...</span>
          </div>
        </div>

        <!-- Chat Bottom Control Area -->
        <div
          class="p-3 sm:p-5 border-t backdrop-blur-xl transition-colors duration-300 space-y-3"
          :class="isDark ? 'bg-stone-900/85 border-stone-800' : 'bg-white/85 border-stone-200'"
        >
          <!-- Quick Suggestions -->
          <QuickPrompts @select-prompt="handleSendMessage" />

          <!-- Input Box & Actions Form -->
          <form @submit.prevent="() => handleSendMessage()" class="flex flex-col sm:flex-row items-center gap-2">
            <!-- Text Input -->
            <div class="relative flex-1 w-full">
              <input
                v-model="inputMessage"
                type="text"
                placeholder="Escribe tu consulta sobre horarios, precios, programas, certificaciones..."
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
                title="Limpiar chat"
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
                title="Forzar respuesta fresca de la IA omitiendo la memoria caché"
              >
                <input
                  type="checkbox"
                  v-model="bypassCache"
                  class="rounded text-amber-600 focus:ring-amber-500"
                />
                <span>Sin Caché</span>
              </label>

              <!-- Send Button -->
              <button
                type="submit"
                :disabled="!inputMessage.trim() || isLoading"
                class="flex items-center justify-center gap-2 px-5 py-3 rounded-2xl text-sm font-semibold transition-all duration-200 shadow-md hover:scale-102 active:scale-98 disabled:opacity-50 disabled:pointer-events-none cursor-pointer"
                :class="
                  isDark
                    ? 'bg-linear-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white shadow-amber-900/20'
                    : 'bg-linear-to-r from-amber-700 to-orange-700 hover:from-amber-600 hover:to-orange-600 text-white shadow-amber-900/10'
                "
              >
                <span>Enviar</span>
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
      @close="showMetrics = false"
    />
  </div>
</template>
