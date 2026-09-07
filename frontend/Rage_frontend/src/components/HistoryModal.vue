<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Swal from 'sweetalert2'
import type { ChatSessionSummary, SessionMessage, EscalationTicket } from '../types/chat'
import { fetchSessions, fetchSessionMessages, fetchTickets, updateTicketStatus } from '../services/api'

const props = defineProps<{
  isDark: boolean
  labels: {
    title: string
    subtitle: string
    tabHistory: string
    tabTickets: string
    noSessions: string
    noTickets: string
    sessionChannel: string
    sessionMessages: string
    sessionEscalations: string
    openTranscript: string
    backToSessions: string
    emptyTranscript: string
    ticketIntent: string
    ticketReason: string
    ticketStatus: string
    ticketCreated: string
    statusOpen: string
    statusInProgress: string
    statusClosed: string
    statusUpdated: string
    closeBtn: string
  }
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const activeTab = ref<'history' | 'tickets'>('history')
const sessions = ref<ChatSessionSummary[]>([])
const tickets = ref<EscalationTicket[]>([])
const loading = ref(false)
const selectedSession = ref<ChatSessionSummary | null>(null)
const transcript = ref<SessionMessage[]>([])
const updatingTicketId = ref<number | null>(null)

const STATUS_META: Record<string, { label: string; cls: string }> = {
  abierto: { label: props.labels.statusOpen, cls: 'bg-rose-500/15 border-rose-500/40 text-rose-700 dark:text-rose-400' },
  en_proceso: { label: props.labels.statusInProgress, cls: 'bg-amber-500/15 border-amber-500/40 text-amber-700 dark:text-amber-400' },
  cerrado: { label: props.labels.statusClosed, cls: 'bg-emerald-500/15 border-emerald-500/40 text-emerald-700 dark:text-emerald-400' }
}

async function loadSessions() {
  loading.value = true
  try {
    sessions.value = await fetchSessions(50)
  } catch (err: any) {
    console.error('Failed to load sessions', err)
    sessions.value = []
  } finally {
    loading.value = false
  }
}

async function loadTickets() {
  loading.value = true
  try {
    tickets.value = await fetchTickets()
  } catch (err: any) {
    console.error('Failed to load tickets', err)
    tickets.value = []
  } finally {
    loading.value = false
  }
}

function switchTab(tab: 'history' | 'tickets') {
  activeTab.value = tab
  selectedSession.value = null
  transcript.value = []
  if (tab === 'history') loadSessions()
  else loadTickets()
}

async function openSession(session: ChatSessionSummary) {
  selectedSession.value = session
  transcript.value = []
  try {
    transcript.value = await fetchSessionMessages(session.id)
  } catch (err: any) {
    console.error('Failed to load transcript', err)
    transcript.value = []
  }
}

function backToSessions() {
  selectedSession.value = null
  transcript.value = []
}

function formatDate(iso: string): string {
  if (!iso) return '—'
  try {
    const d = new Date(iso.replace(' ', 'T'))
    return d.toLocaleString('es-CO', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
  } catch {
    return iso
  }
}

function intentLabel(intent: string): string {
  const map: Record<string, string> = {
    REFUND: 'Reembolso',
    TECHNICAL: 'Soporte Técnico',
    CORPORATE: 'Convenio Corporativo',
    IMMIGRATION: 'Visas / Migración',
    RECIPES: 'Recetas / Fuera de Alcance',
    HUMAN: 'Asesor Humano',
    INJECTION: 'Intento de Inyección',
    faq_escalation: 'Escalamiento FAQ',
    fuera_de_alcance: 'Fuera de Alcance'
  }
  return map[intent] || intent
}

async function setTicketStatus(ticket: EscalationTicket, status: 'abierto' | 'en_proceso' | 'cerrado') {
  updatingTicketId.value = ticket.id
  try {
    await updateTicketStatus(ticket.id, status)
    await loadTickets()
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: props.labels.statusUpdated,
      showConfirmButton: false,
      timer: 2000,
      background: props.isDark ? '#1c1917' : '#ffffff',
      color: props.isDark ? '#f5f5f4' : '#1c1917'
    })
  } catch (err: any) {
    console.error('Failed to update ticket', err)
  } finally {
    updatingTicketId.value = null
  }
}

