<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Swal from 'sweetalert2'
import type { MetricsSummary } from '../types/chat'
import { fetchMetrics, resetMetrics } from '../services/api'

const props = defineProps<{
  isDark: boolean
  currentUser?: any | null
  labels: {
    metricsTitle: string
    metricsSubtitle: string
    loadingMetrics: string
    totalQueries: string
    resolvedByAI: string
    humanEscalation: string
    cacheHits: string
    tokenSectionTitle: string
    totalTokens: string
    savedTokens: string
    localCost: string
    freeLocal: string
    avgLatency: string
    cacheSize: string
    uptime: string
    resetMetricsBtn: string
    resettingBtn: string
    resetConfirm: string
    closeBtn: string
    sweetAlertWarningTitle: string
    sweetAlertWarningText: string
    sweetAlertConfirmBtn: string
    sweetAlertCancelBtn: string
    sweetAlertSuccessTitle: string
    sweetAlertSuccessText: string
    sweetAlertOkBtn: string
  }
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'metricsReset'): void
  (e: 'logout'): void
  (e: 'unauthorized'): void
}>()

const metrics = ref<MetricsSummary | null>(null)
const loading = ref(true)
const resetting = ref(false)

async function loadMetrics() {
  loading.value = true
  try {
    metrics.value = await fetchMetrics()
  } catch (err: any) {
    if (err.message === '401_UNAUTHORIZED') {
      emit('unauthorized')
      emit('close')
      return
    }
    console.error('Failed to load metrics', err)
  } finally {
    loading.value = false
  }
}

async function promptReset() {
  const result = await Swal.fire({
    title: props.labels.sweetAlertWarningTitle,
    text: props.labels.sweetAlertWarningText,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#e11d48',
    cancelButtonColor: props.isDark ? '#44403c' : '#78716c',
    confirmButtonText: props.labels.sweetAlertConfirmBtn,
    cancelButtonText: props.labels.sweetAlertCancelBtn,
    background: props.isDark ? '#1c1917' : '#ffffff',
    color: props.isDark ? '#f5f5f4' : '#1c1917',
    iconColor: '#f59e0b'
  })

  if (result.isConfirmed) {
    resetting.value = true
    try {
      await resetMetrics()
      await loadMetrics()
      emit('metricsReset')

      await Swal.fire({
        title: props.labels.sweetAlertSuccessTitle,
        text: props.labels.sweetAlertSuccessText,
        icon: 'success',
        confirmButtonColor: '#10b981',
        confirmButtonText: props.labels.sweetAlertOkBtn,
        background: props.isDark ? '#1c1917' : '#ffffff',
        color: props.isDark ? '#f5f5f4' : '#1c1917',
        iconColor: '#10b981'
      })
    } catch (err) {
      console.error('Failed to reset metrics', err)
    } finally {
      resetting.value = false
    }
  }
}

