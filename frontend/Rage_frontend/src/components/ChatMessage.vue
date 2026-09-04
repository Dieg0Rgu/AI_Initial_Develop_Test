<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { animate } from 'animejs'
import moment from 'moment'
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

const emit = defineEmits<{
  (e: 'escalationAction', payload: { type: 'whatsapp' | 'email'; contact: string }): void
}>()

const showSources = ref(false)
const messageEl = ref<HTMLElement | null>(null)

onMounted(() => {
  if (messageEl.value) {
    animate(messageEl.value, {
      translateY: [15, 0],
      opacity: [0, 1],
      duration: 350,
      ease: 'outQuad'
    })
  }
})

function formatDisplayTime(ts: string) {
  if (!ts) return moment().format('LT')
  return ts
}

function inlineFormat(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong class="font-black text-stone-950 dark:text-stone-100">$1</strong>')
    .replace(/`([^`]+)`/g, '<code class="font-mono text-xs px-1.5 py-0.5 bg-stone-200 dark:bg-stone-800 text-amber-700 dark:text-amber-400 border border-stone-300 dark:border-stone-700">$1</code>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener" class="underline font-bold text-amber-700 dark:text-amber-400 hover:text-amber-800">$1</a>')
}

function formatContent(text: string): string {
  if (!text) return ''

  // 1. Pre-process markdown tables: eliminate raw pipes, table separator lines (|---|---|) and format into clean bullets
  const rawLines = text.split('\n')
  const preprocessed: string[] = []
  let i = 0

  while (i < rawLines.length) {
    const rawLine = rawLines[i]
    const trimmed = rawLine.trim()

    // Skip table divider lines like |---|---| or |:---|:---| or ---|---
    if (/^[\|\s\-:]+$/.test(trimmed) && trimmed.includes('-') && (trimmed.includes('|') || trimmed.length >= 3)) {
      if (trimmed.includes('|')) {
        i++
        continue
      }
    }

    // Detect markdown table rows
    if (trimmed.includes('|')) {
      const cells = trimmed.split('|').map(c => c.trim()).filter(c => c.length > 0)
      // Check if followed by a table divider line (header row)
      let followedByDivider = false
      if (i + 1 < rawLines.length) {
        const nextTrimmed = rawLines[i + 1].trim()
        if (/^[\|\s\-:]+$/.test(nextTrimmed) && nextTrimmed.includes('-') && nextTrimmed.includes('|')) {
          followedByDivider = true
        }
      }

      if (followedByDivider) {
        // Table header: skip it
        i++
        continue
      }

      if (cells.length >= 2) {
        preprocessed.push(`- **${cells[0]}**: ${cells.slice(1).join(' - ')}`)
        i++
        continue
      } else if (cells.length === 1) {
        preprocessed.push(`- ${cells[0]}`)
        i++
        continue
      }
    }

    // Strip any stray pipes from regular lines
    if (rawLine.includes('|')) {
      const cleanL = rawLine.replace(/^\s*\|\s*/, '').replace(/\s*\|\s*$/, '').replace(/\|/g, ' - ')
      preprocessed.push(cleanL)
    } else {
      preprocessed.push(rawLine)
    }

    i++
  }

  let cleaned = preprocessed.join('\n')

  // 2. Remove raw markdown horizontal dividers (---, ***, ___)
  cleaned = cleaned.replace(/^[ \t]*[-*_]{3,}[ \t]*$/gm, '')

  // 3. Normalize 3+ newlines to 2
  cleaned = cleaned.replace(/\n{3,}/g, '\n\n').trim()

  // 3. Process paragraphs and blocks
  const blocks = cleaned.split(/\n\n+/)
  const renderedBlocks: string[] = []

  for (const block of blocks) {
    const trimmed = block.trim()
    if (!trimmed) continue

    const lines = trimmed.split('\n')

    // Unordered bullet list
    const isBulletList = lines.every(l => /^[ \t]*[-*]\s+/.test(l))
    if (isBulletList) {
      const itemsHtml = lines.map(l => {
        const content = l.replace(/^[ \t]*[-*]\s+/, '')
        return `<li class="flex items-start gap-2 py-0.5"><span class="w-1.5 h-1.5 bg-amber-600 dark:bg-amber-500 shrink-0 mt-2"></span><span class="flex-1 font-medium">${inlineFormat(content)}</span></li>`
      }).join('')
      renderedBlocks.push(`<ul class="my-2 space-y-1">${itemsHtml}</ul>`)
      continue
    }

    // Ordered numeric list
    const isOrderedList = lines.every(l => /^[ \t]*\d+\.\s+/.test(l))
    if (isOrderedList) {
      const itemsHtml = lines.map(l => {
        const match = l.match(/^[ \t]*(\d+)\.\s+(.*)$/)
        const num = match ? match[1].padStart(2, '0') : '01'
        const content = match ? match[2] : l
        return `<li class="flex items-start gap-2 py-0.5"><span class="font-mono text-[10px] font-black px-1 py-0.2 bg-stone-200 dark:bg-stone-800 border border-stone-400 dark:border-stone-700 shrink-0 mt-0.5 text-stone-900 dark:text-stone-100">[${num}]</span><span class="flex-1 font-medium">${inlineFormat(content)}</span></li>`
      }).join('')
      renderedBlocks.push(`<ol class="my-2 space-y-1">${itemsHtml}</ol>`)
      continue
    }

    // Heading lines (e.g. ### Title)
    if (/^#{1,4}\s+/.test(trimmed)) {
      const headingText = trimmed.replace(/^#{1,4}\s+/, '')
      renderedBlocks.push(`<h4 class="font-mono font-black text-xs uppercase tracking-wider my-2 border-b pb-1 text-amber-700 dark:text-amber-400 border-stone-300 dark:border-stone-700">// ${inlineFormat(headingText)}</h4>`)
      continue
    }

    // Normal paragraph
    renderedBlocks.push(`<p class="mb-2 last:mb-0 leading-relaxed">${inlineFormat(trimmed.replace(/\n/g, '<br/>'))}</p>`)
  }

  return renderedBlocks.join('')
}

