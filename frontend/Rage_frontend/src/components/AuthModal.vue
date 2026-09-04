<script setup lang="ts">
import { ref } from 'vue'
import Swal from 'sweetalert2'
import { loginUser, registerUser } from '../services/api'

defineProps<{
  isOpen: boolean
  isDark: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'authenticated', user: any): void
}>()

const activeTab = ref<'login' | 'register'>('login')
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)

// Login form
const loginId = ref('')
const loginPassword = ref('')

// Register form
const regUsername = ref('')
const regFullName = ref('')
const regEmail = ref('')
const regPassword = ref('')

async function handleLogin() {
  errorMessage.value = null
  if (!loginId.value.trim() || !loginPassword.value) {
    errorMessage.value = 'Por favor completa todos los campos requeridos.'
    return
  }

  isSubmitting.value = true
  try {
    const data = await loginUser(loginId.value.trim(), loginPassword.value)
    emit('authenticated', data.user)
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: 'Acceso Concedido',
      text: `Bienvenido, ${data.user.full_name || data.user.username}.`,
      showConfirmButton: false,
      timer: 3000,
      background: '#1c1917',
      color: '#f5f5f4',
      iconColor: '#10b981'
    })
  } catch (err: any) {
    errorMessage.value = err.message || 'Credenciales incorrectas o error en el servidor.'
  } finally {
    isSubmitting.value = false
  }
}