onMounted(() => {
  loadMetrics()
})
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-950/70 backdrop-blur-xs transition-opacity">
    <div
      class="w-full max-w-2xl border-2 p-6 sm:p-7 transition-all duration-200 relative overflow-hidden"
      :class="isDark ? 'bg-stone-950 border-stone-700 text-stone-100 shadow-[8px_8px_0px_0px_#d97706]' : 'bg-white border-stone-900 text-stone-950 shadow-[8px_8px_0px_0px_#1c1917]'"
    >
      <!-- Corner Marks -->
      <div class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-amber-600 pointer-events-none"></div>
      <div class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-amber-600 pointer-events-none"></div>

      <!-- Modal Header -->
      <div
        class="flex items-center justify-between gap-3 mb-5 pb-3 border-b-2"
        :class="isDark ? 'border-stone-800' : 'border-stone-900'"
      >
        <div class="flex items-center gap-3">
          <div class="p-2 border-2 border-stone-900 dark:border-amber-500 bg-amber-500/10 text-amber-700 dark:text-amber-400">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="20" x2="18" y2="10"/>
              <line x1="12" y1="20" x2="12" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="14"/>
            </svg>
          </div>
          <div>
            <h3 class="font-black text-base tracking-tight uppercase text-stone-950 dark:text-stone-100 font-mono">// {{ labels.metricsTitle.toUpperCase() }}</h3>
            <p class="font-mono text-[11px] text-stone-600 dark:text-stone-400">
              {{ labels.metricsSubtitle }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <div
            v-if="currentUser"
            class="hidden sm:flex items-center gap-2 px-2.5 py-1 border border-stone-900 dark:border-stone-700 font-mono text-[11px] font-black"
            :class="isDark ? 'bg-stone-900 text-stone-300' : 'bg-stone-100 text-stone-900'"
          >
            <span>[USR] {{ currentUser.full_name || currentUser.username }}</span>
            <button
              type="button"
              @click="emit('logout')"
              class="text-[10px] font-black text-rose-600 dark:text-rose-400 hover:underline cursor-pointer ml-1 uppercase"
              title="Cerrar sesión"
            >
              Salir
            </button>
          </div>

          <button
            type="button"
            @click="emit('close')"
            class="p-1.5 border-2 border-stone-900 dark:border-stone-700 text-stone-600 hover:text-stone-950 dark:text-stone-400 dark:hover:text-stone-200 transition-colors cursor-pointer"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="18" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-12 text-center text-sm font-mono font-black text-stone-900 dark:text-stone-300">
        <div class="animate-spin w-8 h-8 mx-auto mb-2 border-2 border-amber-600 border-t-transparent"></div>
        {{ labels.loadingMetrics }}
      </div>

      <!-- Metrics Grid -->
      <div v-else-if="metrics" class="space-y-3 font-mono">
        <!-- Top Stats Row -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <!-- Total Queries -->
          <div
            class="p-3 border-2 border-stone-900 dark:border-stone-700 relative shadow-[2px_2px_0px_0px_#1c1917] dark:shadow-[2px_2px_0px_0px_#000]"
            :class="isDark ? 'bg-stone-900' : 'bg-stone-50'"
          >
            <div class="text-[10px] uppercase font-black tracking-wider text-stone-500 dark:text-stone-400">// CONSULTAS</div>
            <div class="text-xl font-black text-stone-950 dark:text-stone-100 mt-0.5">{{ metrics.total_queries }}</div>
            <div class="text-[10px] text-stone-500 mt-1 font-bold">{{ labels.totalQueries }}</div>
          </div>

          <!-- Resolved by AI -->
          <div
            class="p-3 border-2 border-stone-900 dark:border-stone-700 relative shadow-[2px_2px_0px_0px_#059669]"
            :class="isDark ? 'bg-stone-900' : 'bg-stone-50'"
          >
            <div class="text-[10px] uppercase font-black tracking-wider text-emerald-700 dark:text-emerald-400">// RESUELTAS IA</div>
            <div class="text-xl font-black text-emerald-700 dark:text-emerald-400 mt-0.5">{{ metrics.resolved_by_ai_queries }}</div>
            <div class="text-[10px] text-stone-500 mt-1 font-bold">{{ labels.resolvedByAI }}</div>
          </div>

          <!-- Human Escalations -->
          <div
            class="p-3 border-2 border-stone-900 dark:border-stone-700 relative shadow-[2px_2px_0px_0px_#e11d48]"
            :class="isDark ? 'bg-stone-900' : 'bg-stone-50'"
          >
            <div class="text-[10px] uppercase font-black tracking-wider text-rose-700 dark:text-rose-400">// ESCALAMIENTOS</div>
            <div class="text-xl font-black text-rose-700 dark:text-rose-400 mt-0.5">{{ metrics.escalated_queries }}</div>
            <div class="text-[10px] text-stone-500 mt-1 font-bold">{{ labels.humanEscalation }}</div>
          </div>

          <!-- Cache Hits -->
          <div
            class="p-3 border-2 border-stone-900 dark:border-stone-700 relative shadow-[2px_2px_0px_0px_#d97706]"
            :class="isDark ? 'bg-stone-900' : 'bg-stone-50'"
          >
            <div class="text-[10px] uppercase font-black tracking-wider text-amber-700 dark:text-amber-400">// CACHÉ HITS</div>
            <div class="text-xl font-black text-amber-700 dark:text-amber-400 mt-0.5">{{ metrics.performance?.cache?.hits || 0 }}</div>
            <div class="text-[10px] text-stone-500 mt-1 font-bold">{{ labels.cacheHits }}</div>
          </div>
        </div>

        <!-- Token Usage & Economics Section -->
        <div
          class="p-4 border-2 border-stone-900 dark:border-stone-700 space-y-3 shadow-[3px_3px_0px_0px_#1c1917] dark:shadow-[3px_3px_0px_0px_#000]"
          :class="isDark ? 'bg-stone-900/60' : 'bg-stone-50'"
        >
          <div class="flex items-center justify-between border-b border-stone-300 dark:border-stone-800 pb-2">
            <span class="text-xs font-black uppercase text-amber-700 dark:text-amber-400">// {{ labels.tokenSectionTitle.toUpperCase() }}</span>
            <span class="text-[10px] text-stone-500 uppercase">[ECONOMICS]</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div class="p-2 border border-stone-300 dark:border-stone-800 bg-white dark:bg-stone-900">
              <span class="text-[10px] text-stone-500 block uppercase">{{ labels.totalTokens }}</span>
              <span class="text-sm font-black text-stone-950 dark:text-stone-100">{{ metrics.tokens?.total_tokens || 0 }}</span>
            </div>
            <div class="p-2 border border-stone-300 dark:border-stone-800 bg-white dark:bg-stone-900">
              <span class="text-[10px] text-emerald-700 dark:text-emerald-400 block uppercase">{{ labels.savedTokens }}</span>
              <span class="text-sm font-black text-emerald-700 dark:text-emerald-400">{{ metrics.tokens?.tokens_saved_by_cache || 0 }}</span>
            </div>
            <div class="p-2 border border-stone-300 dark:border-stone-800 bg-white dark:bg-stone-900">
              <span class="text-[10px] text-amber-700 dark:text-amber-400 block uppercase">{{ labels.localCost }}</span>
              <span class="text-sm font-black text-amber-700 dark:text-amber-400">{{ labels.freeLocal }}</span>
            </div>
          </div>
        </div>

        <!-- Performance / Latency / System Info -->
        <div class="grid grid-cols-3 gap-3 text-[11px]">
          <div class="p-2.5 border-2 border-stone-900 dark:border-stone-800 bg-white dark:bg-stone-900">
            <span class="text-[9px] text-stone-500 uppercase block">// {{ labels.avgLatency }}</span>
            <span class="font-black text-stone-950 dark:text-stone-100">{{ (metrics.performance?.avg_latency_ms || 0).toFixed(0) }}ms</span>
          </div>
          <div class="p-2.5 border-2 border-stone-900 dark:border-stone-800 bg-white dark:bg-stone-900">
            <span class="text-[9px] text-stone-500 uppercase block">// {{ labels.cacheSize }}</span>
            <span class="font-black text-stone-950 dark:text-stone-100">{{ metrics.performance?.cache?.cache_size || 0 }} items</span>
          </div>
          <div class="p-2.5 border-2 border-stone-900 dark:border-stone-800 bg-white dark:bg-stone-900">
            <span class="text-[9px] text-stone-500 uppercase block">// {{ labels.uptime }}</span>
            <span class="font-black text-stone-950 dark:text-stone-100">{{ (metrics.performance?.uptime_seconds || 0).toFixed(0) }}s</span>
          </div>
        </div>

        <!-- Actions Bar -->
        <div class="pt-3 border-t-2 border-stone-200 dark:border-stone-800 flex items-center justify-between gap-3">
          <button
            type="button"
            @click="promptReset"
            :disabled="resetting"
            class="px-3.5 py-2 border-2 border-rose-600 bg-rose-50 text-rose-950 dark:bg-rose-950/40 dark:text-rose-200 text-xs font-black uppercase transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 disabled:opacity-50 cursor-pointer shadow-[2px_2px_0px_0px_#be123c]"
          >
            {{ resetting ? labels.resettingBtn : labels.resetMetricsBtn }}
          </button>

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
  </div>
</template>
