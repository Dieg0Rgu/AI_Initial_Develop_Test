# ============================================================
# Gastroteacher Frontend — Dockerfile multietapa
# Etapa 1: Build de la aplicación Vue 3 + TypeScript (Vite)
# Etapa 2: Servicio estático con Nginx + proxy inverso hacia el backend
# ============================================================

# ---- Etapa 1: Build ----
FROM node:20-alpine AS build

WORKDIR /app

# Instalar dependencias (usa package-lock.json para builds reproducibles)
COPY package.json package-lock.json ./
RUN npm ci

# Copiar el código fuente y compilar
COPY . .
RUN npm run build

# ---- Etapa 2: Servidor Nginx ----
FROM nginx:1.27-alpine

# Configuración: estáticos + proxy /api -> backend:8000
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Artefactos compilados
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null 2>&1 || exit 1

CMD ["nginx", "-g", "daemon off;"]