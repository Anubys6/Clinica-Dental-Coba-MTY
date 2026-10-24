# -*- coding: utf-8 -*-
"""
Módulo de Integración Oficial WhatsApp Business Cloud API & Motor de IA Conversacional
Clínica Dental Cobá Monterrey & Guadalupe

Funciones:
1. Verificación oficial de Webhooks de Meta (GET /webhook/whatsapp)
2. Recepción y parseo de mensajes entrantes de Meta (POST /webhook/whatsapp)
3. Agente Conversacional Genuino con Memoria de Sesión (Gemini 3.8 Flash)
4. Extracción automática de campos clínicos y sincronización con la base de datos (crm_leads_coba.json/csv)
5. Envío de respuestas salientes vía Meta Graph API v20.0
6. Simulador interactivo para pruebas locales y desde el panel de control
"""

import os
import re
import csv
import json
import time
import uuid
import random
import urllib.request
import urllib.parse
from datetime import datetime

# Intentar cargar cliente oficial de Gemini
try:
    from google import genai
    gemini_client = genai.Client()
    HAS_GEMINI = True
except Exception as e:
    gemini_client = None
    HAS_GEMINI = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTO_DIR = os.path.join(BASE_DIR, 'automation')
JSON_CRM_PATH = os.path.join(AUTO_DIR, 'crm_leads_coba.json')
CSV_CRM_PATH = os.path.join(AUTO_DIR, 'crm_leads_coba.csv')
CONFIG_PATH = os.path.join(AUTO_DIR, 'whatsapp_config.json')

# Variables de entorno o valores de configuración por defecto
DEFAULT_CONFIG = {
    "WHATSAPP_TOKEN": os.environ.get("WHATSAPP_TOKEN", ""),
    "PHONE_NUMBER_ID": os.environ.get("PHONE_NUMBER_ID", "108492019384910"),
    "WABA_ID": os.environ.get("WABA_ID", "938472910492810"),
    "VERIFY_TOKEN": os.environ.get("WHATSAPP_VERIFY_TOKEN", "coba_dental_secure_token_2026"),
    "BUSINESS_PHONE": "528118483941",
    "CLINIC_NAME": "Clínica Dental Cobá",
    "MODEL_NAME": "gemini-3.8-flash"
}