function handleWhatsAppClick() {
  emit('escalationAction', { type: 'whatsapp', contact: '+57 313 730 1501' })
}

function handleEmailClick() {
  emit('escalationAction', { type: 'email', contact: 'edig0rgudevia@gmail.com' })
}
</script>

<template>
  <div
    ref="messageEl"
    class="flex flex-col gap-1.5 w-full transition-all duration-300 opacity-0"
    :class="message.role === 'user' ? 'items-end' : 'items-start'"
  >
    <!-- Constructivist Message Container -->
    <div
      class="max-w-[92%] sm:max-w-[84%] p-4 sm:p-5 border-2 transition-all duration-200 relative group"
      :class="[
        message.role === 'user'
          ? isDark
            ? 'bg-linear-to-br from-amber-800 to-orange-900 border-amber-500 text-amber-50 shadow-[4px_4px_0px_0px_#78350f]'
            : 'bg-linear-to-br from-amber-600 to-orange-600 border-stone-900 text-white shadow-[4px_4px_0px_0px_#1c1917]'
          : isDark
            ? 'bg-stone-900 border-stone-700 text-stone-200 border-l-4 border-l-amber-500 shadow-[4px_4px_0px_0px_#0c0a09]'
            : 'bg-white border-stone-900 text-stone-950 border-l-4 border-l-amber-600 shadow-[4px_4px_0px_0px_#d97706]'
      ]"
    >
      <!-- Geometric Corner Accent -->
      <div
        class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 pointer-events-none"
        :class="message.role === 'user' ? 'border-amber-300' : 'border-amber-600'"
      ></div>

      <!-- Constructivist Header Stamp -->
      <div
        class="flex items-center justify-between gap-3 mb-2.5 pb-1.5 border-b"
        :class="message.role === 'user' ? 'border-white/20' : 'border-stone-300 dark:border-stone-800'"
      >
        <div class="flex items-center gap-2">
          <!-- Logo Reticle -->
          <div
            v-if="message.role === 'assistant'"
            class="w-5 h-5 border border-stone-900 dark:border-stone-600 bg-white flex items-center justify-center shrink-0 p-0.5 shadow-xs"
          >
            <img :src="logoImg" alt="Gastroteacher" class="w-full h-full object-cover" />
          </div>
          <!-- Role Technical Label -->
          <span
            class="font-mono text-[11px] font-black tracking-wider uppercase flex items-center gap-1.5"
            :class="message.role === 'user' ? 'text-amber-100' : isDark ? 'text-amber-400' : 'text-stone-900'"
          >
            {{ message.role === 'user' ? '// ' + labels.you.toUpperCase() : '// GT-SYS.ASISTENTE' }}
          </span>
        </div>

        <span
          class="font-mono text-[10px] font-bold tracking-tight"
          :class="message.role === 'user' ? 'text-amber-200' : isDark ? 'text-stone-400' : 'text-stone-600'"
        >
          {{ formatDisplayTime(message.timestamp) }}
        </span>
      </div>

      <!-- Human Escalation Hazard Block -->
      <div
        v-if="message.is_escalated"
        class="mb-3 p-3 border-2 border-rose-600 dark:border-rose-500 bg-rose-50 dark:bg-rose-950/40 text-rose-950 dark:text-rose-200 shadow-[3px_3px_0px_0px_#be123c]"
      >
        <div class="flex items-start gap-2.5">
          <div class="p-1 bg-rose-600 text-white shrink-0">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div class="flex-1">
            <h4 class="font-mono text-xs font-black uppercase tracking-wider text-rose-900 dark:text-rose-200">
              [ATENCIÓN] {{ labels.escalatedTitle }}
            </h4>
            <p class="text-xs mt-1 font-bold text-stone-900 dark:text-rose-100">
              {{ labels.escalatedDesc }}
            </p>
            <!-- Constructivist Action Buttons -->
            <div class="mt-2.5 flex flex-wrap gap-2">
              <a
                href="https://wa.me/573137301501?text=Hola%20Diego%2C%20quisiera%20asesor%C3%ADa%20sobre%20Gastroteacher"
                target="_blank"
                @click="handleWhatsAppClick"
                class="inline-flex items-center gap-1.5 px-3 py-1 font-mono text-xs font-black bg-emerald-600 text-white hover:bg-emerald-700 border border-stone-900 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 shadow-[2px_2px_0px_0px_#064e3b] cursor-pointer"
              >
                <span>{{ labels.whatsappBtn }}</span>
                <span class="text-[10px] font-mono text-emerald-100">[+57 313 730 1501]</span>
              </a>
              <a
                href="mailto:edig0rgudevia@gmail.com?subject=Consulta%20Asesoría%20Gastroteacher"
                @click="handleEmailClick"
                class="inline-flex items-center gap-1.5 px-3 py-1 font-mono text-xs font-black border border-stone-900 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 shadow-[2px_2px_0px_0px_#1c1917] cursor-pointer"
                :class="isDark ? 'bg-stone-800 text-stone-200 hover:bg-stone-700' : 'bg-white text-stone-900 hover:bg-stone-100'"
              >
                <span>{{ labels.emailBtn }}</span>
                <span class="text-[10px] font-mono text-stone-600 dark:text-stone-400">[edig0rgudevia@gmail.com]</span>
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Message Text Body -->
      <div
        class="text-sm font-sans tracking-normal leading-relaxed overflow-wrap-break-word select-text"
        v-html="formatContent(message.content)"
      ></div>

      <!-- Message Footer & Meta Badges -->
      <div
        v-if="message.role === 'assistant'"
        class="mt-3 pt-2 border-t flex flex-wrap items-center justify-between gap-2 text-[11px]"
        :class="isDark ? 'border-stone-800 text-stone-400' : 'border-stone-300 text-stone-600'"
      >
        <div class="flex items-center gap-2">
          <!-- Cache Indicator Badge -->
          <span
            v-if="message.cached"
            class="inline-flex items-center gap-1 px-1.5 py-0.5 border font-mono text-[9px] font-black uppercase tracking-wider bg-emerald-500/10 border-emerald-500/30 text-emerald-700 dark:text-emerald-400"
          >
            <span>⚡</span>
            <span>{{ labels.cachedBadge }}</span>
          </span>

          <!-- Latency & Tokens -->
          <span v-if="message.latency_ms" class="font-mono text-[10px]">
            {{ message.latency_ms }}ms
          </span>
          <span v-if="message.token_usage?.total_tokens" class="font-mono text-[10px]">
            • {{ message.token_usage.total_tokens }} tok
          </span>
        </div>

        <!-- Sources Drawer Toggle Button -->
        <button
          v-if="message.sources && message.sources.length > 0"
          type="button"
          @click="showSources = !showSources"
          class="font-mono text-[10px] font-bold text-amber-700 dark:text-amber-400 hover:underline cursor-pointer flex items-center gap-1"
        >
          <span>{{ showSources ? labels.hideSources : labels.viewSources }}</span>
          <span>({{ message.sources.length }})</span>
          <span>{{ showSources ? '▲' : '▼' }}</span>
        </button>
      </div>

      <!-- Sources Drawer (Constructivist Technical File) -->
      <div
        v-if="showSources && message.sources && message.sources.length > 0"
        class="mt-3 p-3 border-2 border-stone-800 dark:border-stone-700 bg-stone-100 dark:bg-stone-950 font-mono text-xs space-y-2 shadow-[2px_2px_0px_0px_#d97706]"
      >
        <div class="flex items-center justify-between border-b border-stone-300 dark:border-stone-800 pb-1">
          <span class="font-black uppercase tracking-wider text-[10px] text-amber-700 dark:text-amber-400">
            // {{ labels.officialDocs }}
          </span>
          <span class="text-[9px] text-stone-500 dark:text-stone-400">[CANONICAL_SOURCE]</span>
        </div>
        <div
          v-for="(source, idx) in message.sources"
          :key="idx"
          class="p-2 border border-stone-300 dark:border-stone-800 bg-white dark:bg-stone-900 space-y-1"
        >
          <div class="flex items-center justify-between text-[11px] font-bold">
            <span class="text-stone-900 dark:text-stone-200">#{{ idx + 1 }}. {{ source.title || source.source }}</span>
            <span class="text-amber-700 dark:text-amber-400 font-mono text-[10px]">
              rel: {{ (source.similarity_score * 100).toFixed(0) }}%
            </span>
          </div>
          <p class="text-[10px] text-stone-600 dark:text-stone-400 line-clamp-2 leading-tight">
            {{ source.excerpt }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
