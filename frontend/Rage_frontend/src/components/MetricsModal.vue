<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Swal from 'sweetalert2'
import type { MetricsSummary } from '../types/chat'
import { fetchMetrics, resetMetrics } from '../services/api'

const props = defineProps<{
  isDark: boolean
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
}>()

const metrics = ref<MetricsSummary | null>(null)
const loading = ref(true)
const resetting = ref(false)

async function loadMetrics() {
  loading.value = true
  try {
    metrics.value = await fetchMetrics()
  } catch (err) {
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
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md transition-opacity">
    <div
      class="w-full max-w-2xl rounded-3xl p-6 sm:p-7 backdrop-blur-2xl border shadow-2xl transition-all duration-300 transform scale-100 relative overflow-hidden"
      :class="isDark ? 'bg-stone-900/95 border-stone-800 text-stone-100' : 'bg-white border-stone-300 text-stone-950 shadow-2xl'"
    >
      <!-- Modal Header -->
      <div
        class="flex items-center justify-between gap-3 mb-6 pb-4 border-b"
        :class="isDark ? 'border-stone-800' : 'border-stone-300'"
      >
        <div class="flex items-center gap-3">
          <div class="p-2.5 rounded-2xl bg-amber-500/10 text-amber-700 dark:text-amber-400">
            <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10"/>
              <line x1="12" y1="20" x2="12" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="14"/>
            </svg>
          </div>
          <div>
            <h3 class="font-black text-lg tracking-tight text-stone-950 dark:text-stone-100">{{ labels.metricsTitle }}</h3>
            <p class="text-xs text-stone-900 font-medium dark:text-stone-400">
              {{ labels.metricsSubtitle }}
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="emit('close')"
          class="p-2 rounded-xl text-stone-600 hover:text-stone-950 dark:text-stone-400 dark:hover:text-stone-200 transition-colors cursor-pointer"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-12 text-center text-sm text-stone-900 font-bold">
        <div class="animate-spin w-8 h-8 mx-auto mb-2 border-2 border-amber-600 border-t-transparent rounded-full"></div>
        {{ labels.loadingMetrics }}
      </div>

      <!-- Metrics Grid -->
      <div v-else-if="metrics" class="space-y-4">
        <!-- Top Stats Row -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <!-- Total Queries -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-300'"
          >
            <span class="text-xs font-bold text-stone-950 dark:text-stone-300 block mb-1">{{ labels.totalQueries }}</span>
            <span class="text-2xl font-black text-amber-700 dark:text-amber-400">{{ metrics.total_queries }}</span>
          </div>

          <!-- AI Resolved -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-300'"
          >
            <span class="text-xs font-bold text-stone-950 dark:text-stone-300 block mb-1">{{ labels.resolvedByAI }}</span>
            <span class="text-2xl font-black text-emerald-700 dark:text-emerald-400">{{ metrics.resolved_by_ai_queries }}</span>
          </div>

          <!-- Escalation Rate -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-300'"
          >
            <span class="text-xs font-bold text-stone-950 dark:text-stone-300 block mb-1">{{ labels.humanEscalation }}</span>
            <div class="flex items-baseline gap-1">
              <span class="text-2xl font-black text-rose-700 dark:text-rose-400">{{ metrics.escalated_queries }}</span>
              <span class="text-xs font-bold text-stone-900 dark:text-stone-400">({{ metrics.escalation_rate_pct }}%)</span>
            </div>
          </div>

          <!-- Cache Hits -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-300'"
          >
            <span class="text-xs font-bold text-stone-950 dark:text-stone-300 block mb-1">{{ labels.cacheHits }}</span>
            <div class="flex items-baseline gap-1">
              <span class="text-2xl font-black text-amber-700 dark:text-amber-400">{{ metrics.performance.cache.hits }}</span>
              <span class="text-xs font-bold text-stone-900 dark:text-stone-400">({{ metrics.performance.cache.hit_rate_pct }}%)</span>
            </div>
          </div>
        </div>

        <!-- Token & Cost Section -->
        <div class="p-4 sm:p-5 rounded-2xl border backdrop-blur-md"
          :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-300'"
        >
          <h4 class="text-xs font-black uppercase tracking-wider text-stone-950 dark:text-stone-300 mb-3">
            {{ labels.tokenSectionTitle }}
          </h4>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <span class="text-stone-900 font-bold block">{{ labels.totalTokens }}</span>
              <span class="font-black text-black dark:text-stone-100 text-sm">
                {{ metrics.tokens.total_tokens.toLocaleString() }}
              </span>
            </div>
            <div>
              <span class="text-stone-900 font-bold block">{{ labels.savedTokens }}</span>
              <span class="font-black text-emerald-700 dark:text-emerald-400 text-sm">
                {{ metrics.tokens.tokens_saved_by_cache.toLocaleString() }}
              </span>
            </div>
            <div>
              <span class="text-stone-900 font-bold block">{{ labels.localCost }}</span>
              <span class="font-black text-black dark:text-stone-100 text-sm">
                {{ labels.freeLocal }}
              </span>
            </div>
          </div>
        </div>

        <!-- Performance / Latency Section -->
        <div class="p-4 rounded-2xl border backdrop-blur-md flex items-center justify-between text-xs"
          :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-300'"
        >
          <div>
            <span class="text-stone-900 font-bold block">{{ labels.avgLatency }}</span>
            <span class="font-black text-sm text-black dark:text-stone-100">{{ metrics.performance.avg_latency_ms }} ms</span>
          </div>
          <div>
            <span class="text-stone-900 font-bold block">{{ labels.cacheSize }}</span>
            <span class="font-black text-sm text-black dark:text-stone-100">{{ metrics.performance.cache.cache_size }} / {{ metrics.performance.cache.max_size }}</span>
          </div>
          <div>
            <span class="text-stone-900 font-bold block">{{ labels.uptime }}</span>
            <span class="font-black text-sm text-black dark:text-stone-100">{{ Math.floor(metrics.performance.uptime_seconds / 60) }} min</span>
          </div>
        </div>
      </div>

      <!-- Modal Footer Actions -->
      <div
        class="mt-6 pt-4 border-t flex items-center justify-between gap-3"
        :class="isDark ? 'border-stone-800' : 'border-stone-300'"
      >
        <button
          type="button"
          @click="promptReset"
          :disabled="resetting"
          class="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold text-rose-700 hover:bg-rose-100 dark:hover:bg-rose-950/40 border border-rose-300 dark:border-rose-900/60 transition-all hover:scale-102 active:scale-98 cursor-pointer"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
          <span>{{ resetting ? labels.resettingBtn : labels.resetMetricsBtn }}</span>
        </button>

        <button
          type="button"
          @click="emit('close')"
          class="px-5 py-2 rounded-xl text-xs font-bold bg-stone-950 hover:bg-stone-800 text-white dark:bg-amber-600 dark:hover:bg-amber-500 transition-colors shadow-sm cursor-pointer"
        >
          {{ labels.closeBtn }}
        </button>
      </div>
    </div>
  </div>
</template>
