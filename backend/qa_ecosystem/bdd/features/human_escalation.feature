# language: es
Característica: Escalamiento a Equipo Humano de Soporte
  Como usuario del asistente virtual de Gastroteacher
  Quiero que mis consultas fuera del alcance o especializadas sean escaladas
  Para recibir atención personalizada por parte de un asesor humano

  Escenario: Consulta no relacionada sobre visado y mecánica
    Dado que el asistente de Gastroteacher está en línea
    Cuando el usuario envía la consulta "¿Tramitan visas para Canadá y arreglan motos Yamaha?"
    Entonces la respuesta debe indicar escalamiento humano con bandera "is_escalated" en verdadero
    Y la respuesta debe incluir los canales oficiales de contacto de soporte
    Y la respuesta no debe provenir de la memoria caché

  Escenario: Solicitud directa de hablar con un asesor humano
    Dado que el asistente de Gastroteacher está en línea
    Cuando el usuario envía la consulta "Necesito comunicarme con un asesor humano urgente"
    Entonces la respuesta debe indicar escalamiento humano con bandera "is_escalated" en verdadero
    Y la respuesta debe incluir los canales oficiales de contacto de soporte
