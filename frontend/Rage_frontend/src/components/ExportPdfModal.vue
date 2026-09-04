<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Swal from 'sweetalert2'
import {
  exportChatPdf,
  exportChatMd,
  exportChatTxt,
  fetchOfficialDocuments,
  downloadOfficialDocFile
} from '../services/api'
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

const isExportingPdf = ref(false)
const isExportingMd = ref(false)
const isExportingTxt = ref(false)
const downloadingDocId = ref<string | null>(null)
const alertSuccessMsg = ref<string | null>(null)
const officialDocs = ref<Array<{ id: string; title: string; filename: string; md_filename?: string; size_kb: number }>>([])

function notifySuccess(title: string, text: string) {
  Swal.fire({
    toast: true,
    position: 'top-end',
    icon: 'success',
    title: title,
    text: text,
    showConfirmButton: false,
    timer: 3500,
    timerProgressBar: true,
    background: props.isDark ? '#1c1917' : '#ffffff',
    color: props.isDark ? '#f5f5f4' : '#1c1917',
    iconColor: '#10b981'
  })
}

function notifyError(title: string, text: string) {
  Swal.fire({
    toast: true,
    position: 'top-end',
    icon: 'error',
    title: title,
    text: text,
    showConfirmButton: false,
    timer: 4000,
    timerProgressBar: true,
    background: props.isDark ? '#1c1917' : '#ffffff',
    color: props.isDark ? '#f5f5f4' : '#1c1917'
  })
}

onMounted(async () => {
  try {
    officialDocs.value = await fetchOfficialDocuments()
  } catch {
    officialDocs.value = [
      { id: '01_courses_modalities_levels', title: 'Cursos, Modalidades y Niveles', filename: '01_courses_modalities_levels.pdf', md_filename: '01_courses_modalities_levels.md', size_kb: 9.7 },
      { id: '02_pricing_schedules_promotions', title: 'Tarifas, Horarios y Promociones', filename: '02_pricing_schedules_promotions.pdf', md_filename: '02_pricing_schedules_promotions.md', size_kb: 9.3 },
      { id: '03_enrollments_certifications_policies', title: 'Inscripciones, Certificaciones y Políticas', filename: '03_enrollments_certifications_policies.pdf', md_filename: '03_enrollments_certifications_policies.md', size_kb: 11.0 }
    ]
  }
})

const handleExportPdf = async () => {
  if (isExportingPdf.value || props.messages.length === 0) return
  isExportingPdf.value = true
  alertSuccessMsg.value = null

  try {
    const filename = `gastroteacher_chat_${props.sessionId}.pdf`
    const blob = await exportChatPdf(props.messages, props.sessionId)
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

    alertSuccessMsg.value = filename
    notifySuccess('¡PDF Exportado!', `Descarga completada: ${filename}`)
  } catch (err: any) {
    console.error('PDF Export error:', err)
    notifyError('Error de exportación', err.message || 'No se pudo generar el archivo PDF.')
  } finally {
    isExportingPdf.value = false
  }
}

const handleExportMd = async () => {
  if (isExportingMd.value || props.messages.length === 0) return
  isExportingMd.value = true
  alertSuccessMsg.value = null

  try {
    const filename = `gastroteacher_chat_${props.sessionId}.md`
    const blob = await exportChatMd(props.messages, props.sessionId)
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

    alertSuccessMsg.value = filename
    notifySuccess('¡Markdown Exportado!', `Descarga completada: ${filename}`)
  } catch (err: any) {
    console.error('Markdown Export error:', err)
    notifyError('Error de exportación', err.message || 'No se pudo generar el archivo Markdown.')
  } finally {
    isExportingMd.value = false
  }
}

const handleExportTxt = async () => {
  if (isExportingTxt.value || props.messages.length === 0) return
  isExportingTxt.value = true
  alertSuccessMsg.value = null

  try {
    const filename = `gastroteacher_chat_${props.sessionId}.txt`
    const blob = await exportChatTxt(props.messages, props.sessionId)
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

    alertSuccessMsg.value = filename
    notifySuccess('¡Texto TXT Exportado!', `Descarga completada: ${filename}`)
  } catch (err: any) {
    console.error('TXT Export error:', err)
    notifyError('Error de exportación', err.message || 'No se pudo generar el archivo de texto.')
  } finally {
    isExportingTxt.value = false
  }
}