def load_whatsapp_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                cfg = DEFAULT_CONFIG.copy()
                cfg.update(saved)
                return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_whatsapp_config(new_config):
    cfg = load_whatsapp_config()
    cfg.update(new_config)
    os.makedirs(AUTO_DIR, exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    return cfg

# Memoria de conversación por teléfono en RAM
# sender_phone -> { "messages": [...], "extracted_data": {...}, "last_active": timestamp }
CONVERSATION_SESSIONS = {}

CLINICAL_SYSTEM_PROMPT = """Eres el Asistente Clínico Inteligente Oficial de Clínica Dental Cobá (Monterrey Centro y Guadalupe Centro).
Tu objetivo es comunicarte con los pacientes de manera cálida, genuina, profesional y empática por WhatsApp.

REGLAS DE ATENCIÓN:
1. Comunícate en español mexicano educado y amable ("¡Hola!", "Con mucho gusto", "Estamos para servirte").
2. Brinda respuestas claras sobre procedimientos, promociones y cuidados dentales:
   - Promo Brackets Metálicos: $1,999 MXN pago inicial con limpieza ultrasónica gratis.
   - Coronas de Zirconia Monolítica: Alta estética alemana, libres de metal, garantizadas.
   - Diseño de Sonrisa y Blanqueamiento Láser: Tecnología digital 3D.
   - Endodoncia Microscópica: Tratamiento indoloro de conductos para salvar piezas con dolor.
   - Implantes Dentales de Titanio: Reemplazo fijo de piezas perdidas.
   - Sucursales: Monterrey Centro (Jerónimo Treviño #1111 Pte., estacionamiento privado) y Guadalupe Centro (Benito Juárez #825, Local D).
   - Horarios: Lunes a Viernes de 9:00 AM a 6:00 PM | Sábados de 9:00 AM a 5:00 PM.
3. OBJETIVO DE CAPTACIÓN:
   De forma natural y sin parecer un interrogatorio robótico, recopila los datos clave del paciente:
   - Nombre completo
   - Tratamiento de interés
   - Sucursal preferida (MTY o Guadalupe)
   - Si tiene dolor agudo o urgencia
   - Fecha y horario preferido
4. FORMATO DE RESPUESTA:
   Escribe tu respuesta conversacional normal para el paciente.
   AL FINAL DE TU MENSAJE, si el paciente ha proporcionado algún dato nuevo relevante, agrega un bloque JSON delimitado exactamente por ```json_lead ... ``` con esta estructura:
   ```json_lead
   {
     "nombre": "Nombre si lo dio o null",
     "sucursal": "Monterrey Centro o Guadalupe Centro o null",
     "tratamiento": "Tratamiento inferido o null",
     "urgencia": "Sin dolor / Dolor moderado / Dolor agudo / null",
     "fecha_cita": "YYYY-MM-DD o null",
     "hora_cita": "HH:MM AM/PM o null",
     "intencion": "cotizar" o "agendar" o "duda" o "urgencia",
     "datos_completos": true o false
   }
   ```
   No menciones la palabra JSON en tu texto dirigido al paciente.
"""

def verify_meta_webhook(hub_mode, hub_verify_token, hub_challenge):
    """Valida el handshake GET que hace Meta al registrar el Webhook"""
    cfg = load_whatsapp_config()
    expected_token = cfg.get("VERIFY_TOKEN", "coba_dental_secure_token_2026")
    if hub_mode == 'subscribe' and hub_verify_token == expected_token:
        return hub_challenge
    return None

def extract_meta_message(data):
    """Extrae el mensaje del payload oficial de WhatsApp Cloud API"""
    try:
        entry = data.get('entry', [])[0]
        change = entry.get('changes', [])[0]
        val = change.get('value', {})
        messages = val.get('messages', [])
        contacts = val.get('contacts', [])
        
        if not messages:
            return None

        msg = messages[0]
        sender_phone = msg.get('from', '')
        msg_id = msg.get('id', '')
        msg_type = msg.get('type', '')
        
        patient_name = 'Paciente WhatsApp'
        if contacts:
            profile = contacts[0].get('profile', {})
            patient_name = profile.get('name', 'Paciente WhatsApp')

        body_text = ''
        if msg_type == 'text':
            body_text = msg.get('text', {}).get('body', '').strip()
        elif msg_type == 'interactive':
            interactive = msg.get('interactive', {})
            itype = interactive.get('type', '')
            if itype == 'button_reply':
                body_text = interactive.get('button_reply', {}).get('title', '')
            elif itype == 'list_reply':
                body_text = interactive.get('list_reply', {}).get('title', '')
        elif msg_type == 'button':
            body_text = msg.get('button', {}).get('text', '')

        return {
            'phone': sender_phone,
            'name': patient_name,
            'message_id': msg_id,
            'type': msg_type,
            'text': body_text
        }
    except Exception as e:
        print(f"[WhatsApp Webhook Error] Error parseando payload de Meta: {e}")
        return None

def process_conversational_turn(phone, patient_name, user_text):
    """
    Gestiona el ciclo conversacional con memoria y extracción estructurada con Gemini 3.8 Flash.
    """
    clean_phone = re.sub(r'[^0-9+]', '', phone)
    if clean_phone not in CONVERSATION_SESSIONS:
        CONVERSATION_SESSIONS[clean_phone] = {
            "phone": clean_phone,
            "patient_name": patient_name,
            "history": [],
            "extracted": {
                "nombre": patient_name if patient_name != 'Paciente WhatsApp' else None,
                "telefono": clean_phone,
                "sucursal": "Monterrey Centro",
                "tratamiento": "Valoración General",
                "urgencia": "Sin dolor",
                "fecha_cita": None,
                "hora_cita": "11:00 AM",
                "intencion": "consulta"
            },
            "created_at": datetime.now().isoformat()
        }

    session = CONVERSATION_SESSIONS[clean_phone]
    session["last_active"] = datetime.now().isoformat()
    if patient_name and patient_name != 'Paciente WhatsApp':
        session["extracted"]["nombre"] = patient_name

    # Manejar respuestas a números del menú directo (1, 2, 3, 4, 5)
    menu_reply = handle_menu_quick_number(user_text, session)
    if menu_reply:
        session["history"].append({"role": "user", "text": user_text})
        session["history"].append({"role": "assistant", "text": menu_reply})
        # Sincronizar actualización en BD
        sync_extracted_lead_to_crm(session["extracted"], last_message=user_text)
        return menu_reply

    # Llamar al modelo de IA generativa (Gemini 3.8 Flash)
    ai_raw_response = generate_ai_reply(session, user_text)

    # Extraer bloque json_lead si el modelo lo generó
    clean_response, extracted_json = parse_ai_json_block(ai_raw_response)
    if extracted_json:
        for k, v in extracted_json.items():
            if v is not None and v != "":
                session["extracted"][k] = v

    # Guardar en historial
    session["history"].append({"role": "user", "text": user_text})
    session["history"].append({"role": "assistant", "text": clean_response})

    # Guardar o actualizar automáticamente en la base de datos del panel de control
    sync_extracted_lead_to_crm(session["extracted"], last_message=user_text)

    return clean_response

def handle_menu_quick_number(user_text, session):
    """Responde inmediatamente si el usuario seleccionó una opción del menú"""
    txt = user_text.strip()
    if txt in ('1', '1️⃣', 'Opción 1', 'Confirmar Cita', '1. Confirmar y Bloquear Cita en Sillón'):
        session["extracted"]["intencion"] = "agendar"
        return (
            "🦷 *¡Excelente decisión!* Hemos apartado preventivamente tu sillón dental en "
            f"*{session['extracted'].get('sucursal', 'Monterrey Centro')}*. "
            "Por favor compárteme tu *Nombre Completo* y qué día te gustaría acudir (de Lunes a Sábado) "
            "para asignarte a tu doctor especialista de inmediato."
        )
    elif txt in ('2', '2️⃣', 'Opción 2', 'Cotización', '2. Recibir Cotización Desglosada con Precios y MSI'):
        session["extracted"]["intencion"] = "cotizar"
        return (
            "💎 *Cotización Oficial Clínica Cobá:*\n"
            "• *Brackets Metálicos:* $1,999 MXN inicial + Limpieza Ultrasónica de obsequio.\n"
            "• *Coronas de Zirconia Monolítica:* Máxima resistencia y estética natural.\n"
            "• *Limpieza y Paquete de Resinas:* $950 MXN.\n"
            "Aceptamos transferencias, efectivo y tarjetas de crédito con *3, 6 y 12 Meses Sin Intereses*.\n"
            "¿Cuál de estos tratamientos es el que te interesa cotizar hoy?"
        )
    elif txt in ('3', '3️⃣', 'Opción 3', 'Urgencia', '3. 🚨 Urgencia Dental por Dolor Agudo'):
        session["extracted"]["intencion"] = "urgencia"
        session["extracted"]["urgencia"] = "Dolor agudo urgente"
        return (
            "🚨 *Protocolo de Urgencia Dental Inmediata Cobá:*\n"
            "Lamentamos mucho la molestia. Contamos con sillón de atención prioritaria sin espera en nuestras dos sedes:\n"
            "📍 *Monterrey Centro:* Jerónimo Treviño #1111 Pte. (Tel: 81 8374 6726)\n"
            "📍 *Guadalupe Centro:* Benito Juárez #825, Local D (Tel: 81 8070 1778)\n"
            "¿A cuál sucursal te queda más cerca dirigirte en este momento?"
        )
    elif txt in ('4', '4️⃣', 'Opción 4', 'Ubicación', '4. 📍 Ubicación GPS y Cómo Llegar'):
        return (
            "📍 *Sucursales de Clínica Dental Cobá:*\n\n"
            "1. *Monterrey Centro:* Jerónimo Treviño #1111 Pte. (entre Juan Álvarez y Serafín Peña). "
            "Contamos con estacionamiento privado para pacientes.\n"
            "👉 Google Maps: https://maps.google.com/?q=Jeronimo+Trevino+1111+Monterrey\n\n"
            "2. *Guadalupe Centro:* Benito Juárez #825, Local D, 2do Piso (entre 5 de Mayo y 3ra Av.).\n"
            "¿Te gustaría que apartemos tu horario en alguna de estas dos ubicaciones?"
        )
    elif txt in ('5', '5️⃣', 'Opción 5', 'Doctor', '5. 👨‍⚕️ Hablar con Odontólogo Especialista en Vivo'):
        session["extracted"]["intencion"] = "hablar_con_doctor"
        return (
            "👨‍⚕️ *Conexión con Doctor Especialista:*\n"
            "He notificado a la recepción médica y a los odontólogos de turno. "
            "Un doctor de nuestro equipo revisará tu mensaje en breve para orientarte personalmente. "
            "Por favor cuéntame brevemente qué molestia o duda tienes para que el doctor tenga todo el contexto."
        )
    return None

def generate_ai_reply(session, user_text):
    """Genera la respuesta con Gemini 3.8 Flash con el historial acumulado"""
    cfg = load_whatsapp_config()
    model_name = cfg.get("MODEL_NAME", "gemini-3.8-flash")
    
    # Construir contexto de los últimos turnos
    recent_history = session["history"][-8:] if len(session["history"]) > 8 else session["history"]
    convo_context = "\n".join([f"{msg['role'].upper()}: {msg['text']}" for msg in recent_history])
    
    prompt = f"""{CLINICAL_SYSTEM_PROMPT}

DATOS ACTUALES RECOPILADOS DEL PACIENTE EN BD:
{json.dumps(session['extracted'], indent=2, ensure_ascii=False)}

HISTORIAL RECIENTE:
{convo_context}

NUEVO MENSAJE DEL PACIENTE:
PACIENTE: {user_text}

RESPUESTA DEL ASISTENTE CLÍNICO COBÁ:"""

    if HAS_GEMINI and gemini_client:
        try:
            response = gemini_client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"[Gemini AI Error]: {e}")

    # Fallback conversacional de alta calidad si no hay conexión externa temporal
    return fallback_conversational_rules(user_text, session)

