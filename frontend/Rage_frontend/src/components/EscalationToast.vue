<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { animate } from 'animejs'
import moment from 'moment'
import 'moment/locale/es'

const props = defineProps<{
  show: boolean
  type: 'whatsapp' | 'email' | 'auto_escalate'
  isDark: boolean
  lang: 'es' | 'en'
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const toastRef = ref<HTMLElement | null>(null)
const formattedTime = ref('')

function updateTime() {
  if (props.lang === 'es') {
    moment.locale('es')
    formattedTime.value = moment().format('D [de] MMMM [de] YYYY, h:mm:ss a')
  } else {
    moment.locale('en')
    formattedTime.value = moment().format('MMMM Do YYYY, h:mm:ss a')
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    updateTime()
    nextTick(() => {
      if (toastRef.value) {
        animate(toastRef.value, {
          translateY: [-40, 0],
          opacity: [0, 1],
          scale: [0.85, 1],
          duration: 650,
          ease: 'outElastic(1, .75)'
        })
      }
    })
  }
})

function handleClose() {
  if (toastRef.value) {
    animate(toastRef.value, {
      translateY: [0, -30],
      opacity: [1, 0],
      scale: [1, 0.9],
      duration: 350,
      ease: 'inQuad',
      onComplete: () => {
        emit('close')
      }
    })
  } else {
    emit('close')
  }
}
</script>

<template>
  <div
    v-if="show"
    ref="toastRef"
    class="fixed top-20 left-1/2 -translate-x-1/2 z-50 w-[92%] max-w-lg p-4 rounded-2xl shadow-2xl border backdrop-blur-2xl transition-colors select-none"
    :class="
      isDark
        ? 'bg-stone-900/95 border-amber-500/40 text-stone-100 shadow-black/60'
        : 'bg-white border-amber-500 text-stone-950 shadow-2xl'
    "
  >
    <div class="flex items-start gap-3">
      <!-- Icon badge -->
      <div
        class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 shadow-xs text-white font-bold"
        :class="
          type === 'whatsapp'
            ? 'bg-emerald-600'
            : type === 'email'
              ? 'bg-blue-600'
              : 'bg-amber-600'
        "
      >
        <svg v-if="type === 'whatsapp'" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
        </svg>
        <svg v-else-if="type === 'email'" class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
          <polyline points="22,6 12,13 2,6"/>
        </svg>
        <svg v-else class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      </div>

      <!-- Message text -->
      <div class="flex-1 text-xs">
        <div class="flex items-center justify-between gap-2 mb-0.5">
          <span class="font-black text-sm bg-linear-to-r from-amber-700 to-orange-700 bg-clip-text text-transparent">
            {{
              type === 'whatsapp'
                ? lang === 'es' ? 'Redirigiendo a WhatsApp Personal' : 'Redirecting to Personal WhatsApp'
                : type === 'email'
                  ? lang === 'es' ? 'Notificación de Correo Enviada' : 'Email Notification Sent'
                  : lang === 'es' ? 'Consulta Escalada a Asesor Humano' : 'Query Escalated to Human Counselor'
            }}
          </span>
          <button
            type="button"
            @click="handleClose"
            class="text-stone-500 hover:text-stone-950 dark:text-stone-400 dark:hover:text-stone-200 cursor-pointer p-0.5"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>

        <p class="text-stone-950 dark:text-stone-200 font-medium leading-snug">
          <template v-if="type === 'whatsapp'">
            {{ lang === 'es' ? 'Abriendo canal directo de WhatsApp al número' : 'Opening direct WhatsApp channel to' }}
            <b class="text-emerald-700 dark:text-emerald-400 font-black">+57 313 730 1501</b>.
          </template>
          <template v-else-if="type === 'email'">
            {{ lang === 'es' ? 'Tu solicitud ha sido registrada y enviada al correo personal' : 'Your request was registered and sent to email' }}
            <b class="text-blue-700 dark:text-blue-400 font-black">edig0rgudevia@gmail.com</b>.
          </template>
          <template v-else>
            {{ lang === 'es' ? 'Tu consulta requiere atención directa. Canales activos: WhatsApp ' : 'Your query requires human attention. Active channels: WhatsApp ' }}
            <b class="text-emerald-700 dark:text-emerald-400 font-black">3137301501</b> / <b class="text-blue-700 dark:text-blue-400 font-black">edig0rgudevia@gmail.com</b>.
          </template>
        </p>

        <!-- Moment.js Timestamp footer -->
        <div class="mt-2 pt-1.5 border-t border-stone-300 dark:border-stone-800/50 flex items-center gap-1.5 text-[10px] text-stone-700 dark:text-stone-400 font-mono font-bold">
          <svg class="w-3 h-3 text-amber-600 dark:text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>⏱️ {{ formattedTime }} (Moment.js)</span>
        </div>
      </div>
    </div>
  </div>
</template>
