<script setup lang="ts">
const emit = defineEmits<{
  (e: 'selectPrompt', prompt: string): void
}>()

const prompts = [
  {
    icon: '📅',
    title: 'Horarios de clases',
    prompt: '¿Cuáles son los horarios de clases disponibles los fines de semana y entre semana?'
  },
  {
    icon: '💰',
    title: 'Precios y descuentos',
    prompt: '¿Cuánto cuestan los programas de inglés y qué facilidades de pago o becas ofrecen?'
  },
  {
    icon: '📜',
    title: 'Certificaciones oficiales',
    prompt: '¿Qué certificaciones otorgan y tienen convenios para exámenes como TOEFL o IELTS?'
  },
  {
    icon: '📝',
    title: 'Proceso de matrícula',
    prompt: '¿Cómo es el proceso de inscripción y cuándo son las fechas de inicio de clases?'
  },
  {
    icon: '🚨',
    title: 'Probar escalamiento humano',
    prompt: '¿Cómo reparar el motor de una moto Yamaha y tramitan visas a Canadá?'
  }
]
</script>

<template>
  <div class="w-full">
    <div class="flex items-center gap-2 mb-2 text-xs font-semibold uppercase tracking-wider text-stone-500 dark:text-stone-400">
      <svg class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
      </svg>
      <span>Consultas Frecuentes Rápidas</span>
    </div>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="(p, idx) in prompts"
        :key="idx"
        type="button"
        @click="emit('selectPrompt', p.prompt)"
        class="group flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium backdrop-blur-md border transition-all duration-200 shadow-xs hover:scale-102 active:scale-98 text-left bg-white/70 hover:bg-amber-50/90 border-stone-200 hover:border-amber-400 text-stone-700 hover:text-amber-900 dark:bg-stone-800/60 dark:hover:bg-stone-800/90 dark:border-stone-700/80 dark:hover:border-amber-500/50 dark:text-stone-300 dark:hover:text-amber-200"
      >
        <span>{{ p.icon }}</span>
        <span>{{ p.title }}</span>
      </button>
    </div>
  </div>
</template>