async function handleRegister() {
  errorMessage.value = null
  if (!regUsername.value.trim() || !regFullName.value.trim() || !regEmail.value.trim() || !regPassword.value) {
    errorMessage.value = 'Por favor completa todos los campos de registro.'
    return
  }

  if (regPassword.value.length < 6) {
    errorMessage.value = 'La contraseña debe tener al menos 6 caracteres.'
    return
  }

  isSubmitting.value = true
  try {
    const data = await registerUser({
      username: regUsername.value.trim(),
      full_name: regFullName.value.trim(),
      email: regEmail.value.trim(),
      password: regPassword.value
    })
    emit('authenticated', data.user)
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: 'Registro Exitoso',
      text: `Cuenta creada correctamente para ${data.user.username}.`,
      showConfirmButton: false,
      timer: 3000,
      background: '#1c1917',
      color: '#f5f5f4',
      iconColor: '#10b981'
    })
  } catch (err: any) {
    errorMessage.value = err.message || 'No se pudo completar el registro. Verifica los datos.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-stone-950/70 backdrop-blur-xs transition-opacity"
    @click.self="emit('close')"
  >
    <div
      class="w-full max-w-md border-2 transition-all duration-200 relative overflow-hidden"
      :class="isDark ? 'bg-stone-950 border-stone-700 text-stone-100 shadow-[8px_8px_0px_0px_#d97706]' : 'bg-white border-stone-900 text-stone-950 shadow-[8px_8px_0px_0px_#1c1917]'"
    >
      <!-- Corner Marks -->
      <div class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-amber-600 pointer-events-none"></div>
      <div class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-amber-600 pointer-events-none"></div>

      <!-- Modal Header -->
      <div
        class="flex items-center justify-between p-4 border-b-2"
        :class="isDark ? 'border-stone-800 bg-stone-900' : 'border-stone-900 bg-stone-100'"
      >
        <div class="flex items-center gap-2.5">
          <div class="w-7 h-7 border-2 border-stone-900 dark:border-amber-500 bg-amber-500/10 text-amber-700 dark:text-amber-400 flex items-center justify-center font-mono font-black text-xs">
            SEC
          </div>
          <div>
            <h3 class="font-black text-sm uppercase tracking-tight font-mono text-stone-950 dark:text-stone-100">
              // CONTROL DE ACCESO
            </h3>
            <p class="font-mono text-[10px] text-stone-600 dark:text-stone-400">
              Identificación para panel analítico
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="emit('close')"
          class="p-1.5 border-2 border-stone-900 dark:border-stone-700 text-stone-700 hover:text-stone-950 dark:text-stone-400 dark:hover:text-stone-200 transition-colors cursor-pointer"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="18" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Tab Switcher -->
      <div class="flex border-b-2" :class="isDark ? 'border-stone-800 bg-stone-900' : 'border-stone-900 bg-stone-50'">
        <button
          type="button"
          @click="activeTab = 'login'; errorMessage = null"
          class="flex-1 py-2.5 text-xs font-mono font-black uppercase transition-all border-b-2 cursor-pointer flex items-center justify-center gap-1.5"
          :class="activeTab === 'login'
            ? 'border-amber-600 text-amber-700 dark:text-amber-400 bg-amber-500/10'
            : 'border-transparent text-stone-500 hover:text-stone-900 dark:hover:text-stone-200'"
        >
          <span>[01] INICIAR SESIÓN</span>
        </button>

        <button
          type="button"
          @click="activeTab = 'register'; errorMessage = null"
          class="flex-1 py-2.5 text-xs font-mono font-black uppercase transition-all border-b-2 cursor-pointer flex items-center justify-center gap-1.5"
          :class="activeTab === 'register'
            ? 'border-amber-600 text-amber-700 dark:text-amber-400 bg-amber-500/10'
            : 'border-transparent text-stone-500 hover:text-stone-900 dark:hover:text-stone-200'"
        >
          <span>[02] REGISTRARSE</span>
        </button>
      </div>

      <!-- Content -->
      <div class="p-5 space-y-3.5">
        <!-- Error Message Alert -->
        <div
          v-if="errorMessage"
          class="p-2.5 border-2 border-rose-600 bg-rose-50 dark:bg-rose-950/40 text-rose-950 dark:text-rose-200 text-xs font-bold font-mono"
        >
          <span>[ERR] {{ errorMessage }}</span>
        </div>

        <!-- 1. LOGIN FORM -->
        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="space-y-3">
          <div>
            <label class="block text-[11px] font-mono font-black uppercase mb-1" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              // Usuario o Correo
            </label>
            <input
              v-model="loginId"
              type="text"
              required
              placeholder="admin o correo@ejemplo.com"
              class="w-full px-3 py-2 text-xs font-mono border-2 transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-900 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-stone-50 border-stone-900 text-stone-950 focus:border-amber-600'"
            />
          </div>

          <div>
            <label class="block text-[11px] font-mono font-black uppercase mb-1" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              // Contraseña
            </label>
            <input
              v-model="loginPassword"
              type="password"
              required
              placeholder="••••••••"
              class="w-full px-3 py-2 text-xs font-mono border-2 transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-900 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-stone-50 border-stone-900 text-stone-950 focus:border-amber-600'"
            />
          </div>

          <button
            type="submit"
            :disabled="isSubmitting"
            class="w-full mt-2 py-2.5 font-mono text-xs font-black uppercase tracking-wider border-2 border-stone-900 bg-amber-600 hover:bg-amber-500 text-white transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 disabled:opacity-50 cursor-pointer shadow-[3px_3px_0px_0px_#1c1917] dark:shadow-[3px_3px_0px_0px_#f59e0b]"
          >
            {{ isSubmitting ? 'VERIFICANDO...' : 'INGRESAR AL SISTEMA' }}
          </button>
        </form>

        <!-- 2. REGISTER FORM -->
        <form v-else @submit.prevent="handleRegister" class="space-y-2.5">
          <div>
            <label class="block text-[11px] font-mono font-black uppercase mb-0.5" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              // Nombre de Usuario
            </label>
            <input
              v-model="regUsername"
              type="text"
              required
              placeholder="ej. chef_diego"
              class="w-full px-3 py-1.5 text-xs font-mono border-2 transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-900 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-stone-50 border-stone-900 text-stone-950 focus:border-amber-600'"
            />
          </div>

          <div>
            <label class="block text-[11px] font-mono font-black uppercase mb-0.5" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              // Nombre Completo
            </label>
            <input
              v-model="regFullName"
              type="text"
              required
              placeholder="ej. Diego Rodríguez"
              class="w-full px-3 py-1.5 text-xs font-mono border-2 transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-900 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-stone-50 border-stone-900 text-stone-950 focus:border-amber-600'"
            />
          </div>

          <div>
            <label class="block text-[11px] font-mono font-black uppercase mb-0.5" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              // Correo Institucional
            </label>
            <input
              v-model="regEmail"
              type="email"
              required
              placeholder="chef@gastroteacher.edu.co"
              class="w-full px-3 py-1.5 text-xs font-mono border-2 transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-900 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-stone-50 border-stone-900 text-stone-950 focus:border-amber-600'"
            />
          </div>

          <div>
            <label class="block text-[11px] font-mono font-black uppercase mb-0.5" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              // Contraseña
            </label>
            <input
              v-model="regPassword"
              type="password"
              required
              placeholder="Mínimo 6 caracteres"
              class="w-full px-3 py-1.5 text-xs font-mono border-2 transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-900 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-stone-50 border-stone-900 text-stone-950 focus:border-amber-600'"
            />
          </div>

          <button
            type="submit"
            :disabled="isSubmitting"
            class="w-full mt-2 py-2.5 font-mono text-xs font-black uppercase tracking-wider border-2 border-stone-900 bg-amber-600 hover:bg-amber-500 text-white transition-transform hover:-translate-x-0.5 hover:-translate-y-0.5 active:translate-x-0 active:translate-y-0 disabled:opacity-50 cursor-pointer shadow-[3px_3px_0px_0px_#1c1917] dark:shadow-[3px_3px_0px_0px_#f59e0b]"
          >
            {{ isSubmitting ? 'REGISTRANDO...' : 'REGISTRAR USUARIO' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