def parse_ai_json_block(text):
    """Extrae bloques delimitados por ```json_lead ... ``` de la respuesta"""
    pattern = r'```(?:json_lead|json)\s*(\{.*?\})\s*```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        json_str = match.group(1)
        clean_text = re.sub(pattern, '', text, flags=re.DOTALL).strip()
        try:
            data = json.loads(json_str)
            return clean_text, data
        except Exception:
            return clean_text, None
    return text, None

def fallback_conversational_rules(user_text, session):
    """Motor de respaldo robusto en caso de latencia de red"""
    ut = user_text.lower()
    name = session["extracted"].get("nombre") or "estimado paciente"
    
    if any(k in ut for k in ['precio', 'costo', 'cuanto', 'sale', 'cotiz']):
        return (
            f"Con gusto, {name}. En Clínica Dental Cobá manejamos promociones directas: los brackets están en $1,999 MXN de anticipo con limpieza incluida, "
            "las coronas de zirconia estética desde $3,800 MXN y el paquete de limpieza ultrasónica con resinas en $950 MXN. "
            "Además contamos con hasta 12 meses sin intereses. ¿Qué procedimiento específico te gustaría realizarte?"
        )
    elif any(k in ut for k in ['dolor', 'urgencia', 'muela', 'emergencia', 'duele']):
        session["extracted"]["urgencia"] = "Dolor agudo"
        return (
            f"Comprendo la urgencia, {name}. Si tienes dolor agudo o inflamación, te asignamos sillón prioritario en nuestra sede de "
            "Monterrey Centro (81 8374 6726) o Guadalupe Centro (81 8070 1778). ¿Podrías indicarme tu nombre para ingresarte de inmediato al sistema?"
        )
    elif any(k in ut for k in ['cita', 'agenda', 'horario', 'cuando']):
        return (
            f"¡Claro que sí! Con gusto apartamos tu horario, {name}. Atendemos de Lunes a Viernes de 9:00 AM a 6:00 PM y Sábados de 9:00 AM a 5:00 PM. "
            "¿Prefieres acudir a nuestra sucursal de Monterrey Centro o Guadalupe Centro, y qué día te acomoda mejor?"
        )
    else:
        return (
            f"¡Hola! Gracias por comunicarte con Clínica Dental Cobá, {name}. Con gusto te ayudo con información de tratamientos, presupuestos con promociones "
            "o apartando tu cita con nuestros especialistas en Monterrey o Guadalupe. ¿En qué podemos apoyarte hoy?"
        )

