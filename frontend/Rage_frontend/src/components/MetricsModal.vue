<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { MetricsSummary } from '../types/chat'
import { fetchMetrics, resetMetrics } from '../services/api'

defineProps<{
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

// SweetAlert states
const showWarningAlert = ref(false)
const showSuccessAlert = ref(false)

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

function promptReset() {
  showWarningAlert.value = true
}

async function confirmReset() {
  showWarningAlert.value = false
  resetting.value = true
  try {
    await resetMetrics()
    await loadMetrics()
    showSuccessAlert.value = true
    emit('metricsReset')
  } catch (err) {
    console.error('Failed to reset metrics', err)
  } finally {
    resetting.value = false
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
      :class="isDark ? 'bg-stone-900/95 border-stone-800 text-stone-100' : 'bg-white/95 border-stone-200 text-stone-900'"
    >
      <!-- SweetAlert Warning Modal Overlay -->
      <div
        v-if="showWarningAlert"
        class="absolute inset-0 z-20 flex items-center justify-center p-6 bg-black/75 backdrop-blur-md animate-fade-in"
      >
        <div
          class="w-full max-w-md p-6 rounded-3xl border text-center shadow-2xl transition-all scale-100"
          :class="isDark ? 'bg-stone-900 border-amber-500/40 text-stone-100' : 'bg-white border-amber-400 text-stone-900'"
        >
          <!-- Warning Icon Badge -->
          <div class="w-14 h-14 mx-auto mb-4 rounded-full bg-amber-500/20 text-amber-500 flex items-center justify-center text-2xl font-black border border-amber-500/40 shadow-inner">
            !
          </div>

          <h3 class="text-base sm:text-lg font-bold mb-2">
            {{ labels.sweetAlertWarningTitle }}
          </h3>
          <p class="text-xs text-stone-500 dark:text-stone-400 mb-6 leading-relaxed">
            {{ labels.sweetAlertWarningText }}
          </p>

          <!-- Buttons -->
          <div class="flex items-center justify-center gap-3">
            <button
              type="button"
              @click="showWarningAlert = false"
              class="px-4 py-2 rounded-xl text-xs font-semibold border transition-colors cursor-pointer"
              :class="isDark ? 'border-stone-700 bg-stone-800 text-stone-300 hover:bg-stone-700' : 'border-stone-300 bg-stone-100 text-stone-700 hover:bg-stone-200'"
            >
              {{ labels.sweetAlertCancelBtn }}
            </button>
            <button
              type="button"
              @click="confirmReset"
              class="px-4 py-2 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-500 text-white shadow-md shadow-rose-600/30 transition-transform hover:scale-102 active:scale-98 cursor-pointer"
            >
              {{ labels.sweetAlertConfirmBtn }}
            </button>
          </div>
        </div>
      </div>

      <!-- SweetAlert Success Modal Overlay -->
      <div
        v-if="showSuccessAlert"
        class="absolute inset-0 z-20 flex items-center justify-center p-6 bg-black/75 backdrop-blur-md animate-fade-in"
      >
        <div
          class="w-full max-w-md p-6 rounded-3xl border text-center shadow-2xl transition-all scale-100"
          :class="isDark ? 'bg-stone-900 border-emerald-500/40 text-stone-100' : 'bg-white border-emerald-400 text-stone-900'"
        >
          <!-- Success Icon Badge -->
          <div class="w-14 h-14 mx-auto mb-4 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center text-2xl font-black border border-emerald-500/40 shadow-inner">
            ✓
          </div>

          <h3 class="text-base sm:text-lg font-bold mb-2">
            {{ labels.sweetAlertSuccessTitle }}
          </h3>
          <p class="text-xs text-stone-500 dark:text-stone-400 mb-6 leading-relaxed">
            {{ labels.sweetAlertSuccessText }}
          </p>

          <!-- Button -->
          <button
            type="button"
            @click="showSuccessAlert = false"
            class="px-6 py-2 rounded-xl text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/30 transition-transform hover:scale-102 active:scale-98 cursor-pointer"
          >
            {{ labels.sweetAlertOkBtn }}
          </button>
        </div>
      </div>

      <!-- Modal Header -->
      <div
        class="flex items-center justify-between gap-3 mb-6 pb-4 border-b"
        :class="isDark ? 'border-stone-800' : 'border-stone-200'"
      >
        <div class="flex items-center gap-3">
          <div class="p-2.5 rounded-2xl bg-amber-500/10 text-amber-600 dark:text-amber-400">
            <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="20" x2="18" y2="10"/>
              <line x1="12" y1="20" x2="12" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="14"/>
            </svg>
          </div>
          <div>
            <h3 class="font-bold text-lg tracking-tight">{{ labels.metricsTitle }}</h3>
            <p class="text-xs text-stone-500 dark:text-stone-400">
              {{ labels.metricsSubtitle }}
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="emit('close')"
          class="p-2 rounded-xl text-stone-400 hover:text-stone-600 dark:hover:text-stone-200 transition-colors cursor-pointer"
        >
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="py-12 text-center text-sm text-stone-500">
        <div class="animate-spin w-8 h-8 mx-auto mb-2 border-2 border-amber-600 border-t-transparent rounded-full"></div>
        {{ labels.loadingMetrics }}
      </div>

      <!-- Metrics Grid -->
      <div v-else-if="metrics" class="space-y-4">
        <!-- Top Stats Row -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <!-- Total Queries -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
          >
            <span class="text-xs font-medium text-stone-500 dark:text-stone-400 block mb-1">{{ labels.totalQueries }}</span>
            <span class="text-2xl font-black text-amber-600 dark:text-amber-400">{{ metrics.total_queries }}</span>
          </div>

          <!-- AI Resolved -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
          >
            <span class="text-xs font-medium text-stone-500 dark:text-stone-400 block mb-1">{{ labels.resolvedByAI }}</span>
            <span class="text-2xl font-black text-emerald-600 dark:text-emerald-400">{{ metrics.resolved_by_ai_queries }}</span>
          </div>

          <!-- Escalation Rate -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
          >
            <span class="text-xs font-medium text-stone-500 dark:text-stone-400 block mb-1">{{ labels.humanEscalation }}</span>
            <div class="flex items-baseline gap-1">
              <span class="text-2xl font-black text-rose-600 dark:text-rose-400">{{ metrics.escalated_queries }}</span>
              <span class="text-xs font-semibold text-stone-500">({{ metrics.escalation_rate_pct }}%)</span>
            </div>
          </div>

          <!-- Cache Hits -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
          >
            <span class="text-xs font-medium text-stone-500 dark:text-stone-400 block mb-1">{{ labels.cacheHits }}</span>
            <div class="flex items-baseline gap-1">
              <span class="text-2xl font-black text-amber-600 dark:text-amber-400">{{ metrics.performance.cache.hits }}</span>
              <span class="text-xs font-semibold text-stone-500">({{ metrics.performance.cache.hit_rate_pct }}%)</span>
            </div>
          </div>
        </div>

        <!-- Token & Cost Section -->
        <div class="p-4 sm:p-5 rounded-2xl border backdrop-blur-md"
          :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
        >
          <h4 class="text-xs font-bold uppercase tracking-wider text-stone-500 dark:text-stone-400 mb-3">
            {{ labels.tokenSectionTitle }}
          </h4>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <span class="text-stone-500 block">{{ labels.totalTokens }}</span>
              <span class="font-bold text-stone-800 dark:text-stone-200 text-sm">
                {{ metrics.tokens.total_tokens.toLocaleString() }}
              </span>
            </div>
            <div>
              <span class="text-stone-500 block">{{ labels.savedTokens }}</span>
              <span class="font-bold text-emerald-600 dark:text-emerald-400 text-sm">
                {{ metrics.tokens.tokens_saved_by_cache.toLocaleString() }}
              </span>
            </div>
            <div>
              <span class="text-stone-500 block">{{ labels.localCost }}</span>
              <span class="font-bold text-stone-800 dark:text-stone-200 text-sm">
                {{ labels.freeLocal }}
              </span>
            </div>
          </div>
        </div>

        <!-- Performance / Latency Section -->
        <div class="p-4 rounded-2xl border backdrop-blur-md flex items-center justify-between text-xs"
          :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
        >
          <div>
            <span class="text-stone-500 block">{{ labels.avgLatency }}</span>
            <span class="font-bold text-sm text-stone-800 dark:text-stone-200">{{ metrics.performance.avg_latency_ms }} ms</span>
          </div>
          <div>
            <span class="text-stone-500 block">{{ labels.cacheSize }}</span>
            <span class="font-bold text-sm text-stone-800 dark:text-stone-200">{{ metrics.performance.cache.cache_size }} / {{ metrics.performance.cache.max_size }}</span>
          </div>
          <div>
            <span class="text-stone-500 block">{{ labels.uptime }}</span>
            <span class="font-bold text-sm text-stone-800 dark:text-stone-200">{{ Math.floor(metrics.performance.uptime_seconds / 60) }} min</span>
          </div>
        </div>
      </div>

      <!-- Modal Footer Actions -->
      <div
        class="mt-6 pt-4 border-t flex items-center justify-between gap-3"
        :class="isDark ? 'border-stone-800' : 'border-stone-200'"
      >
        <button
          type="button"
          @click="promptReset"
          :disabled="resetting"
          class="flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 transition-all hover:scale-102 active:scale-98 cursor-pointer"
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
          class="px-5 py-2 rounded-xl text-xs font-semibold bg-stone-900 hover:bg-stone-800 text-white dark:bg-amber-600 dark:hover:bg-amber-500 transition-colors shadow-sm cursor-pointer"
        >
          {{ labels.closeBtn }}
        </button>
      </div>
    </div>
  </div>
</template>
