<script setup lang="ts">
defineProps<{
  isDark: boolean
  isOnline: boolean
  totalQueries: number
}>()

const emit = defineEmits<{
  (e: 'toggleTheme'): void
  (e: 'openMetrics'): void
}>()
</script>

<template>
  <header
    class="sticky top-0 z-30 w-full backdrop-blur-xl transition-colors duration-300 border-b"
    :class="
      isDark
        ? 'bg-stone-900/75 border-stone-800 text-stone-100'
        : 'bg-stone-50/80 border-stone-200/80 text-stone-800'
    "
  >
    <div class="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-3">
      <!-- Brand & Logo -->
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-2xl flex items-center justify-center shadow-md shadow-amber-900/10 transition-transform hover:scale-105"
          :class="isDark ? 'bg-linear-to-r from-amber-700 to-orange-900 text-amber-100' : 'bg-linear-to-r from-amber-600 to-orange-700 text-white'"
        >
          <!-- Gastroteacher Chef Hat + Book Icon -->
          <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M6 13.87A4 4 0 0 1 7.41 6a5.11 5.11 0 0 1 1.05-1.54 5 5 0 0 1 7.08 0A5.11 5.11 0 0 1 16.59 6 4 4 0 0 1 18 13.87V21H6Z"/>
            <line x1="6" y1="17" x2="18" y2="17"/>
          </svg>
        </div>

        <div>
          <div class="flex items-center gap-2">
            <span class="font-bold text-lg tracking-tight bg-linear-to-r from-amber-700 via-orange-600 to-amber-900 bg-clip-text text-transparent dark:from-amber-400 dark:via-orange-300 dark:to-amber-200">
              Gastroteacher
            </span>
            <span class="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full border tracking-wider"
              :class="isDark ? 'bg-amber-950/60 border-amber-800/60 text-amber-300' : 'bg-amber-100/80 border-amber-300/80 text-amber-900'">
              RAG v1.0
            </span>
          </div>
          <p class="text-xs text-stone-500 dark:text-stone-400 font-medium">
            Academia de Idiomas & Gastronomía
          </p>
        </div>
      </div>

      <!-- Actions & Status -->
      <div class="flex items-center gap-2 sm:gap-3">
        <!-- Status Indicator -->
        <div
          class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border shadow-xs"
          :class="
            isOnline
              ? isDark ? 'bg-emerald-950/40 border-emerald-800/50 text-emerald-400' : 'bg-emerald-50 border-emerald-200 text-emerald-700'
              : isDark ? 'bg-rose-950/40 border-rose-800/50 text-rose-400' : 'bg-rose-50 border-rose-200 text-rose-700'
          "
        >
          <span class="relative flex h-2 w-2">
            <span
              class="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75"
              :class="isOnline ? 'bg-emerald-400' : 'bg-rose-400'"
            ></span>
            <span
              class="relative inline-flex rounded-full h-2 w-2"
              :class="isOnline ? 'bg-emerald-500' : 'bg-rose-500'"
            ></span>
          </span>
          <span>{{ isOnline ? 'IA & RAG Online' : 'Desconectado' }}</span>
        </div>

        <!-- Metrics Button -->
        <button
          type="button"
          @click="emit('openMetrics')"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all duration-200 shadow-xs hover:scale-102 active:scale-98"
          :class="
            isDark
              ? 'bg-stone-800/90 hover:bg-stone-700/90 border-stone-700 text-stone-200 hover:border-amber-700/50'
              : 'bg-white/90 hover:bg-stone-100 border-stone-300 text-stone-700 hover:border-amber-600/50'
          "
          title="Ver métricas y analítica"
        >
          <svg class="w-4 h-4 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"/>
            <line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
          <span>Métricas</span>
          <span
            v-if="totalQueries > 0"
            class="ml-1 px-1.5 py-0.2 text-[10px] rounded-full bg-amber-600 text-white font-bold"
          >
            {{ totalQueries }}
          </span>
        </button>

        <!-- Theme Toggle -->
        <button
          type="button"
          @click="emit('toggleTheme')"
          class="p-2 rounded-xl border transition-all duration-200 shadow-xs hover:scale-105 active:scale-95"
          :class="
            isDark
              ? 'bg-stone-800/90 hover:bg-stone-700 border-stone-700 text-amber-300'
              : 'bg-white/90 hover:bg-stone-100 border-stone-300 text-amber-600'
          "
          :title="isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'"
        >
          <!-- Sun icon -->
          <svg v-if="isDark" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <!-- Moon icon -->
          <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>
