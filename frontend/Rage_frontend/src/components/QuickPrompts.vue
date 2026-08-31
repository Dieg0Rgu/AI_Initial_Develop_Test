<script setup lang="ts">
interface PromptItem {
  title: string
  prompt: string
}

defineProps<{
  labelTitle: string
  prompts: {
    schedule: PromptItem
    pricing: PromptItem
    certification: PromptItem
    enrollment: PromptItem
    escalation: PromptItem
  }
}>()

const emit = defineEmits<{
  (e: 'selectPrompt', prompt: string): void
}>()
</script>

<template>
  <div class="w-full">
    <div class="flex items-center gap-2 mb-2 text-xs font-bold uppercase tracking-wider text-stone-900 dark:text-stone-300">
      <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
      </svg>
      <span>{{ labelTitle }}</span>
    </div>
    <div class="flex flex-wrap gap-2">
      <!-- Schedule -->
      <button
        type="button"
        @click="emit('selectPrompt', prompts.schedule.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold backdrop-blur-md border transition-all duration-200 shadow-xs hover:scale-102 active:scale-98 text-left bg-white hover:bg-amber-50 border-stone-300 hover:border-amber-500 text-stone-950 hover:text-amber-950 dark:bg-stone-800/60 dark:hover:bg-stone-800/90 dark:border-stone-700/80 dark:hover:border-amber-500/50 dark:text-stone-200 dark:hover:text-amber-200 cursor-pointer"
      >
        <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <polyline points="12 6 12 12 16 14"/>
        </svg>
        <span>{{ prompts.schedule.title }}</span>
      </button>

      <!-- Pricing -->
      <button
        type="button"
        @click="emit('selectPrompt', prompts.pricing.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold backdrop-blur-md border transition-all duration-200 shadow-xs hover:scale-102 active:scale-98 text-left bg-white hover:bg-amber-50 border-stone-300 hover:border-amber-500 text-stone-950 hover:text-amber-950 dark:bg-stone-800/60 dark:hover:bg-stone-800/90 dark:border-stone-700/80 dark:hover:border-amber-500/50 dark:text-stone-200 dark:hover:text-amber-200 cursor-pointer"
      >
        <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="1" x2="12" y2="23"/>
          <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
        </svg>
        <span>{{ prompts.pricing.title }}</span>
      </button>

      <!-- Certification -->
      <button
        type="button"
        @click="emit('selectPrompt', prompts.certification.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold backdrop-blur-md border transition-all duration-200 shadow-xs hover:scale-102 active:scale-98 text-left bg-white hover:bg-amber-50 border-stone-300 hover:border-amber-500 text-stone-950 hover:text-amber-950 dark:bg-stone-800/60 dark:hover:bg-stone-800/90 dark:border-stone-700/80 dark:hover:border-amber-500/50 dark:text-stone-200 dark:hover:text-amber-200 cursor-pointer"
      >
        <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="8" r="7"/>
          <polyline points="8.21 13.89 7 23 12 20 17 23 15.79 13.88"/>
        </svg>
        <span>{{ prompts.certification.title }}</span>
      </button>

      <!-- Enrollment -->
      <button
        type="button"
        @click="emit('selectPrompt', prompts.enrollment.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold backdrop-blur-md border transition-all duration-200 shadow-xs hover:scale-102 active:scale-98 text-left bg-white hover:bg-amber-50 border-stone-300 hover:border-amber-500 text-stone-950 hover:text-amber-950 dark:bg-stone-800/60 dark:hover:bg-stone-800/90 dark:border-stone-700/80 dark:hover:border-amber-500/50 dark:text-stone-200 dark:hover:text-amber-200 cursor-pointer"
      >
        <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
          <polyline points="10 9 9 9 8 9"/>
        </svg>
        <span>{{ prompts.enrollment.title }}</span>
      </button>

      <!-- Escalation -->
      <button
        type="button"
        @click="emit('selectPrompt', prompts.escalation.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold backdrop-blur-md border transition-all duration-200 shadow-xs hover:scale-102 active:scale-98 text-left bg-white hover:bg-rose-50 border-stone-300 hover:border-rose-400 text-stone-950 hover:text-rose-950 dark:bg-stone-800/60 dark:hover:bg-stone-800/90 dark:border-stone-700/80 dark:hover:border-amber-500/50 dark:text-stone-200 dark:hover:text-amber-200 cursor-pointer"
      >
        <svg class="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="8.5" cy="7" r="4"/>
          <line x1="18" y1="8" x2="23" y2="13"/>
          <line x1="23" y1="8" x2="18" y2="13"/>
        </svg>
        <span>{{ prompts.escalation.title }}</span>
      </button>
    </div>
  </div>
</template>
