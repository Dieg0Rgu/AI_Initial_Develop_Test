<script setup lang="ts">
import { ref } from 'vue'
import type { ChatMessage } from '../types/chat'
import logoImg from '../assets/gastroteacher-logo.png'

defineProps<{
  message: ChatMessage
  isDark: boolean
  labels: {
    you: string
    assistant: string
    escalatedTitle: string
    escalatedDesc: string
    whatsappBtn: string
    emailBtn: string
    cachedBadge: string
    viewSources: string
    hideSources: string
    officialDocs: string
  }
}>()

const showSources = ref(false)

function formatContent(text: string) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-stone-900 dark:text-stone-100">$1</strong>')
    .replace(/^- (.*)$/gm, '<li class="ml-4 list-disc">$1</li>')
    .replace(/\n\n/g, '<br/><br/>')
    .replace(/\n/g, '<br/>')
}
</script>

<template>
  <div
    class="flex flex-col gap-2 w-full transition-all duration-300"
    :class="message.role === 'user' ? 'items-end' : 'items-start'"
  >
    <!-- Message Container -->
    <div
      class="max-w-[88%] sm:max-w-[80%] rounded-2xl p-4 sm:p-5 backdrop-blur-xl border shadow-sm transition-all duration-200"
      :class="[
        message.role === 'user'
          ? isDark
            ? 'bg-gradient-to-br from-amber-700/80 to-orange-800/80 border-amber-600/40 text-amber-50 rounded-br-xs'
            : 'bg-gradient-to-br from-amber-600 to-orange-600 border-amber-500/50 text-white rounded-br-xs shadow-amber-900/10'
          : isDark
            ? 'bg-stone-900/80 border-stone-800 text-stone-200 rounded-bl-xs'
            : 'bg-white/85 border-stone-200/90 text-stone-800 rounded-bl-xs'
      ]"
    >
      <!-- Message Header -->
      <div
        class="flex items-center justify-between gap-3 mb-2 pb-1.5 border-b"
        :class="message.role === 'user' ? 'border-white/20' : 'border-stone-200/60 dark:border-stone-800/60'"
      >
        <div class="flex items-center gap-2">
          <!-- Role Icon -->
          <div
            v-if="message.role === 'assistant'"
            class="w-6 h-6 rounded-full overflow-hidden border border-stone-300 dark:border-stone-700 bg-white flex items-center justify-center shrink-0"
          >
            <img :src="logoImg" alt="Gastroteacher" class="w-full h-full object-cover" />
          </div>
          <span
            class="text-xs font-semibold tracking-wide"
            :class="message.role === 'user' ? 'text-amber-100' : 'text-stone-700 dark:text-stone-300'"
          >
            {{ message.role === 'user' ? labels.you : labels.assistant }}
          </span>
        </div>

        <span class="text-[10px] opacity-70">
          {{ message.timestamp }}
        </span>
      </div>

      <!-- Human Escalation Banner -->
      <div
        v-if="message.is_escalated"
        class="mb-3 p-3 rounded-xl border backdrop-blur-md flex items-start gap-2.5"
        :class="
          isDark
            ? 'bg-rose-950/40 border-rose-800/60 text-rose-200'
            : 'bg-rose-50/90 border-rose-200 text-rose-800'
        "
      >
        <div class="p-1 rounded-lg bg-rose-500/20 text-rose-600 dark:text-rose-400 mt-0.5 shrink-0">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
        <div class="flex-1">
          <h4 class="text-xs font-bold uppercase tracking-wider">
            {{ labels.escalatedTitle }}
          </h4>
          <p class="text-xs mt-0.5 opacity-90">
            {{ labels.escalatedDesc }}
          </p>
          <!-- Quick Contact Action Buttons -->
          <div class="mt-2.5 flex flex-wrap gap-2">
            <a
              href="https://wa.me/573017325327"
              target="_blank"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-600 text-white hover:bg-emerald-700 transition-colors shadow-xs"
            >
              <span>{{ labels.whatsappBtn }}</span>
            </a>
            <a
              href="mailto:soporte@gastroteacher.edu.co"
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold border transition-colors"
              :class="isDark ? 'bg-stone-800 border-stone-700 text-stone-200 hover:bg-stone-700' : 'bg-white border-stone-300 text-stone-700 hover:bg-stone-100'"
            >
              <span>{{ labels.emailBtn }}</span>
            </a>
          </div>
        </div>
      </div>

      <!-- Message Content -->
      <div
        class="text-sm leading-relaxed whitespace-pre-wrap break-words"
        v-html="formatContent(message.content)"
      ></div>

      <!-- Metadata Badges (Assistant only) -->
      <div
        v-if="message.role === 'assistant'"
        class="mt-3 pt-2.5 border-t flex flex-wrap items-center justify-between gap-2 text-[10px]"
        :class="isDark ? 'border-stone-800/80 text-stone-400' : 'border-stone-200/80 text-stone-500'"
      >
        <div class="flex items-center gap-2">
          <!-- Cache Pill -->
          <span
            v-if="message.cached"
            class="px-2 py-0.5 rounded-md font-semibold bg-emerald-100 dark:bg-emerald-950/60 text-emerald-700 dark:text-emerald-300 border border-emerald-300/60 dark:border-emerald-800/60 flex items-center gap-1"
          >
            <svg class="w-3 h-3 text-emerald-600 dark:text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
            </svg>
            <span>{{ labels.cachedBadge }}</span>
          </span>

          <!-- Latency -->
          <span v-if="message.latency_ms !== undefined" class="flex items-center gap-1">
            <svg class="w-3 h-3 text-stone-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            <span>{{ message.latency_ms }} ms</span>
          </span>

          <!-- Tokens -->
          <span v-if="message.token_usage" class="flex items-center gap-1">
            <svg class="w-3 h-3 text-stone-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>
              <rect x="9" y="9" width="6" height="6"/>
              <line x1="9" y1="1" x2="9" y2="4"/>
              <line x1="15" y1="1" x2="15" y2="4"/>
              <line x1="9" y1="20" x2="9" y2="23"/>
              <line x1="15" y1="20" x2="15" y2="23"/>
            </svg>
            <span>{{ message.token_usage.total_tokens }} tokens</span>
          </span>
        </div>

        <!-- Sources Toggle Button -->
        <button
          v-if="message.sources && message.sources.length > 0"
          type="button"
          @click="showSources = !showSources"
          class="flex items-center gap-1 px-2 py-0.5 rounded-md font-medium transition-colors hover:underline cursor-pointer"
          :class="isDark ? 'text-amber-400 hover:text-amber-300' : 'text-amber-700 hover:text-amber-800'"
        >
          <svg class="w-3 h-3 transition-transform" :class="{ 'rotate-180': showSources }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
          <span>{{ showSources ? labels.hideSources : labels.viewSources.replace('{count}', String(message.sources.length)) }}</span>
        </button>
      </div>

      <!-- Sources Drawer -->
      <div
        v-if="showSources && message.sources && message.sources.length > 0"
        class="mt-3 pt-3 border-t space-y-2 text-xs"
        :class="isDark ? 'border-stone-800' : 'border-stone-200'"
      >
        <div class="font-semibold text-stone-600 dark:text-stone-300 flex items-center gap-1.5">
          <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <span>{{ labels.officialDocs }}</span>
        </div>

        <div
          v-for="(src, sIdx) in message.sources"
          :key="sIdx"
          class="p-2.5 rounded-xl border backdrop-blur-md"
          :class="isDark ? 'bg-stone-950/60 border-stone-800 text-stone-300' : 'bg-stone-50 border-stone-200/90 text-stone-700'"
        >
          <div class="flex items-center justify-between gap-2 mb-1">
            <div class="flex items-center gap-1.5 truncate">
              <svg class="w-3.5 h-3.5 text-stone-400 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <span class="font-semibold text-amber-700 dark:text-amber-400 truncate">
                {{ src.source }}
              </span>
            </div>
            <span class="text-[10px] px-1.5 py-0.2 rounded-md font-mono bg-stone-200 dark:bg-stone-800 shrink-0">
              Score: {{ (src.similarity_score * 100).toFixed(1) }}%
            </span>
          </div>
          <p class="text-[11px] leading-relaxed text-stone-600 dark:text-stone-400 italic">
            "{{ src.excerpt }}"
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