onMounted(() => {
  loadSessions()
})
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-950/70 backdrop-blur-xs transition-opacity">
    <div
      class="w-full max-w-3xl border-2 p-5 sm:p-7 transition-all duration-200 relative overflow-hidden flex flex-col max-h-[90vh]"
      :class="isDark ? 'bg-stone-950 border-stone-700 text-stone-100 shadow-[8px_8px_0px_0px_#d97706]' : 'bg-white border-stone-900 text-stone-950 shadow-[8px_8px_0px_0px_#1c1917]'"
    >
      <!-- Corner Marks -->
      <div class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-amber-600 pointer-events-none"></div>
      <div class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-amber-600 pointer-events-none"></div>

      <!-- Modal Header -->
      <div
        class="flex items-center justify-between gap-3 mb-4 pb-3 border-b-2"
        :class="isDark ? 'border-stone-800' : 'border-stone-900'"
      >
        <div class="flex items-center gap-3">
          <div class="p-2 border-2 border-stone-900 dark:border-amber-500 bg-amber-500/10 text-amber-700 dark:text-amber-400">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M3 5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-5 4V5z"/>
              <line x1="8" y1="9" x2="16" y2="9"/>
              <line x1="8" y1="13" x2="13" y2="13"/>
            </svg>
          </div>
          <div>
            <h3 class="font-black text-base tracking-tight uppercase text-stone-950 dark:text-stone-100 font-mono">// {{ labels.title.toUpperCase() }}</h3>
            <p class="font-mono text-[11px] text-stone-600 dark:text-stone-400">{{ labels.subtitle }}</p>
          </div>
        </div>

        <button
          type="button"
          @click="emit('close')"
          class="p-1.5 border-2 border-stone-900 dark:border-stone-700 text-stone-600 hover:text-stone-950 dark:text-stone-400 dark:hover:text-stone-200 transition-colors cursor-pointer"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Tabs -->
      <div class="flex items-center gap-2 mb-4 font-mono text-xs font-black">
        <button
          type="button"
          @click="switchTab('history')"
          class="px-3 py-1.5 border-2 transition-transform cursor-pointer"
          :class="
            activeTab === 'history'
              ? isDark
                ? 'bg-amber-600 text-white border-amber-500 shadow-[2px_2px_0px_0px_#f59e0b]'
                : 'bg-amber-600 text-white border-stone-900 shadow-[2px_2px_0px_0px_#1c1917]'
              : isDark
                ? 'bg-stone-900 border-stone-700 text-stone-400 hover:border-amber-500'
                : 'bg-white border-stone-900 text-stone-600 hover:bg-amber-50'
          "
        >
          [01] {{ labels.tabHistory }}
        </button>
        <button
          type="button"
          @click="switchTab('tickets')"
          class="px-3 py-1.5 border-2 transition-transform cursor-pointer"
          :class="
            activeTab === 'tickets'
              ? isDark
                ? 'bg-rose-600 text-white border-rose-500 shadow-[2px_2px_0px_0px_#e11d48]'
                : 'bg-rose-600 text-white border-stone-900 shadow-[2px_2px_0px_0px_#1c1917]'
              : isDark
                ? 'bg-stone-900 border-stone-700 text-stone-400 hover:border-rose-500'
                : 'bg-white border-stone-900 text-stone-600 hover:bg-rose-50'
          "
        >
          [02] {{ labels.tabTickets }}
          <span v-if="tickets.length > 0" class="ml-1 px-1.5 bg-rose-600 text-white text-[9px] rounded-none">{{ tickets.length }}</span>
        </button>
      </div>

      <!-- Body -->
      <div class="flex-1 overflow-y-auto min-h-60 pr-1">
        <!-- Loading -->
        <div v-if="loading" class="py-12 text-center text-sm font-mono font-black text-stone-900 dark:text-stone-300">
          <div class="animate-spin w-8 h-8 mx-auto mb-2 border-2 border-amber-600 border-t-transparent"></div>
          [PROCESANDO...]
        </div>

        <!-- ============ HISTORIAL TAB ============ -->
        <template v-else-if="activeTab === 'history'">
          <!-- Transcript view -->
          <div v-if="selectedSession" class="space-y-3">
            <div class="flex items-center justify-between border-b pb-2" :class="isDark ? 'border-stone-800' : 'border-stone-300'">
              <div>
                <div class="font-mono text-[11px] font-black text-amber-700 dark:text-amber-400 uppercase">
                  // {{ labels.openTranscript }}
                </div>
                <div class="font-mono text-[10px] text-stone-500 mt-0.5">{{ selectedSession.id }} · {{ formatDate(selectedSession.last_activity_at) }}</div>
              </div>
              <button
                type="button"
                @click="backToSessions"
                class="px-2.5 py-1 border-2 font-mono text-[10px] font-black uppercase cursor-pointer hover:-translate-x-0.5 hover:-translate-y-0.5 transition-transform"
                :class="isDark ? 'bg-stone-900 border-stone-700 text-stone-300' : 'bg-white border-stone-900 text-stone-900'"
              >
                ← {{ labels.backToSessions }}
              </button>
            </div>

            <div v-if="transcript.length === 0" class="py-8 text-center text-xs font-mono text-stone-500">
              {{ labels.emptyTranscript }}
            </div>

            <div v-for="msg in transcript" :key="msg.id" class="space-y-1">
              <div
                class="p-2.5 border-2 font-mono text-xs leading-relaxed"
                :class="
                  msg.role === 'user'
                    ? isDark
                      ? 'bg-amber-950/40 border-amber-600/60 text-amber-100'
                      : 'bg-amber-50 border-stone-900 text-stone-900'
                    : isDark
                      ? 'bg-stone-900 border-stone-700 text-stone-200'
                      : 'bg-stone-50 border-stone-900 text-stone-900'
                "
              >
                <div class="flex items-center justify-between text-[9px] font-black uppercase tracking-wider mb-1 opacity-70">
                  <span>{{ msg.role === 'user' ? '// USUARIO' : '// GT-SYS.ASISTENTE' }}</span>
                  <span class="flex items-center gap-1.5">
                    <span v-if="msg.is_escalated === 1" class="text-rose-600 dark:text-rose-400">[ESCALADO]</span>
                    <span>{{ formatDate(msg.created_at) }}</span>
                  </span>
                </div>
                <p class="whitespace-pre-wrap break-words">{{ msg.content }}</p>
              </div>
            </div>
          </div>

          <!-- Sessions list -->
          <div v-else-if="sessions.length === 0" class="py-12 text-center text-xs font-mono text-stone-500">
            {{ labels.noSessions }}
          </div>

          <div v-else class="space-y-2">
            <div
              v-for="session in sessions"
              :key="session.id"
              class="p-3 border-2 cursor-pointer transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0"
              :class="isDark ? 'bg-stone-900 border-stone-700 hover:border-amber-500' : 'bg-stone-50 border-stone-900 hover:border-amber-600'"
              @click="openSession(session)"
            >
              <div class="flex items-center justify-between gap-2">
                <div class="font-mono text-xs font-black text-stone-950 dark:text-stone-100 truncate">
                  {{ session.id }}
                </div>
                <div class="flex items-center gap-1.5 font-mono text-[10px] font-black shrink-0">
                  <span class="px-1.5 py-0.5 border" :class="isDark ? 'border-stone-700 text-stone-400' : 'border-stone-300 text-stone-600'">
                    {{ labels.sessionChannel }}: {{ session.channel }}
                  </span>
                  <span class="px-1.5 py-0.5 border border-amber-600 text-amber-700 dark:text-amber-400">
                    {{ labels.sessionMessages }}: {{ session.message_count }}
                  </span>
                  <span v-if="session.escalated_count > 0" class="px-1.5 py-0.5 border border-rose-600 text-rose-700 dark:text-rose-400">
                    {{ labels.sessionEscalations }}: {{ session.escalated_count }}
                  </span>
                </div>
              </div>
              <div class="mt-1.5 flex items-center justify-between gap-2">
                <p class="font-mono text-[10px] text-stone-500 truncate">
                  {{ session.last_message || '—' }}
                </p>
                <span class="font-mono text-[9px] text-stone-500 shrink-0">{{ formatDate(session.last_activity_at) }}</span>
              </div>
            </div>
          </div>
        </template>

        <!-- ============ TICKETS TAB ============ -->
        <template v-else>
          <div v-if="tickets.length === 0" class="py-12 text-center text-xs font-mono text-stone-500">
            {{ labels.noTickets }}
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="ticket in tickets"
              :key="ticket.id"
              class="p-3 border-2"
              :class="isDark ? 'bg-stone-900 border-stone-700' : 'bg-stone-50 border-stone-900'"
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="flex items-center gap-2 font-mono text-xs font-black">
                  <span class="text-amber-700 dark:text-amber-400">[#{{ ticket.id }}]</span>
                  <span class="text-stone-950 dark:text-stone-100">{{ ticket.session_id }}</span>
                  <span
                    class="px-1.5 py-0.5 border text-[10px]"
                    :class="(STATUS_META[ticket.status] || STATUS_META.abierto).cls"
                  >
                    {{ (STATUS_META[ticket.status] || STATUS_META.abierto).label }}
                  </span>
                </div>
                <span class="font-mono text-[9px] text-stone-500">{{ formatDate(ticket.created_at) }}</span>
              </div>

              <div class="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                <div class="p-2 border" :class="isDark ? 'border-stone-800 bg-stone-950' : 'border-stone-300 bg-white'">
                  <span class="text-[9px] uppercase font-black text-stone-500 block">{{ labels.ticketIntent }}</span>
                  <span class="font-black text-stone-950 dark:text-stone-100">{{ intentLabel(ticket.intent) }}</span>
                </div>
                <div class="p-2 border" :class="isDark ? 'border-stone-800 bg-stone-950' : 'border-stone-300 bg-white'">
                  <span class="text-[9px] uppercase font-black text-stone-500 block">{{ labels.ticketReason }}</span>
                  <span class="text-stone-900 dark:text-stone-300 line-clamp-2">{{ ticket.contact_reason || '—' }}</span>
                </div>
              </div>

              <div class="mt-2.5 flex items-center gap-2 font-mono text-[10px] font-black">
                <span class="text-stone-500 uppercase">{{ labels.ticketStatus }}:</span>
                <button
                  type="button"
                  :disabled="updatingTicketId === ticket.id || ticket.status === 'abierto'"
                  @click="setTicketStatus(ticket, 'abierto')"
                  class="px-2 py-1 border-2 border-rose-500/60 text-rose-700 dark:text-rose-400 disabled:opacity-40 disabled:cursor-not-allowed hover:-translate-x-0.5 hover:-translate-y-0.5 transition-transform cursor-pointer bg-rose-500/10"
                >
                  {{ labels.statusOpen }}
                </button>
                <button
                  type="button"
                  :disabled="updatingTicketId === ticket.id || ticket.status === 'en_proceso'"
                  @click="setTicketStatus(ticket, 'en_proceso')"
                  class="px-2 py-1 border-2 border-amber-500/60 text-amber-700 dark:text-amber-400 disabled:opacity-40 disabled:cursor-not-allowed hover:-translate-x-0.5 hover:-translate-y-0.5 transition-transform cursor-pointer bg-amber-500/10"
                >
                  {{ labels.statusInProgress }}
                </button>
                <button
                  type="button"
                  :disabled="updatingTicketId === ticket.id || ticket.status === 'cerrado'"
                  @click="setTicketStatus(ticket, 'cerrado')"
                  class="px-2 py-1 border-2 border-emerald-500/60 text-emerald-700 dark:text-emerald-400 disabled:opacity-40 disabled:cursor-not-allowed hover:-translate-x-0.5 hover:-translate-y-0.5 transition-transform cursor-pointer bg-emerald-500/10"
                >
                  {{ labels.statusClosed }}
                </button>
                <span v-if="updatingTicketId === ticket.id" class="ml-1 animate-pulse text-stone-500">[...]</span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Footer -->
      <div class="pt-3 border-t-2 mt-3 flex justify-end" :class="isDark ? 'border-stone-800' : 'border-stone-200'">
        <button
          type="button"
          @click="emit('close')"
          class="px-4 py-2 border-2 border-stone-900 dark:border-stone-700 bg-white dark:bg-stone-900 text-xs font-black uppercase text-stone-950 dark:text-stone-200 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 cursor-pointer shadow-[2px_2px_0px_0px_#1c1917] dark:shadow-[2px_2px_0px_0px_#d97706]"
        >
          {{ labels.closeBtn }}
        </button>
      </div>
    </div>
  </div>
</template>