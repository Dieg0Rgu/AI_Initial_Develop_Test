<script setup lang="ts">
import { ref } from 'vue'
import Swal from 'sweetalert2'
import { loginUser, registerUser } from '../services/api'

const props = defineProps<{
  isOpen: boolean
  isDark: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'authenticated', user: any): void
}>()

const activeTab = ref<'login' | 'register'>('login')
const isLoading = ref(false)
const errorMessage = ref<string | null>(null)

// Login form state
const loginId = ref('admin')
const loginPassword = ref('admin123')

// Register form state
const regFullName = ref('')
const regUsername = ref('')
const regEmail = ref('')
const regPassword = ref('')

async function handleLogin() {
  if (!loginId.value.trim() || !loginPassword.value) {
    errorMessage.value = 'Por favor ingresa tu usuario/correo y contraseña.'
    return
  }

  isLoading.value = true
  errorMessage.value = null

  try {
    const res = await loginUser(loginId.value.trim(), loginPassword.value)
    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: '¡Sesión Iniciada!',
      text: `Bienvenido(a), ${res.user.full_name || res.user.username}`,
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true,
      background: props.isDark ? '#1c1917' : '#ffffff',
      color: props.isDark ? '#f5f5f4' : '#1c1917',
      iconColor: '#10b981'
    })
    emit('authenticated', res.user)
    emit('close')
  } catch (err: any) {
    errorMessage.value = err.message || 'Error al iniciar sesión.'
  } finally {
    isLoading.value = false
  }
}

