export type Language = 'es' | 'en'

export const translations = {
  es: {
    // Navbar
    subtitle: 'Academia de Idiomas & Gastronomía',
    statusOnline: 'Sistema RAG Conectado',
    statusOffline: 'Servidor Desconectado',
    metricsBtn: 'Métricas',
    exportPdfBtn: 'Exportar PDF',
    exportingPdf: 'Generando...',
    themeLight: 'Cambiar a modo claro',
    themeDark: 'Cambiar a modo oscuro',

    // Export Modal
    exportModalTitle: 'Exportar Documentos & Conversación en PDF',
    exportModalSubtitle: 'Genera reportes oficiales corporativos en formato PDF con diseño institucional',
    exportChatTitle: 'Exportar Conversación Actual',
    exportChatDesc: 'Descarga un archivo PDF con la transcripción completa de los mensajes, métricas y fuentes consultadas.',
    exportChatAction: 'Descargar Chat en PDF',
    exportDocsTitle: 'Descargar Documentos Oficiales del Negocio',
    exportDocsDesc: 'Accede a los documentos originales de la academia en PDF corporativo:',
    exportSuccessAlertTitle: '¡PDF Generado con Éxito!',
    exportSuccessAlertText: 'Tu archivo PDF ha sido compilado y la descarga ha comenzado.',

    // Quick Prompts
    frequentQuestions: 'Consultas Frecuentes',
    prompts: {
      schedule: {
        title: 'Horarios y Jornadas',
        prompt: '¿Cuáles son los horarios de clases disponibles los fines de semana y entre semana?'
      },
      pricing: {
        title: 'Precios y Financiación',
        prompt: '¿Cuánto cuestan los programas de inglés y qué facilidades de pago o becas ofrecen?'
      },
      certification: {
        title: 'Certificaciones Oficiales',
        prompt: '¿Qué certificaciones otorgan y tienen convenios para exámenes como TOEFL o IELTS?'
      },
      enrollment: {
        title: 'Proceso de Matrícula',
        prompt: '¿Cómo es el proceso de inscripción y cuándo son las fechas de inicio de clases?'
      },
      escalation: {
        title: 'Prueba de Escalamiento',
        prompt: '¿Cómo reparar el motor de una moto Yamaha y tramitan visas a Canadá?'
      }
    },

    // Chat
    you: 'Tú',
    assistant: 'Gastroteacher Assistant',
    welcomeMessage: 'Bienvenido al Asistente Virtual de **Gastroteacher Academy**.\n\nEstoy capacitado para responder consultas institucionales sobre nuestros programas de formación en inglés general y gastronómico, horarios, inversión y formas de pago, modalidades de estudio, certificaciones internacionales y proceso de admisión.\n\n¿En qué temática académica o comercial requieres orientación?',
    welcomeReset: 'Sesión reiniciada. ¿Qué información sobre Gastroteacher deseas consultar?',
    inputPlaceholder: 'Escribe tu consulta sobre horarios, precios, programas, certificaciones...',
    loadingText: 'Consultando base de conocimiento oficial & procesando respuesta...',
    clearChatTitle: 'Limpiar conversación',
    clearChatConfirm: '¿Deseas reiniciar la sesión de consulta?',
    noCache: 'Sin Caché',
    noCacheTitle: 'Forzar respuesta fresca omitiendo la memoria caché',
    sendBtn: 'Enviar',
    connectionError: 'Aviso del sistema: No se pudo establecer conexión con el servidor API.',

    // Escalation & Sources
    escalatedTitle: 'Escalado al Equipo Humano de Soporte',
    escalatedDesc: 'Esta consulta requiere atención humana o se encuentra fuera del alcance de los documentos oficiales.',
    whatsappBtn: 'WhatsApp Directo',
    emailBtn: 'Enviar Correo',
    cachedBadge: 'En Caché',
    viewSources: 'Ver {count} fuentes RAG',
    hideSources: 'Ocultar fuentes',
    officialDocs: 'Documentos Oficiales Consultados:',

    // Metrics Modal & SweetAlerts
    metricsTitle: 'Panel de Métricas & Rendimiento',
    metricsSubtitle: 'Analítica de consultas, ahorro por caché y tasa de escalamiento',
    loadingMetrics: 'Cargando métricas en tiempo real...',
    totalQueries: 'Total Consultas',
    resolvedByAI: 'Resueltas por IA',
    humanEscalation: 'Escalamiento Humano',
    cacheHits: 'Aciertos de Caché',
    tokenSectionTitle: 'Consumo de Tokens y Ahorro Estimado',
    totalTokens: 'Total Tokens Procesados:',
    savedTokens: 'Tokens Ahorrados (Caché):',
    localCost: 'Costo en Ollama Local:',
    freeLocal: '$0.00 COP (100% Local)',
    avgLatency: 'Latencia Promedio:',
    cacheSize: 'Tamaño Caché en Memoria:',
    uptime: 'Tiempo de Actividad:',
    resetMetricsBtn: 'Reiniciar Métricas',
    resettingBtn: 'Reiniciando...',
    resetConfirm: '¿Estás seguro de que deseas reiniciar los contadores de métricas y caché?',
    closeBtn: 'Cerrar',

    // SweetAlerts for Metrics Reset
    sweetAlertWarningTitle: '¿Reiniciar todas las métricas?',
    sweetAlertWarningText: 'Esta acción restablecerá a cero las estadísticas de consultas, contadores de tokens y la memoria caché.',
    sweetAlertConfirmBtn: 'Sí, reiniciar métricas',
    sweetAlertCancelBtn: 'Cancelar',
    sweetAlertSuccessTitle: '¡Métricas Reiniciadas!',
    sweetAlertSuccessText: 'Los contadores de rendimiento y la memoria caché han vuelto a cero con éxito.',
    sweetAlertOkBtn: 'Entendido'
  },
  en: {
    // Navbar
    subtitle: 'Language & Gastronomy Academy',
    statusOnline: 'RAG System Connected',
    statusOffline: 'Server Disconnected',
    metricsBtn: 'Metrics',
    exportPdfBtn: 'Export PDF',
    exportingPdf: 'Generating...',
    themeLight: 'Switch to light mode',
    themeDark: 'Switch to dark mode',

    // Export Modal
    exportModalTitle: 'Export Documents & Chat Transcript in PDF',
    exportModalSubtitle: 'Generate corporate official PDF reports with institutional branding',
    exportChatTitle: 'Export Current Conversation',
    exportChatDesc: 'Download a PDF file with complete message history, response metrics, and cited sources.',
    exportChatAction: 'Download Chat PDF',
    exportDocsTitle: 'Download Official Business Documents',
    exportDocsDesc: 'Access original academy documents in corporate PDF format:',
    exportSuccessAlertTitle: 'PDF Generated Successfully!',
    exportSuccessAlertText: 'Your PDF report has been compiled and the download has started.',

    // Quick Prompts
    frequentQuestions: 'Frequently Asked Questions',
    prompts: {
      schedule: {
        title: 'Schedules & Shifts',
        prompt: 'What class schedules are available on weekends and weekdays?'
      },
      pricing: {
        title: 'Pricing & Financing',
        prompt: 'How much do the English programs cost and what payment plans or scholarships do you offer?'
      },
      certification: {
        title: 'Official Certifications',
        prompt: 'What certifications do you award and do you have partnerships for TOEFL or IELTS exams?'
      },
      enrollment: {
        title: 'Enrollment Process',
        prompt: 'What is the enrollment process and when are the next class start dates?'
      },
      escalation: {
        title: 'Escalation Test',
        prompt: 'How to fix a Yamaha motorcycle engine and do you process Canadian visas?'
      }
    },

    // Chat
    you: 'You',
    assistant: 'Gastroteacher Assistant',
    welcomeMessage: 'Welcome to the **Gastroteacher Academy** Virtual Assistant.\n\nI am trained to answer institutional inquiries about our general and culinary English training programs, flexible schedules, tuition and payment options in COP, study modalities, international certifications, and the admissions process.\n\nHow can I help you today?',
    welcomeReset: 'Conversation reset. What information about Gastroteacher would you like to ask?',
    inputPlaceholder: 'Ask about schedules, prices, programs, certifications...',
    loadingText: 'Querying official knowledge base & synthesizing response...',
    clearChatTitle: 'Clear conversation',
    clearChatConfirm: 'Are you sure you want to reset this conversation?',
    noCache: 'No Cache',
    noCacheTitle: 'Bypass cache and force fresh generation',
    sendBtn: 'Send',
    connectionError: 'System notice: Unable to connect to the API server.',

    // Escalation & Sources
    escalatedTitle: 'Escalated to Human Support Team',
    escalatedDesc: 'This inquiry requires human assistance or falls outside the scope of official documents.',
    whatsappBtn: 'Direct WhatsApp',
    emailBtn: 'Send Email',
    cachedBadge: 'Cached',
    viewSources: 'View {count} RAG sources',
    hideSources: 'Hide sources',
    officialDocs: 'Official Consulted Documents:',

    // Metrics Modal & SweetAlerts
    metricsTitle: 'Performance & Metrics Dashboard',
    metricsSubtitle: 'Analytics on queries, cache savings, and escalation rate',
    loadingMetrics: 'Loading real-time metrics...',
    totalQueries: 'Total Queries',
    resolvedByAI: 'Resolved by AI',
    humanEscalation: 'Human Escalation',
    cacheHits: 'Cache Hits',
    tokenSectionTitle: 'Token Usage & Estimated Savings',
    totalTokens: 'Total Tokens Processed:',
    savedTokens: 'Tokens Saved (Cache):',
    localCost: 'Local Ollama Cost:',
    freeLocal: '$0.00 USD (100% Local)',
    avgLatency: 'Average Latency:',
    cacheSize: 'In-Memory Cache Size:',
    uptime: 'Uptime:',
    resetMetricsBtn: 'Reset Metrics',
    resettingBtn: 'Resetting...',
    resetConfirm: 'Are you sure you want to reset all metrics and cache?',
    closeBtn: 'Close',

    // SweetAlerts for Metrics Reset
    sweetAlertWarningTitle: 'Reset all metrics?',
    sweetAlertWarningText: 'This action will clear all query statistics, token counters, and in-memory cache.',
    sweetAlertConfirmBtn: 'Yes, reset metrics',
    sweetAlertCancelBtn: 'Cancel',
    sweetAlertSuccessTitle: 'Metrics Reset Successfully!',
    sweetAlertSuccessText: 'Performance analytics and in-memory cache have been reset to zero.',
    sweetAlertOkBtn: 'Got it'
  }
}
