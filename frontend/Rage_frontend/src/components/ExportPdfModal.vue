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
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-950/70 backdrop-blur-xs transition-opacity duration-200"
    @click.self="emit('close')"
  >
    <div
      class="w-full max-w-2xl border-2 overflow-hidden flex flex-col max-h-[90vh] transition-all transform scale-100 relative"
      :class="isDark ? 'bg-stone-900 border-amber-600/60 text-stone-100 shadow-[8px_8px_0px_0px_#d97706]' : 'bg-stone-50 border-stone-900 text-stone-950 shadow-[8px_8px_0px_0px_#1c1917]'"
    >
      <!-- Corner ticks -->
      <span class="absolute top-1 left-1 font-mono text-[9px] text-stone-400 select-none pointer-events-none">+</span>
      <span class="absolute top-1 right-1 font-mono text-[9px] text-stone-400 select-none pointer-events-none">+</span>
      <span class="absolute bottom-1 left-1 font-mono text-[9px] text-stone-400 select-none pointer-events-none">+</span>
      <span class="absolute bottom-1 right-1 font-mono text-[9px] text-stone-400 select-none pointer-events-none">+</span>

      <!-- Header -->
      <div
        class="px-6 py-4 border-b-2 flex items-center justify-between"
        :class="isDark ? 'border-amber-600/40 bg-stone-900' : 'border-stone-900 bg-stone-100'"
      >
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 border-2 flex items-center justify-center font-mono font-black text-xs"
               :class="isDark ? 'border-amber-500 bg-amber-500/10 text-amber-400' : 'border-stone-900 bg-amber-500 text-stone-950'">
            EXP
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-mono text-[10px] tracking-widest uppercase font-bold text-amber-700 dark:text-amber-400">
                [DOC // DISPATCH]
              </span>
            </div>
            <h2 class="text-sm sm:text-base font-black uppercase tracking-tight text-stone-950 dark:text-stone-100">
              {{ labels.exportModalTitle }} (PDF / MD / TXT)
            </h2>
          </div>
        </div>

        <button
          type="button"
          @click="emit('close')"
          class="w-8 h-8 border-2 flex items-center justify-center font-mono font-bold transition-all cursor-pointer"
          :class="isDark ? 'border-stone-700 text-stone-300 hover:bg-stone-800 hover:border-stone-500' : 'border-stone-900 text-stone-900 hover:bg-stone-200'"
        >
          ✕
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 overflow-y-auto space-y-5">
        <!-- Success Alert -->
        <div
          v-if="alertSuccessMsg"
          class="p-3.5 border-2 flex items-start gap-3 bg-emerald-500/10 border-emerald-600 text-emerald-950 dark:text-emerald-300 font-mono text-xs shadow-[3px_3px_0px_0px_#059669]"
        >
          <span class="px-1.5 py-0.5 bg-emerald-600 text-white font-bold text-[10px] uppercase">OK</span>
          <div class="flex-1">
            <h4 class="font-black uppercase tracking-wide">
              {{ labels.exportSuccessAlertTitle }}
            </h4>
            <p class="text-[11px] mt-0.5 font-medium">
              {{ labels.exportSuccessAlertText }} (<b>{{ alertSuccessMsg }}</b>)
            </p>
          </div>
        </div>

        <!-- Section 1: Export Current Conversation -->
        <div
          class="p-4 border-2 transition-all"
          :class="isDark ? 'bg-stone-900/60 border-stone-800 shadow-[4px_4px_0px_0px_#292524]' : 'bg-white border-stone-900 shadow-[4px_4px_0px_0px_#d97706]'"
        >
          <div class="flex flex-col gap-3">
            <div>
              <div class="flex items-center gap-2">
                <span class="px-1.5 py-0.5 font-mono text-[9px] font-black uppercase tracking-wider bg-amber-500 text-stone-950 border border-stone-900">
                  SESIÓN VIVA
                </span>
                <h3 class="font-black text-xs uppercase tracking-wide text-stone-950 dark:text-stone-100">
                  {{ labels.exportChatTitle }}
                </h3>
              </div>
              <p class="text-xs text-stone-700 dark:text-stone-300 font-sans mt-1">
                {{ labels.exportChatDesc }}
              </p>
              <div class="flex items-center gap-3 mt-2 font-mono text-[11px] text-stone-600 dark:text-stone-400">
                <span>// {{ messages.length }} MENSAJES REGISTRADOS</span>
                <span>•</span>
                <span>PDF | MD | TXT</span>
              </div>
            </div>

            <!-- Export Buttons Row -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-3 border-t-2 border-stone-200 dark:border-stone-800">
              <!-- Export PDF Button -->
              <button
                type="button"
                @click="handleExportPdf"
                :disabled="isExportingPdf || messages.length === 0"
                class="flex items-center justify-center gap-2 px-3 py-2.5 border-2 text-xs font-mono font-bold uppercase transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                :class="isDark 
                  ? 'border-rose-500 bg-rose-600 text-white hover:bg-rose-500 shadow-[3px_3px_0px_0px_#e11d48]' 
                  : 'border-stone-900 bg-rose-600 text-white hover:bg-rose-700 shadow-[3px_3px_0px_0px_#1c1917] active:shadow-[1px_1px_0px_0px_#1c1917]'"
              >
                <span v-if="!isExportingPdf">■ EXPORTAR PDF</span>
                <span v-else class="animate-pulse">GENERANDO...</span>
              </button>

              <!-- Export Markdown Button -->
              <button
                type="button"
                @click="handleExportMd"
                :disabled="isExportingMd || messages.length === 0"
                class="flex items-center justify-center gap-2 px-3 py-2.5 border-2 text-xs font-mono font-bold uppercase transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                :class="isDark 
                  ? 'border-amber-500 bg-amber-600 text-white hover:bg-amber-500 shadow-[3px_3px_0px_0px_#d97706]' 
                  : 'border-stone-900 bg-amber-500 text-stone-950 hover:bg-amber-400 shadow-[3px_3px_0px_0px_#1c1917] active:shadow-[1px_1px_0px_0px_#1c1917]'"
              >
                <span v-if="!isExportingMd">▲ EXPORTAR MD</span>
                <span v-else class="animate-pulse">GENERANDO...</span>
              </button>

              <!-- Export TXT Button -->
              <button
                type="button"
                @click="handleExportTxt"
                :disabled="isExportingTxt || messages.length === 0"
                class="flex items-center justify-center gap-2 px-3 py-2.5 border-2 text-xs font-mono font-bold uppercase transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                :class="isDark 
                  ? 'border-stone-600 bg-stone-800 text-stone-100 hover:bg-stone-700 shadow-[3px_3px_0px_0px_#57534e]' 
                  : 'border-stone-900 bg-stone-900 text-white hover:bg-stone-800 shadow-[3px_3px_0px_0px_#d97706] active:shadow-[1px_1px_0px_0px_#d97706]'"
              >
                <span v-if="!isExportingTxt">● EXPORTAR TXT</span>
                <span v-else class="animate-pulse">GENERANDO...</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Section 2: Official Business Documents -->
        <div>
          <div class="mb-3 flex items-center justify-between">
            <h3 class="font-black text-xs uppercase tracking-wider font-mono flex items-center gap-2 text-stone-950 dark:text-stone-100">
              <span class="w-2.5 h-2.5 bg-emerald-600 inline-block"></span>
              {{ labels.exportDocsTitle }}
            </h3>
            <span class="font-mono text-[10px] text-stone-500 dark:text-stone-400 uppercase">[CANONICAL DOCS]</span>
          </div>

          <div class="grid grid-cols-1 gap-2">
            <div
              v-for="doc in officialDocs"
              :key="doc.id"
              class="p-3 border-2 flex items-center justify-between gap-3 transition-all"
              :class="isDark ? 'bg-stone-900 border-stone-800 hover:border-amber-500/50 shadow-[2px_2px_0px_0px_#292524]' : 'bg-white border-stone-900 hover:border-amber-600 shadow-[2px_2px_0px_0px_#e7e5e4]'"
            >
              <div class="flex items-center gap-3">
                <div class="w-7 h-7 border-2 border-stone-900 dark:border-stone-700 bg-stone-100 dark:bg-stone-800 flex items-center justify-center font-mono font-black text-[10px]">
                  #
                </div>
                <div>
                  <h4 class="font-bold text-xs uppercase text-stone-950 dark:text-stone-100">
                    {{ doc.title }}
                  </h4>
                  <p class="text-[10px] text-stone-600 dark:text-stone-400 font-mono">
                    {{ doc.filename }} // ~{{ doc.size_kb }} KB
                  </p>
                </div>
              </div>

              <!-- Download options -->
              <div class="flex items-center gap-1.5">
                <!-- PDF Download -->
                <button
                  type="button"
                  @click="handleDownloadDoc(doc.filename)"
                  :disabled="downloadingDocId === doc.filename"
                  title="Descargar PDF"
                  class="px-2.5 py-1 border-2 font-mono text-[11px] font-bold uppercase transition-all cursor-pointer"
                  :class="
                    isDark
                      ? 'border-stone-700 bg-stone-800 text-stone-200 hover:border-rose-500'
                      : 'border-stone-900 bg-white text-stone-950 hover:bg-stone-100 shadow-[2px_2px_0px_0px_#1c1917]'
                  "
                >
                  <span class="text-rose-600 dark:text-rose-400 font-black">PDF</span>
                  <span class="ml-1">{{ downloadingDocId === doc.filename ? '...' : '↓' }}</span>
                </button>

                <!-- Markdown Download (if available) -->
                <button
                  v-if="doc.md_filename"
                  type="button"
                  @click="handleDownloadDoc(doc.md_filename)"
                  :disabled="downloadingDocId === doc.md_filename"
                  title="Descargar Markdown (.md)"
                  class="px-2.5 py-1 border-2 font-mono text-[11px] font-bold uppercase transition-all cursor-pointer"
                  :class="
                    isDark
                      ? 'border-stone-700 bg-stone-800 text-stone-200 hover:border-amber-500'
                      : 'border-stone-900 bg-white text-stone-950 hover:bg-stone-100 shadow-[2px_2px_0px_0px_#1c1917]'
                  "
                >
                  <span class="text-amber-600 dark:text-amber-400 font-black">MD</span>
                  <span class="ml-1">{{ downloadingDocId === doc.md_filename ? '...' : '↓' }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div
        class="px-6 py-3 border-t-2 flex justify-end"
        :class="isDark ? 'border-amber-600/40 bg-stone-900' : 'border-stone-900 bg-stone-100'"
      >
        <button
          type="button"
          @click="emit('close')"
          class="px-4 py-1.5 border-2 font-mono text-xs font-black uppercase transition-all cursor-pointer"
          :class="isDark ? 'border-stone-700 bg-stone-800 text-stone-300 hover:border-stone-500' : 'border-stone-900 bg-white text-stone-950 hover:bg-stone-100 shadow-[2px_2px_0px_0px_#1c1917]'"
        >
          [CERRAR]
        </button>
      </div>
    </div>
  </div>
</template>
