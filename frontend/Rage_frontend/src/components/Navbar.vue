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
    class="sticky top-0 z-30 w-full backdrop-blur-md transition-colors duration-200 border-b-2"
    :class="
      isDark
        ? 'bg-stone-950/95 border-stone-800 text-stone-100'
        : 'bg-white/95 border-stone-900 text-stone-950 shadow-xs'
    "
  >
    <div class="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-3">
      <!-- Brand & Constructivist Logo Framing -->
      <div class="flex items-center gap-3">
        <!-- Logo Reticle Framing -->
        <div
          class="w-11 h-11 border-2 p-0.5 transition-transform hover:scale-105 flex items-center justify-center shrink-0 relative shadow-[2px_2px_0px_0px_#d97706]"
          :class="isDark ? 'border-amber-500 bg-stone-900' : 'border-stone-900 bg-white'"
        >
          <div class="absolute -top-1 -left-1 w-1.5 h-1.5 bg-amber-600"></div>
          <div class="absolute -bottom-1 -right-1 w-1.5 h-1.5 bg-amber-600"></div>
          <img
            :src="logoImg"
            alt="Gastroteacher Logo"
            class="w-full h-full object-cover"
          />
        </div>

        <div>
          <div class="flex items-center gap-2">
            <span
              class="font-black text-lg tracking-tight uppercase"
              :class="isDark ? 'text-amber-400' : 'text-stone-950'"
            >
              Gastroteacher
            </span>
            <span
              class="font-mono text-[9px] uppercase font-black px-1.5 py-0.5 border tracking-wider"
              :class="isDark ? 'bg-amber-950/80 border-amber-600 text-amber-300' : 'bg-amber-100 border-stone-900 text-stone-950'"
            >
              [SYS // RAG-v1]
            </span>
          </div>
          <p
            class="font-mono text-[11px] font-bold tracking-tight"
            :class="isDark ? 'text-stone-400' : 'text-stone-700'"
          >
            // {{ labels.subtitle.toUpperCase() }}
          </p>
        </div>
      </div>

      <!-- Actions & Status Panel -->
      <div class="flex items-center gap-2 sm:gap-2.5">
        <!-- Technical Status Indicator -->
        <div
          class="hidden lg:flex items-center gap-2 px-2.5 py-1 text-[11px] font-mono font-black border-2 shadow-[2px_2px_0px_0px_rgba(0,0,0,0.8)]"
          :class="
            isOnline
              ? isDark
                ? 'border-emerald-600 bg-stone-900 text-emerald-400'
                : 'border-stone-900 bg-emerald-50 text-emerald-950'
              : isDark
                ? 'border-rose-600 bg-stone-900 text-rose-400'
                : 'border-stone-900 bg-rose-50 text-rose-950'
          "
        >
          <div
            class="w-2 h-2 shrink-0"
            :class="isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'"
          ></div>
          <span class="tracking-wide">
            {{ isOnline ? '[ONLINE // READY]' : '[OFFLINE // ERR]' }}
          </span>
          <span class="text-[10px] opacity-70">
            (#{{ totalQueries }})
          </span>
        </div>

        <!-- Metrics Button -->
        <button
          type="button"
          @click="emit('openMetrics')"
          class="flex items-center gap-1.5 px-3 py-1.5 font-mono text-xs font-black uppercase tracking-wider border-2 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 cursor-pointer shadow-[2px_2px_0px_0px_#d97706]"
          :class="
            isDark
              ? 'bg-stone-900 border-amber-500/80 text-amber-400 hover:bg-stone-800'
              : 'bg-white border-stone-900 text-stone-950 hover:bg-amber-50'
          "
          :title="labels.metricsBtn"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="20" x2="18" y2="10"/>
            <line x1="12" y1="20" x2="12" y2="4"/>
            <line x1="6" y1="20" x2="6" y2="14"/>
          </svg>
          <span class="hidden sm:inline">{{ labels.metricsBtn }}</span>
        </button>

        <!-- Export Documents / Chat PDF Button -->
        <button
          type="button"
          @click="emit('openExportPdf')"
          class="flex items-center gap-1.5 px-3 py-1.5 font-mono text-xs font-black uppercase tracking-wider border-2 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 cursor-pointer shadow-[2px_2px_0px_0px_#e11d48]"
          :class="
            isDark
              ? 'bg-stone-900 border-rose-500/80 text-rose-400 hover:bg-stone-800'
              : 'bg-white border-stone-900 text-rose-950 hover:bg-rose-50'
          "
          :title="labels.exportPdfBtn"
        >
          <svg class="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          <span class="hidden sm:inline">{{ labels.exportPdfBtn }}</span>
        </button>

        <!-- Language Toggle -->
        <button
          type="button"
          @click="emit('toggleLang')"
          class="px-2.5 py-1.5 font-mono text-xs font-black border-2 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 cursor-pointer"
          :class="
            isDark
              ? 'bg-stone-900 border-stone-700 text-stone-200 hover:border-amber-500 shadow-[2px_2px_0px_0px_#78350f]'
              : 'bg-white border-stone-900 text-stone-950 hover:bg-stone-100 shadow-[2px_2px_0px_0px_#1c1917]'
          "
          :title="currentLang === 'es' ? 'Switch to English' : 'Cambiar a Español'"
        >
          <span :class="currentLang === 'es' ? 'text-amber-600 dark:text-amber-400' : ''">ES</span>
          <span class="mx-0.5 opacity-40">/</span>
          <span :class="currentLang === 'en' ? 'text-amber-600 dark:text-amber-400' : ''">EN</span>
        </button>

        <!-- Theme Toggle -->
        <button
          type="button"
          @click="emit('toggleTheme')"
          class="p-2 border-2 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 cursor-pointer"
          :class="
            isDark
              ? 'bg-stone-900 border-stone-700 text-amber-400 hover:border-amber-400 shadow-[2px_2px_0px_0px_#f59e0b]'
              : 'bg-white border-stone-900 text-stone-800 hover:text-amber-600 shadow-[2px_2px_0px_0px_#1c1917]'
          "
          :title="isDark ? labels.themeLight : labels.themeDark"
        >
          <!-- Sun Icon -->
          <svg v-if="isDark" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
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
          <!-- Moon Icon -->
          <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>
