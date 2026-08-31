from behave import given, when, then

@given('que el asistente de Gastroteacher está en línea')
def step_assistant_online(context):
    res = context.client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") in ["healthy", "ok", "operational"]

@given('que la consulta "{query}" fue procesada previamente')
def step_query_preprocessed(context, query):
    res = context.client.post("/api/chat", json={
        "message": query,
        "session_id": "bdd_session_test",
        "bypass_cache": False,
        "language": "es"
    })
    assert res.status_code == 200

@when('el usuario envía la consulta "{query}"')
def step_user_sends_query(context, query):
    res = context.client.post("/api/chat", json={
        "message": query,
        "session_id": "bdd_session_test",
        "bypass_cache": False,
        "language": "es"
    })
    assert res.status_code == 200
    context.last_response = res
    context.last_json = res.json()

@when('el usuario envía exactamente la misma consulta "{query}"')
def step_user_sends_same_query(context, query):
    res = context.client.post("/api/chat", json={
        "message": query,
        "session_id": "bdd_session_test",
        "bypass_cache": False,
        "language": "es"
    })
    assert res.status_code == 200
    context.last_response = res
    context.last_json = res.json()

@then('la respuesta debe indicar escalamiento humano con bandera "{flag}" en verdadero')
def step_check_escalated_true(context, flag):
    assert context.last_json.get(flag) is True, f"Expected {flag} to be True, got {context.last_json.get(flag)}"

@then('la respuesta debe incluir los canales oficiales de contacto de soporte')
def step_check_support_channels(context):
    resp_text = context.last_json.get("response", "")
    assert "WhatsApp" in resp_text or "Correo" in resp_text or "soporte" in resp_text or "+57" in resp_text

@then('la respuesta no debe provenir de la memoria caché')
def step_check_not_cached(context):
    assert context.last_json.get("cached") is False

@then('la respuesta debe proveer el número de WhatsApp de soporte')
def step_check_whatsapp_provided(context):
    resp_text = context.last_json.get("response", "")
    assert "+57" in resp_text or "WhatsApp" in resp_text

@then('la respuesta debe contener información oficial de horarios')
def step_check_schedule_info(context):
    resp_text = context.last_json.get("response", "")
    assert any(term in resp_text.lower() for term in ["horario", "mañana", "tarde", "noche", "sabado", "sábado", "fin de semana"])

@then('la respuesta debe incluir al menos una fuente documental oficial')
def step_check_sources_present(context):
    sources = context.last_json.get("sources", [])
    assert len(sources) >= 1, f"Expected at least 1 source document, got {len(sources)}"

@then('la bandera "{flag}" debe ser falsa')
def step_check_flag_false(context, flag):
    assert context.last_json.get(flag) is False, f"Expected {flag} to be False, got {context.last_json.get(flag)}"

@then('la respuesta debe indicar "{flag}" en verdadero')
def step_check_flag_true(context, flag):
    assert context.last_json.get(flag) is True, f"Expected {flag} to be True, got {context.last_json.get(flag)}"

@then('la latencia de respuesta debe ser inferior a {max_ms:d} milisegundos')
def step_check_latency_ms(context, max_ms):
    latency = context.last_json.get("latency_ms", 1000)
    assert latency < max_ms, f"Expected latency < {max_ms} ms, got {latency} ms"
