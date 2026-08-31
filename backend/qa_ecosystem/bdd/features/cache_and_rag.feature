# language: es
Característica: Respuestas RAG y Aceleración por Caché
  Como estudiante interesado en Gastroteacher Academy
  Quiero consultar precios, programas y horarios rápidamente
  Para obtener información oficial de forma instantánea y confiable

  Escenario: Consulta de horarios consulta la base de conocimiento oficial
    Dado que el asistente de Gastroteacher está en línea
    Cuando el usuario envía la consulta "¿Cuáles son los horarios de clases disponibles los fines de semana?"
    Entonces la respuesta debe contener información oficial de horarios
    Y la respuesta debe incluir al menos una fuente documental oficial
    Y la bandera "is_escalated" debe ser falsa

  Escenario: Consulta repetida es respondida inmediatamente desde la memoria caché
    Dado que la consulta "¿Cuáles son los precios del curso de inglés general?" fue procesada previamente
    Cuando el usuario envía exactamente la misma consulta "¿Cuáles son los precios del curso de inglés general?"
    Entonces la respuesta debe indicar "cached" en verdadero
    Y la latencia de respuesta debe ser inferior a 25 milisegundos