def sync_extracted_lead_to_crm(extracted, last_message=""):
    """
    Sincroniza y escribe la información directamente en crm_leads_coba.json y crm_leads_coba.csv.
    Esto alimenta inmediatamente el panel de control del cliente (portal_doctor.html).
    """
    os.makedirs(AUTO_DIR, exist_ok=True)
    phone = extracted.get("telefono") or "Sin teléfono"
    
    # 1. Leer registros existentes
    leads = []
    if os.path.exists(JSON_CRM_PATH):
        try:
            with open(JSON_CRM_PATH, 'r', encoding='utf-8') as f:
                leads = json.load(f)
        except Exception:
            leads = []

    # 2. Buscar si el lead ya existe por teléfono
    existing = None
    for item in leads:
        if item.get("telefono") and re.sub(r'\D', '', item.get("telefono")) == re.sub(r'\D', '', phone):
            existing = item
            break

    now_iso = datetime.now().isoformat()
    nombre_final = extracted.get("nombre") or (existing.get("nombre") if existing else "Paciente WhatsApp")

    if existing:
        # Actualizar campos existentes
        if extracted.get("nombre") and extracted.get("nombre") != "Paciente WhatsApp":
            existing["nombre"] = extracted.get("nombre")
        if extracted.get("sucursal"):
            existing["sucursal"] = extracted.get("sucursal")
        if extracted.get("tratamiento"):
            existing["tratamiento"] = extracted.get("tratamiento")
        if extracted.get("fecha_cita"):
            existing["fecha_cita"] = extracted.get("fecha_cita")
        if extracted.get("hora_cita"):
            existing["hora_cita"] = extracted.get("hora_cita")
        if extracted.get("urgencia"):
            existing["urgencia"] = extracted.get("urgencia")
        
        existing["status"] = "WhatsApp Activo (En Conversación)"
        existing["last_update"] = now_iso
        existing["source"] = "WhatsApp Cloud API Directo"
        if last_message:
            existing["ultimo_mensaje"] = last_message
    else:
        # Crear nuevo registro en la base de datos
        folio = f"COBA-WA-{random.randint(1000, 9999)}"
        new_lead = {
            "id": str(uuid.uuid4())[:8],
            "folio": folio,
            "nombre": nombre_final,
            "telefono": phone,
            "email": extracted.get("email") or f"paciente_{phone[-4:]}@whatsapp.coba",
            "sucursal": extracted.get("sucursal") or "Monterrey Centro (Jerónimo Treviño #1111 Pte.)",
            "tratamiento": extracted.get("tratamiento") or "Valoración General",
            "urgencia": extracted.get("urgencia") or "🟢 Sin dolor",
            "fecha_cita": extracted.get("fecha_cita") or datetime.now().strftime('%Y-%m-%d'),
            "hora_cita": extracted.get("hora_cita") or "11:00 AM",
            "mensaje": last_message or "Registro iniciado vía WhatsApp Business",
            "status": "WhatsApp Activo (En Conversación)",
            "source": "WhatsApp Cloud API Directo",
            "timestamp": now_iso
        }
        leads.insert(0, new_lead)

    # 3. Guardar JSON
    try:
        with open(JSON_CRM_PATH, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[CRM Save Error] {e}")

    # 4. Guardar CSV (de respaldo)
    try:
        with open(CSV_CRM_PATH, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Nombre', 'Telefono', 'Email', 'Sucursal', 'Tratamiento', 'Fecha_Cita', 'Hora_Cita', 'Mensaje', 'Status'])
            for ld in leads:
                writer.writerow([
                    ld.get('timestamp', ''),
                    ld.get('nombre', ''),
                    ld.get('telefono', ''),
                    ld.get('email', ''),
                    ld.get('sucursal', ''),
                    ld.get('tratamiento', ''),
                    ld.get('fecha_cita', ''),
                    ld.get('hora_cita', ''),
                    ld.get('mensaje', ''),
                    ld.get('status', '')
                ])
    except Exception as e:
        print(f"[CSV Save Error] {e}")

    return leads[0] if leads else None

def send_meta_outbound_whatsapp_message(to_phone, text_body):
    """
    Envía un mensaje saliente a través de la API oficial de Meta (WhatsApp Cloud API v20.0).
    Endpoint: https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages
    """
    cfg = load_whatsapp_config()
    token = cfg.get("WHATSAPP_TOKEN", "").strip()
    phone_id = cfg.get("PHONE_NUMBER_ID", "").strip()

    if not token or not phone_id:
        # Modo simulación: no hay token de Meta configurado todavía
        print(f"[WhatsApp Outbound Simulado] Para {to_phone}: {text_body[:80]}...")
        return {"status": "simulated", "to": to_phone, "text": text_body}

    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    clean_to = re.sub(r'[^0-9]', '', to_phone)

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": clean_to,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": text_body
        }
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print(f"[WhatsApp Outbound Meta OK] {res_data}")
            return {"status": "sent", "meta_response": res_data}
    except Exception as err:
        print(f"[WhatsApp Outbound Meta Error] {err}")
        return {"status": "error", "error": str(err)}
