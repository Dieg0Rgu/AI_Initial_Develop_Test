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
    <div class="flex items-center gap-2 mb-2 font-mono text-[11px] font-black uppercase tracking-wider text-stone-900 dark:text-stone-300">
      <span class="w-2 h-2 bg-amber-600"></span>
      <span>// {{ labelTitle.toUpperCase() }} [ACCESO_DIRECTO]</span>
    </div>
    <div class="flex flex-wrap gap-2">
      <!-- 01 // Horarios -->
      <button
        type="button"
        @click="emit('selectPrompt', prompts.schedule.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 font-mono text-xs font-black border-2 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 text-left bg-white hover:bg-amber-50 border-stone-900 text-stone-950 dark:bg-stone-900 dark:hover:bg-stone-800 dark:border-stone-700 dark:text-stone-200 dark:hover:text-amber-300 cursor-pointer shadow-[2px_2px_0px_0px_#d97706]"
      >
        <span class="text-amber-600 dark:text-amber-400 font-mono text-[10px]">[01]</span>
        <span class="uppercase tracking-tight">{{ prompts.schedule.title }}</span>
      </button>

      <!-- 02 // Precios -->
      <button
        type="button"
        @click="emit('selectPrompt', prompts.pricing.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 font-mono text-xs font-black border-2 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 text-left bg-white hover:bg-amber-50 border-stone-900 text-stone-950 dark:bg-stone-900 dark:hover:bg-stone-800 dark:border-stone-700 dark:text-stone-200 dark:hover:text-amber-300 cursor-pointer shadow-[2px_2px_0px_0px_#d97706]"
      >
        <span class="text-amber-600 dark:text-amber-400 font-mono text-[10px]">[02]</span>
        <span class="uppercase tracking-tight">{{ prompts.pricing.title }}</span>
      </button>

      <!-- 03 // Certificaciones -->
      <button
        type="button"
        @click="emit('selectPrompt', prompts.certification.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 font-mono text-xs font-black border-2 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 text-left bg-white hover:bg-amber-50 border-stone-900 text-stone-950 dark:bg-stone-900 dark:hover:bg-stone-800 dark:border-stone-700 dark:text-stone-200 dark:hover:text-amber-300 cursor-pointer shadow-[2px_2px_0px_0px_#d97706]"
      >
        <span class="text-amber-600 dark:text-amber-400 font-mono text-[10px]">[03]</span>
        <span class="uppercase tracking-tight">{{ prompts.certification.title }}</span>
      </button>

      <!-- 04 // Inscripciones -->
      <button
        type="button"
        @click="emit('selectPrompt', prompts.enrollment.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 font-mono text-xs font-black border-2 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 text-left bg-white hover:bg-amber-50 border-stone-900 text-stone-950 dark:bg-stone-900 dark:hover:bg-stone-800 dark:border-stone-700 dark:text-stone-200 dark:hover:text-amber-300 cursor-pointer shadow-[2px_2px_0px_0px_#d97706]"
      >
        <span class="text-amber-600 dark:text-amber-400 font-mono text-[10px]">[04]</span>
        <span class="uppercase tracking-tight">{{ prompts.enrollment.title }}</span>
      </button>

      <!-- 05 // Asesor Humano -->
      <button
        type="button"
        @click="emit('selectPrompt', prompts.escalation.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 font-mono text-xs font-black border-2 transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 text-left bg-rose-50 hover:bg-rose-100 border-rose-600 text-rose-950 dark:bg-rose-950/40 dark:hover:bg-rose-950/60 dark:border-rose-500 dark:text-rose-200 cursor-pointer shadow-[2px_2px_0px_0px_#be123c]"
      >
        <span class="text-rose-600 dark:text-rose-400 font-mono text-[10px]">[05]</span>
        <span class="uppercase tracking-tight">{{ prompts.escalation.title }}</span>
      </button>
    </div>
  </div>
</template>
