<script setup lang="ts">
import logoImg from '../assets/gastroteacher-logo.png'
import type { Language } from '../i18n/translations'

defineProps<{
  isDark: boolean
  isOnline: boolean
  totalQueries: number
  currentLang: Language
  labels: {
    subtitle: string
    statusOnline: string
    statusOffline: string
    metricsBtn: string
    exportPdfBtn: string
    themeLight: string
    themeDark: string
  }
}>()

const emit = defineEmits<{
  (e: 'toggleTheme'): void
  (e: 'openMetrics'): void
  (e: 'toggleLang'): void
  (e: 'openExportPdf'): void
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
      <!-- Brand & Official Logo -->
      <div class="flex items-center gap-3">
        <div
          class="w-11 h-11 rounded-full overflow-hidden border-2 shadow-sm transition-transform hover:scale-105 flex items-center justify-center shrink-0"
          :class="isDark ? 'border-amber-600/50 bg-stone-900' : 'border-stone-300 bg-white'"
        >
          <img
            :src="logoImg"
            alt="Gastroteacher Logo"
            class="w-full h-full object-cover"
          />
        </div>

        <div>
          <div class="flex items-center gap-2">
            <span class="font-bold text-lg tracking-tight bg-gradient-to-r from-amber-700 via-orange-600 to-amber-900 bg-clip-text text-transparent dark:from-amber-400 dark:via-orange-300 dark:to-amber-200">
              Gastroteacher
            </span>
            <span
              class="text-[10px] uppercase font-semibold px-2 py-0.5 rounded-full border tracking-wider"
              :class="isDark ? 'bg-amber-950/60 border-amber-800/60 text-amber-300' : 'bg-amber-100/80 border-amber-300/80 text-amber-900'"
            >
              RAG v1.0
            </span>
          </div>
          <p class="text-xs text-stone-500 dark:text-stone-400 font-medium">
            {{ labels.subtitle }}
          </p>
        </div>
      </div>

      <!-- Actions & Status -->
      <div class="flex items-center gap-2 sm:gap-2.5">
        <!-- Status Indicator -->
        <div
          class="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border shadow-xs"
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
          <span>{{ isOnline ? labels.statusOnline : labels.statusOffline }}</span>
        </div>

        <!-- Export PDF Button -->
        <button
          type="button"
          @click="emit('openExportPdf')"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all duration-200 shadow-xs hover:scale-102 active:scale-98 cursor-pointer"
          :class="
            isDark
              ? 'bg-stone-800/90 hover:bg-stone-700/90 border-stone-700 text-rose-300 hover:border-rose-700/50'
              : 'bg-white/90 hover:bg-stone-100 border-stone-300 text-rose-700 hover:border-rose-600/50'
          "
          :title="labels.exportPdfBtn"
        >
          <svg class="w-4 h-4 text-rose-600 dark:text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          <span class="hidden sm:inline">{{ labels.exportPdfBtn }}</span>
        </button>

        <!-- Language Switcher -->
        <button
          type="button"
          @click="emit('toggleLang')"
          class="flex items-center gap-1 px-2.5 py-1.5 rounded-xl border text-xs font-bold transition-all duration-200 shadow-xs hover:scale-105 active:scale-95 cursor-pointer"
          :class="
            isDark
              ? 'bg-stone-800/90 hover:bg-stone-700 border-stone-700 text-stone-200'
              : 'bg-white/90 hover:bg-stone-100 border-stone-300 text-stone-700'
          "
          :title="currentLang === 'es' ? 'Switch to English' : 'Cambiar a Español'"
        >
          <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="2" y1="12" x2="22" y2="12"/>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
          </svg>
          <span :class="{ 'text-amber-600 dark:text-amber-400 font-extrabold': currentLang === 'es', 'opacity-60': currentLang !== 'es' }">ES</span>
          <span class="opacity-30">|</span>
          <span :class="{ 'text-amber-600 dark:text-amber-400 font-extrabold': currentLang === 'en', 'opacity-60': currentLang !== 'en' }">EN</span>
        </button>

        <!-- Metrics Button -->
        <button
          type="button"
          @click="emit('openMetrics')"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all duration-200 shadow-xs hover:scale-102 active:scale-98 cursor-pointer"
          :class="
            isDark
              ? 'bg-stone-800/90 hover:bg-stone-700/90 border-stone-700 text-stone-200 hover:border-amber-700/50'
              : 'bg-white/90 hover:bg-stone-100 border-stone-300 text-stone-700 hover:border-amber-600/50'
          "
          :title="labels.metricsBtn"
        >
          <svg class="w-4 h-4 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="20" x2="18" y2="10"/>
            <line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
          <span class="hidden md:inline">{{ labels.metricsBtn }}</span>
          <span
            v-if="totalQueries > 0"
            class="px-1.5 py-0.2 text-[10px] rounded-full bg-amber-600 text-white font-bold"
          >
            {{ totalQueries }}
          </span>
        </button>

        <!-- Theme Toggle -->
        <button
          type="button"
          @click="emit('toggleTheme')"
          class="p-2 rounded-xl border transition-all duration-200 shadow-xs hover:scale-105 active:scale-95 cursor-pointer"
          :class="
            isDark
              ? 'bg-stone-800/90 hover:bg-stone-700 border-stone-700 text-amber-300'
              : 'bg-white/90 hover:bg-stone-100 border-stone-300 text-amber-600'
          "
          :title="isDark ? labels.themeLight : labels.themeDark"
        >
          <svg v-if="isDark" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="12" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>