async function handleRegister() {
  if (!regFullName.value.trim() || !regUsername.value.trim() || !regEmail.value.trim() || !regPassword.value) {
    errorMessage.value = 'Por favor completa todos los campos del formulario.'
    return
  }

  if (regPassword.value.length < 6) {
    errorMessage.value = 'La contraseña debe tener al menos 6 caracteres.'
    return
  }

  isLoading.value = true
  errorMessage.value = null

  try {
    const res = await registerUser({
      full_name: regFullName.value.trim(),
      username: regUsername.value.trim(),
      email: regEmail.value.trim(),
      password: regPassword.value
    })

    Swal.fire({
      toast: true,
      position: 'top-end',
      icon: 'success',
      title: '¡Cuenta Creada!',
      text: `Usuario ${res.user.username} registrado con éxito.`,
      showConfirmButton: false,
      timer: 3500,
      timerProgressBar: true,
      background: props.isDark ? '#1c1917' : '#ffffff',
      color: props.isDark ? '#f5f5f4' : '#1c1917',
      iconColor: '#10b981'
    })
    emit('authenticated', res.user)
    emit('close')
  } catch (err: any) {
    errorMessage.value = err.message || 'Error al registrar la cuenta.'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md transition-opacity duration-300"
    @click.self="emit('close')"
  >
    <div
      class="w-full max-w-md rounded-3xl shadow-2xl border overflow-hidden flex flex-col transition-all transform scale-100"
      :class="isDark ? 'bg-stone-900 border-stone-800 text-stone-100' : 'bg-white border-stone-300 text-stone-950'"
    >
      <!-- Header -->
      <div
        class="px-6 py-5 border-b flex items-center justify-between"
        :class="isDark ? 'border-stone-800 bg-stone-900/90' : 'border-stone-200 bg-stone-50'"
      >
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-600 dark:text-amber-400">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div>
            <h2 class="text-base font-black tracking-tight text-stone-950 dark:text-stone-100">
              Acceso a Métricas y Analítica
            </h2>
            <p class="text-xs text-stone-600 dark:text-stone-400 font-medium">
              Inicia sesión o regístrate para visualizar el dashboard
            </p>
          </div>
        </div>

        <button
          type="button"
          @click="emit('close')"
          class="p-2 rounded-xl border transition-colors cursor-pointer hover:bg-stone-200 dark:hover:bg-stone-800"
          :class="isDark ? 'border-stone-700 text-stone-400' : 'border-stone-300 text-stone-700'"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="18" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Tab Switcher -->
      <div class="flex border-b" :class="isDark ? 'border-stone-800 bg-stone-950/40' : 'border-stone-200 bg-stone-100/50'">
        <button
          type="button"
          @click="activeTab = 'login'; errorMessage = null"
          class="flex-1 py-3 text-xs font-black transition-all border-b-2 cursor-pointer flex items-center justify-center gap-2"
          :class="activeTab === 'login'
            ? 'border-amber-600 text-amber-700 dark:text-amber-400 bg-amber-500/5'
            : 'border-transparent text-stone-500 hover:text-stone-800 dark:hover:text-stone-200'"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/>
            <polyline points="10 17 15 12 10 7"/>
            <line x1="15" y1="12" x2="3" y2="12"/>
          </svg>
          <span>Iniciar Sesión</span>
        </button>

        <button
          type="button"
          @click="activeTab = 'register'; errorMessage = null"
          class="flex-1 py-3 text-xs font-black transition-all border-b-2 cursor-pointer flex items-center justify-center gap-2"
          :class="activeTab === 'register'
            ? 'border-amber-600 text-amber-700 dark:text-amber-400 bg-amber-500/5'
            : 'border-transparent text-stone-500 hover:text-stone-800 dark:hover:text-stone-200'"
        >
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="8.5" cy="7" r="4"/>
            <line x1="20" y1="8" x2="20" y2="14"/>
            <line x1="23" y1="11" x2="17" y2="11"/>
          </svg>
          <span>Registrarse</span>
        </button>
      </div>

      <!-- Content -->
      <div class="p-6 space-y-4">
        <!-- Error Message Alert -->
        <div
          v-if="errorMessage"
          class="p-3 rounded-xl border flex items-center gap-2.5 bg-rose-500/10 border-rose-500/30 text-rose-800 dark:text-rose-300 text-xs font-semibold"
        >
          <svg class="w-4 h-4 shrink-0 text-rose-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- 1. LOGIN FORM -->
        <form v-if="activeTab === 'login'" @submit.prevent="handleLogin" class="space-y-3.5">
          <div>
            <label class="block text-xs font-black mb-1.5" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              Usuario o Correo Electrónico
            </label>
            <input
              v-model="loginId"
              type="text"
              required
              placeholder="ej. admin o correo@ejemplo.com"
              class="w-full px-3.5 py-2.5 rounded-xl text-xs font-medium border transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-950 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-white border-stone-300 text-stone-900 focus:border-amber-600'"
            />
          </div>

          <div>
            <label class="block text-xs font-black mb-1.5" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              Contraseña
            </label>
            <input
              v-model="loginPassword"
              type="password"
              required
              placeholder="••••••••"
              class="w-full px-3.5 py-2.5 rounded-xl text-xs font-medium border transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-950 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-white border-stone-300 text-stone-900 focus:border-amber-600'"
            />
          </div>

          <!-- Quick Tip with Default Admin Credentials -->
          <div
            class="p-2.5 rounded-xl border flex items-center justify-between text-[11px] font-bold"
            :class="isDark ? 'bg-amber-950/20 border-amber-800/40 text-amber-300' : 'bg-amber-50 border-amber-300 text-amber-950'"
          >
            <span>💡 Cuenta demo: <b>admin</b> / <b>admin123</b></span>
            <button
              type="button"
              @click="loginId = 'admin'; loginPassword = 'admin123'"
              class="text-[10px] underline cursor-pointer hover:opacity-80"
            >
              Autocompletar
            </button>
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-3 rounded-xl text-xs font-black text-white bg-linear-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 shadow-md shadow-amber-600/20 transition-all hover:scale-101 active:scale-99 disabled:opacity-50 cursor-pointer flex items-center justify-center gap-2"
          >
            <svg v-if="isLoading" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
              <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
            </svg>
            <span>{{ isLoading ? 'Verificando...' : 'Ingresar al Dashboard' }}</span>
          </button>
        </form>

        <!-- 2. REGISTER FORM -->
        <form v-else @submit.prevent="handleRegister" class="space-y-3">
          <div>
            <label class="block text-xs font-black mb-1" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              Nombre Completo
            </label>
            <input
              v-model="regFullName"
              type="text"
              required
              placeholder="ej. Chef Carlos Martínez"
              class="w-full px-3.5 py-2 rounded-xl text-xs font-medium border transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-950 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-white border-stone-300 text-stone-900 focus:border-amber-600'"
            />
          </div>

          <div>
            <label class="block text-xs font-black mb-1" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              Nombre de Usuario
            </label>
            <input
              v-model="regUsername"
              type="text"
              required
              placeholder="ej. chef_carlos"
              class="w-full px-3.5 py-2 rounded-xl text-xs font-medium border transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-950 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-white border-stone-300 text-stone-900 focus:border-amber-600'"
            />
          </div>

          <div>
            <label class="block text-xs font-black mb-1" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              Correo Electrónico
            </label>
            <input
              v-model="regEmail"
              type="email"
              required
              placeholder="carlos@gastroteacher.com"
              class="w-full px-3.5 py-2 rounded-xl text-xs font-medium border transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-950 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-white border-stone-300 text-stone-900 focus:border-amber-600'"
            />
          </div>

          <div>
            <label class="block text-xs font-black mb-1" :class="isDark ? 'text-stone-300' : 'text-stone-800'">
              Contraseña (mínimo 6 caracteres)
            </label>
            <input
              v-model="regPassword"
              type="password"
              required
              minlength="6"
              placeholder="••••••••"
              class="w-full px-3.5 py-2 rounded-xl text-xs font-medium border transition-colors outline-hidden"
              :class="isDark ? 'bg-stone-950 border-stone-700 text-stone-100 focus:border-amber-500' : 'bg-white border-stone-300 text-stone-900 focus:border-amber-600'"
            />
          </div>

          <button
            type="submit"
            :disabled="isLoading"
            class="w-full py-3 mt-1 rounded-xl text-xs font-black text-white bg-linear-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 shadow-md shadow-amber-600/20 transition-all hover:scale-101 active:scale-99 disabled:opacity-50 cursor-pointer flex items-center justify-center gap-2"
          >
            <svg v-if="isLoading" class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10" stroke-opacity="0.25"/>
              <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"/>
            </svg>
            <span>{{ isLoading ? 'Creando cuenta...' : 'Crear Cuenta y Continuar' }}</span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

