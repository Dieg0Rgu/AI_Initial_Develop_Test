<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { exportChatPdf, fetchOfficialDocuments, downloadOfficialDocPdf } from '../services/api'
import type { ChatMessage } from '../types/chat'

const props = defineProps<{
  isOpen: boolean
  isDark: boolean
  messages: ChatMessage[]
  sessionId: string
  labels: {
    exportModalTitle: string
    exportModalSubtitle: string
    exportChatTitle: string
    exportChatDesc: string
    exportChatAction: string
    exportDocsTitle: string
    exportDocsDesc: string
    exportSuccessAlertTitle: string
    exportSuccessAlertText: string
    closeBtn: string
  }
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const isExportingChat = ref(false)
const downloadingDocId = ref<string | null>(null)
const alertSuccessMsg = ref<string | null>(null)
const officialDocs = ref<Array<{ id: string; title: string; filename: string; size_kb: number }>>([])

onMounted(async () => {
  try {
    officialDocs.value = await fetchOfficialDocuments()
  } catch (e) {
    // Fallback hardcoded list if server is loading
    officialDocs.value = [
      { id: '01_courses_modalities_levels', title: 'Cursos, Modalidades y Niveles', filename: '01_courses_modalities_levels.pdf', size_kb: 9.7 },
      { id: '02_pricing_schedules_promotions', title: 'Tarifas, Horarios y Promociones', filename: '02_pricing_schedules_promotions.pdf', size_kb: 9.3 },
      { id: '03_enrollments_certifications_policies', title: 'Inscripciones, Certificaciones y Políticas', filename: '03_enrollments_certifications_policies.pdf', size_kb: 11.0 }
    ]
  }
})

const handleExportChat = async () => {
  if (isExportingChat.value) return
  isExportingChat.value = true
  alertSuccessMsg.value = null

  try {
    const blob = await exportChatPdf(props.messages, props.sessionId)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `gastroteacher_chat_${props.sessionId}.pdf`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    alertSuccessMsg.value = `gastroteacher_chat_${props.sessionId}.pdf`
  } catch (err) {
    console.error('Export error:', err)
  } finally {
    isExportingChat.value = false
  }
}

const handleDownloadDoc = async (filename: string) => {
  if (downloadingDocId.value) return
  downloadingDocId.value = filename
  alertSuccessMsg.value = null

  try {
    const blob = await downloadOfficialDocPdf(filename)
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    alertSuccessMsg.value = filename
  } catch (err) {
    console.error('Download error:', err)
  } finally {
    downloadingDocId.value = null
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md transition-opacity duration-300"
    @click.self="emit('close')"
  >
    <div
      class="w-full max-w-2xl rounded-3xl shadow-2xl border overflow-hidden flex flex-col max-h-[90vh] transition-all transform scale-100"
      :class="isDark ? 'bg-stone-900 border-stone-800 text-stone-100' : 'bg-white border-stone-200 text-stone-900'"
    >
      <!-- Header -->
      <div
        class="px-6 py-5 border-b flex items-center justify-between"
        :class="isDark ? 'border-stone-800 bg-stone-900/90' : 'border-stone-100 bg-stone-50/90'"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-600 dark:text-amber-400">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <div>
            <h2 class="text-base sm:text-lg font-bold tracking-tight">
              {{ labels.exportModalTitle }}
            </h2>
            <p class="text-xs text-stone-500 dark:text-stone-400">
              {{ labels.exportModalSubtitle }}
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="emit('close')"
          class="p-2 rounded-xl border transition-colors cursor-pointer hover:bg-stone-200 dark:hover:bg-stone-800"
          :class="isDark ? 'border-stone-700 text-stone-400' : 'border-stone-300 text-stone-500'"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto space-y-6">
        <!-- SweetAlert Style Success Card -->
        <div
          v-if="alertSuccessMsg"
          class="p-4 rounded-2xl border flex items-start gap-3 bg-emerald-500/10 border-emerald-500/30 text-emerald-800 dark:text-emerald-300 animate-fade-in"
        >
          <div class="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center shrink-0 font-bold text-sm">
            ✓
          </div>
          <div class="flex-1">
            <h4 class="font-bold text-sm">
              {{ labels.exportSuccessAlertTitle }}
            </h4>
            <p class="text-xs mt-0.5 opacity-90">
              {{ labels.exportSuccessAlertText }} (<b>{{ alertSuccessMsg }}</b>)
            </p>
          </div>
        </div>

        <!-- Section 1: Export Current Conversation -->
        <div
          class="p-5 rounded-2xl border transition-all"
          :class="isDark ? 'bg-stone-800/40 border-stone-700/60' : 'bg-stone-50/80 border-stone-200'"
        >
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/30">
                  SESIÓN ACTIVA
                </span>
                <h3 class="font-bold text-sm">
                  {{ labels.exportChatTitle }}
                </h3>
              </div>
              <p class="text-xs text-stone-500 dark:text-stone-400 mt-1">
                {{ labels.exportChatDesc }}
              </p>
              <div class="flex items-center gap-3 mt-2 text-[11px] font-medium text-stone-500 dark:text-stone-400">
                <span>💬 {{ messages.length }} mensajes</span>
                <span>•</span>
                <span>⏱️ ReportLab PDF Engine</span>
              </div>
            </div>

            <button
              type="button"
              @click="handleExportChat"
              :disabled="isExportingChat || messages.length === 0"
              class="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white shadow-md shadow-amber-600/20 transition-all hover:scale-102 active:scale-98 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer shrink-0"
            >
              <svg v-if="!isExportingChat" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              <svg v-else class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
              </svg>
              <span>{{ isExportingChat ? 'Compilando...' : labels.exportChatAction }}</span>
            </button>
          </div>
        </div>

        <!-- Section 2: Official Business Documents -->
        <div>
          <div class="mb-3">
            <h3 class="font-bold text-sm flex items-center gap-2">
              <svg class="w-4 h-4 text-emerald-600 dark:text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
              </svg>
              {{ labels.exportDocsTitle }}
            </h3>
            <p class="text-xs text-stone-500 dark:text-stone-400">
              {{ labels.exportDocsDesc }}
            </p>
          </div>

          <div class="grid grid-cols-1 gap-2.5">
            <div
              v-for="doc in officialDocs"
              :key="doc.id"
              class="p-3.5 rounded-xl border flex items-center justify-between gap-3 transition-colors"
              :class="isDark ? 'bg-stone-800/20 border-stone-800 hover:bg-stone-800/40' : 'bg-stone-50/50 border-stone-200 hover:bg-stone-100/60'"
            >
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center justify-center font-bold text-[10px]">
                  PDF
                </div>
                <div>
                  <h4 class="font-semibold text-xs text-stone-800 dark:text-stone-200">
                    {{ doc.title }}
                  </h4>
                  <p class="text-[10px] text-stone-400 font-mono">
                    {{ doc.filename }} • ~{{ doc.size_kb }} KB
                  </p>
                </div>
              </div>

              <button
                type="button"
                @click="handleDownloadDoc(doc.filename)"
                :disabled="downloadingDocId === doc.filename"
                class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all hover:scale-102 active:scale-98 cursor-pointer"
                :class="
                  isDark
                    ? 'bg-stone-800 border-stone-700 text-stone-200 hover:bg-stone-700'
                    : 'bg-white border-stone-300 text-stone-700 hover:bg-stone-100'
                "
              >
                <svg v-if="downloadingDocId !== doc.filename" class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                <svg v-else class="w-3.5 h-3.5 animate-spin text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                  <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
                </svg>
                <span>{{ downloadingDocId === doc.filename ? 'Descargando...' : 'Descargar' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div
        class="px-6 py-4 border-t flex justify-end"
        :class="isDark ? 'border-stone-800 bg-stone-900/60' : 'border-stone-100 bg-stone-50/60'"
      >
        <button
          type="button"
          @click="emit('close')"
          class="px-4 py-2 rounded-xl text-xs font-semibold border transition-colors cursor-pointer"
          :class="isDark ? 'border-stone-700 bg-stone-800 text-stone-300 hover:bg-stone-700' : 'border-stone-300 bg-white text-stone-700 hover:bg-stone-100'"
        >
          {{ labels.closeBtn }}
        </button>
      </div>
    </div>
  </div>
</template>
