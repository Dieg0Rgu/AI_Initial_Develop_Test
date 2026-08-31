<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { MetricsSummary } from '../types/chat'
import { fetchMetrics, resetMetrics } from '../services/api'

defineProps<{
  isDark: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
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

async function handleReset() {
  if (!confirm('¿Estás seguro de que deseas reiniciar los contadores de métricas y caché?')) return
  resetting.value = true
  try {
    await resetMetrics()
    await loadMetrics()
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
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm transition-opacity">
    <div
      class="w-full max-w-2xl rounded-3xl p-6 sm:p-7 backdrop-blur-2xl border shadow-2xl transition-all duration-300 transform scale-100"
      :class="isDark ? 'bg-stone-900/90 border-stone-800 text-stone-100' : 'bg-white/95 border-stone-200 text-stone-900'"
    >
      <!-- Modal Header -->
      <div class="flex items-center justify-between gap-3 mb-6 pb-4 border-b"
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
            <h3 class="font-bold text-lg tracking-tight">Panel de Métricas & Rendimiento</h3>
            <p class="text-xs text-stone-500 dark:text-stone-400">
              Analítica de consultas, ahorro por caché y tasa de escalamiento
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="emit('close')"
          class="p-2 rounded-xl text-stone-400 hover:text-stone-600 dark:hover:text-stone-200 transition-colors"
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
        Cargando métricas en tiempo real...
      </div>

      <!-- Metrics Grid -->
      <div v-else-if="metrics" class="space-y-4">
        <!-- Top Stats Row -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <!-- Total Queries -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
          >
            <span class="text-xs font-medium text-stone-500 dark:text-stone-400 block mb-1">Total Consultas</span>
            <span class="text-2xl font-black text-amber-600 dark:text-amber-400">{{ metrics.total_queries }}</span>
          </div>

          <!-- AI Resolved -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
          >
            <span class="text-xs font-medium text-stone-500 dark:text-stone-400 block mb-1">Resueltas por IA</span>
            <span class="text-2xl font-black text-emerald-600 dark:text-emerald-400">{{ metrics.resolved_by_ai_queries }}</span>
          </div>

          <!-- Escalation Rate -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
          >
            <span class="text-xs font-medium text-stone-500 dark:text-stone-400 block mb-1">Escalamiento Humano</span>
            <div class="flex items-baseline gap-1">
              <span class="text-2xl font-black text-rose-600 dark:text-rose-400">{{ metrics.escalated_queries }}</span>
              <span class="text-xs font-semibold text-stone-500">({{ metrics.escalation_rate_pct }}%)</span>
            </div>
          </div>

          <!-- Cache Hits -->
          <div class="p-4 rounded-2xl border backdrop-blur-md"
            :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
          >
            <span class="text-xs font-medium text-stone-500 dark:text-stone-400 block mb-1">Aciertos de Caché</span>
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
            Consumo de Tokens y Ahorro Estimado
          </h4>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <span class="text-stone-500 block">Total Tokens Procesados:</span>
              <span class="font-bold text-stone-800 dark:text-stone-200 text-sm">
                {{ metrics.tokens.total_tokens.toLocaleString() }}
              </span>
            </div>
            <div>
              <span class="text-stone-500 block">Tokens Ahorrados (Caché):</span>
              <span class="font-bold text-emerald-600 dark:text-emerald-400 text-sm">
                {{ metrics.tokens.tokens_saved_by_cache.toLocaleString() }}
              </span>
            </div>
            <div>
              <span class="text-stone-500 block">Costo en Ollama Local:</span>
              <span class="font-bold text-stone-800 dark:text-stone-200 text-sm">
                $0.00 COP (100% Local)
              </span>
            </div>
          </div>
        </div>

        <!-- Performance / Latency Section -->
        <div class="p-4 rounded-2xl border backdrop-blur-md flex items-center justify-between text-xs"
          :class="isDark ? 'bg-stone-950/50 border-stone-800' : 'bg-stone-50 border-stone-200'"
        >
          <div>
            <span class="text-stone-500 block">Latencia Promedio:</span>
            <span class="font-bold text-sm text-stone-800 dark:text-stone-200">{{ metrics.performance.avg_latency_ms }} ms</span>
          </div>
          <div>
            <span class="text-stone-500 block">Tamaño Caché en Memoria:</span>
            <span class="font-bold text-sm text-stone-800 dark:text-stone-200">{{ metrics.performance.cache.cache_size }} / {{ metrics.performance.cache.max_size }}</span>
          </div>
          <div>
            <span class="text-stone-500 block">Tiempo de Actividad:</span>
            <span class="font-bold text-sm text-stone-800 dark:text-stone-200">{{ Math.floor(metrics.performance.uptime_seconds / 60) }} min</span>
          </div>
        </div>
      </div>

      <!-- Modal Footer Actions -->
      <div class="mt-6 pt-4 border-t flex items-center justify-between gap-3"
        :class="isDark ? 'border-stone-800' : 'border-stone-200'"
      >
        <button
          type="button"
          @click="handleReset"
          :disabled="resetting"
          class="px-3.5 py-2 rounded-xl text-xs font-semibold text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 transition-colors"
        >
          {{ resetting ? 'Reiniciando...' : 'Reiniciar Métricas' }}
        </button>

        <button
          type="button"
          @click="emit('close')"
          class="px-5 py-2 rounded-xl text-xs font-semibold bg-stone-900 hover:bg-stone-800 text-white dark:bg-amber-600 dark:hover:bg-amber-500 transition-colors shadow-sm"
        >
          Cerrar
        </button>
      </div>
    </div>
  </div>
</template>