const handleDownloadDoc = async (filename: string) => {
  if (downloadingDocId.value) return
  downloadingDocId.value = filename
  alertSuccessMsg.value = null

  try {
    const blob = await downloadOfficialDocFile(filename)
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

    alertSuccessMsg.value = filename
    notifySuccess('Documento Oficial Descargado', `Archivo: ${filename}`)
  } catch (err: any) {
    console.error('Download error:', err)
    notifyError('Error de descarga', err.message || 'No se pudo descargar el documento.')
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
      :class="isDark ? 'bg-stone-900 border-stone-800 text-stone-100' : 'bg-white border-stone-300 text-stone-950 shadow-2xl'"
    >
      <!-- Header -->
      <div
        class="px-6 py-5 border-b flex items-center justify-between"
        :class="isDark ? 'border-stone-800 bg-stone-900/90' : 'border-stone-200 bg-stone-50'"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-700 dark:text-amber-400">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <div>
            <h2 class="text-base sm:text-lg font-black tracking-tight text-stone-950 dark:text-stone-100">
              {{ labels.exportModalTitle }} (PDF / Markdown / TXT)
            </h2>
            <p class="text-xs text-stone-900 font-medium dark:text-stone-300">
              {{ labels.exportModalSubtitle }}
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="emit('close')"
          class="p-2 rounded-xl border transition-colors cursor-pointer hover:bg-stone-200 dark:hover:bg-stone-800"
          :class="isDark ? 'border-stone-700 text-stone-400' : 'border-stone-400 text-stone-900'"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto space-y-6">
        <!-- Success Alert -->
        <div
          v-if="alertSuccessMsg"
          class="p-4 rounded-2xl border flex items-start gap-3 bg-emerald-500/10 border-emerald-500/40 text-emerald-950 dark:text-emerald-300 animate-fade-in font-medium"
        >
          <div class="w-8 h-8 rounded-full bg-emerald-600 text-white flex items-center justify-center shrink-0 font-bold text-sm">
            ✓
          </div>
          <div class="flex-1">
            <h4 class="font-black text-sm text-emerald-950 dark:text-emerald-300">
              {{ labels.exportSuccessAlertTitle }} (SweetAlert2)
            </h4>
            <p class="text-xs mt-0.5 text-stone-950 dark:text-emerald-200 font-semibold">
              {{ labels.exportSuccessAlertText }} (<b>{{ alertSuccessMsg }}</b>)
            </p>
          </div>
        </div>

        <!-- Section 1: Export Current Conversation -->
        <div
          class="p-5 rounded-2xl border transition-all"
          :class="isDark ? 'bg-stone-800/40 border-stone-700/60' : 'bg-stone-50 border-stone-300'"
        >
          <div class="flex flex-col gap-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-black bg-amber-500/20 text-amber-900 dark:text-amber-300 border border-amber-500/40">
                  SESIÓN ACTIVA
                </span>
                <h3 class="font-black text-sm text-stone-950 dark:text-stone-100">
                  {{ labels.exportChatTitle }}
                </h3>
              </div>
              <p class="text-xs text-stone-950 font-medium dark:text-stone-300 mt-1">
                {{ labels.exportChatDesc }} Selecciona el formato de descarga deseado:
              </p>
              <div class="flex items-center gap-3 mt-2 text-[11px] font-bold text-stone-900 dark:text-stone-300">
                <span>💬 {{ messages.length }} mensajes en memoria</span>
                <span>•</span>
                <span>📋 Formatos: PDF, Markdown (.md), Texto (.txt)</span>
              </div>
            </div>

            <!-- Export Buttons Row -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-2 border-t border-stone-200 dark:border-stone-700">
              <!-- Export PDF Button -->
              <button
                type="button"
                @click="handleExportPdf"
                :disabled="isExportingPdf || messages.length === 0"
                class="flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-black bg-linear-to-r from-rose-600 to-rose-700 hover:from-rose-700 hover:to-rose-800 text-white shadow-md shadow-rose-600/20 transition-all hover:scale-102 active:scale-98 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                <svg v-if="!isExportingPdf" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
                <svg v-else class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                  <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
                </svg>
                <span>{{ isExportingPdf ? 'Generando...' : 'Exportar PDF' }}</span>
              </button>

              <!-- Export Markdown Button -->
              <button
                type="button"
                @click="handleExportMd"
                :disabled="isExportingMd || messages.length === 0"
                class="flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-black bg-linear-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 text-white shadow-md shadow-amber-600/20 transition-all hover:scale-102 active:scale-98 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                <svg v-if="!isExportingMd" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                  <polyline points="7 15 7 9 10 12 13 9 13 15"/>
                  <polyline points="17 12 19 14 17 16"/>
                </svg>
                <svg v-else class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                  <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
                </svg>
                <span>{{ isExportingMd ? 'Generando...' : 'Exportar Markdown (.md)' }}</span>
              </button>

              <!-- Export TXT Button -->
              <button
                type="button"
                @click="handleExportTxt"
                :disabled="isExportingTxt || messages.length === 0"
                class="flex items-center justify-center gap-2 px-3.5 py-2.5 rounded-xl text-xs font-black bg-linear-to-r from-stone-700 to-stone-800 hover:from-stone-800 hover:to-stone-900 text-white shadow-md shadow-stone-700/20 transition-all hover:scale-102 active:scale-98 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                <svg v-if="!isExportingTxt" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <line x1="16" y1="13" x2="8" y2="13"/>
                  <line x1="16" y1="17" x2="8" y2="17"/>
                  <polyline points="10 9 9 9 8 9"/>
                </svg>
                <svg v-else class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
                  <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
                </svg>
                <span>{{ isExportingTxt ? 'Generando...' : 'Exportar TXT' }}</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Section 2: Official Business Documents -->
        <div>
          <div class="mb-3">
            <h3 class="font-black text-sm flex items-center gap-2 text-stone-950 dark:text-stone-100">
              <svg class="w-4 h-4 text-emerald-600 dark:text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
              </svg>
              {{ labels.exportDocsTitle }}
            </h3>
            <p class="text-xs text-stone-950 font-medium dark:text-stone-300">
              {{ labels.exportDocsDesc }}
            </p>
          </div>

          <div class="grid grid-cols-1 gap-2.5">
            <div
              v-for="doc in officialDocs"
              :key="doc.id"
              class="p-3.5 rounded-xl border flex items-center justify-between gap-3 transition-colors"
              :class="isDark ? 'bg-stone-800/20 border-stone-800 hover:bg-stone-800/40' : 'bg-stone-50 border-stone-300 hover:bg-stone-100'"
            >
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg bg-rose-500/15 border border-rose-500/30 text-rose-700 dark:text-rose-400 flex items-center justify-center font-bold text-[10px]">
                  DOC
                </div>
                <div>
                  <h4 class="font-bold text-xs text-stone-950 dark:text-stone-100">
                    {{ doc.title }}
                  </h4>
                  <p class="text-[10px] text-stone-700 dark:text-stone-400 font-mono font-medium">
                    {{ doc.filename }} • ~{{ doc.size_kb }} KB
                  </p>
                </div>
              </div>

              <!-- Download options -->
              <div class="flex items-center gap-2">
                <!-- PDF Download -->
                <button
                  type="button"
                  @click="handleDownloadDoc(doc.filename)"
                  :disabled="downloadingDocId === doc.filename"
                  title="Descargar PDF"
                  class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all hover:scale-102 active:scale-98 cursor-pointer"
                  :class="
                    isDark
                      ? 'bg-stone-800 border-stone-700 text-stone-200 hover:bg-stone-700'
                      : 'bg-white border-stone-400 text-stone-950 hover:bg-stone-100'
                  "
                >
                  <span class="text-[10px] font-black text-rose-600 dark:text-rose-400">PDF</span>
                  <span>{{ downloadingDocId === doc.filename ? '...' : 'Descargar' }}</span>
                </button>

                <!-- Markdown Download (if available) -->
                <button
                  v-if="doc.md_filename"
                  type="button"
                  @click="handleDownloadDoc(doc.md_filename)"
                  :disabled="downloadingDocId === doc.md_filename"
                  title="Descargar Markdown (.md)"
                  class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all hover:scale-102 active:scale-98 cursor-pointer"
                  :class="
                    isDark
                      ? 'bg-stone-800 border-stone-700 text-stone-200 hover:bg-stone-700'
                      : 'bg-white border-stone-400 text-stone-950 hover:bg-stone-100'
                  "
                >
                  <span class="text-[10px] font-black text-amber-600 dark:text-amber-400">MD</span>
                  <span>{{ downloadingDocId === doc.md_filename ? '...' : 'Descargar' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div
        class="px-6 py-4 border-t flex justify-end"
        :class="isDark ? 'border-stone-800 bg-stone-900/60' : 'border-stone-200 bg-stone-50'"
      >
        <button
          type="button"
          @click="emit('close')"
          class="px-4 py-2 rounded-xl text-xs font-bold border transition-colors cursor-pointer"
          :class="isDark ? 'border-stone-700 bg-stone-800 text-stone-300 hover:bg-stone-700' : 'border-stone-400 bg-white text-stone-950 hover:bg-stone-100'"
        >
          {{ labels.closeBtn }}
        </button>
      </div>
    </div>
  </div>
</template>
