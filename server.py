#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor Unificado AUTOMATIC (Agencia IA Monterrey) + Caso Real Clínica Dental Cobá MTY
Incluye Motor Neural de Voz Humana en Tiempo Real (/api/tts) con:
  - Normalización Fonética Conversacional Mexicana (fechas, horas, precios, abreviaturas)
  - Síntesis Neural Gratuita de Alta Definición (Dalia MX, Salomé CO, Ava Multilingual DragonHD, Paloma US)
  - Conector Directo Opcional con ElevenLabs (eleven_multilingual_v2)
  - Caché instantáneo en disco para latencia < 50ms
"""

import os
import re
import sys
import csv
import json
import hashlib
import asyncio
import smtplib
import random
import unicodedata
from email.message import EmailMessage
import urllib.request
import urllib.parse
from datetime import datetime
import time
import uuid
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import edge_tts

try:
    import resend
except ImportError:
    resend = None

from inventory_service import (
    calculate_inventory_metrics,
    update_supply_price,
    save_or_create_supply,
    delete_supply,
    update_supply_stock
)
import pdf_receipt_service
import doctor_attendance_service
import whatsapp_bot_service
import mvp_database
import cybersecurity_shield
import io

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTOMATIC_DIR = os.path.join(BASE_DIR, 'automatic')
AUTO_DIR = os.path.join(BASE_DIR, 'automation')
TTS_CACHE_DIR = os.path.join(AUTO_DIR, 'tts_cache')
EMAILS_DIR = os.path.join(AUTO_DIR, 'emails')
os.makedirs(AUTO_DIR, exist_ok=True)
os.makedirs(TTS_CACHE_DIR, exist_ok=True)
os.makedirs(EMAILS_DIR, exist_ok=True)

CSV_CRM_PATH = os.path.join(AUTO_DIR, 'crm_leads_coba.csv')
JSON_CRM_PATH = os.path.join(AUTO_DIR, 'crm_leads_coba.json')
DOCTORS_FILE = os.path.join(AUTO_DIR, 'doctors.json')
EMAIL_CONFIG_PATH = os.path.join(AUTO_DIR, 'email_config.json')
CLINIC_CONFIG_PATH = os.path.join(AUTO_DIR, 'clinic_config.json')

N8N_PRODUCTION_WEBHOOK = os.environ.get('N8N_WEBHOOK_URL', '')
RETELL_API_KEY = os.environ.get('RETELL_API_KEY', '')
RETELL_AGENT_ID = os.environ.get('RETELL_AGENT_ID', 'agent_clinica_dental_coba_mty')
RETELL_FROM_NUMBER = os.environ.get('RETELL_FROM_NUMBER', '+528118483941')
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY', '')
ELEVENLABS_VOICE_ID = os.environ.get('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')  # Sarah / Bella Multilingual

VOICE_MAP = {
    'dalia': ('es-MX-DaliaNeural', '+3%', '+0Hz'),
    'salome': ('es-CO-SalomeNeural', '+2%', '+0Hz'),
    'ava': ('es-ES-XimenaNeural', '+2%', '+0Hz'),
    'paloma': ('es-US-PalomaNeural', '+2%', '+0Hz'),
    'ximena': ('es-ES-XimenaNeural', '+2%', '+0Hz')
}


def normalize_for_natural_mexican_speech(text: str) -> str:
    """
    Transforma números, precios, horas, fechas ISO y símbolos en español conversacional
    natural de México para que la voz neural suene 100% como una mujer real por teléfono.
    """
    if not text:
        return ""
    s = str(text)

    # Reemplazos de horarios comunes del sistema de booking
    time_replacements = {
        '09:30 AM': 'las nueve y media de la mañana',
        '11:00 AM': 'las once de la mañana',
        '12:30 PM': 'las doce y media de la tarde',
        '02:00 PM': 'las dos de la tarde',
        '03:30 PM': 'las tres y media de la tarde',
        '04:30 PM': 'las cuatro y media de la tarde',
        '05:15 PM': 'las cinco y cuarto de la tarde',
        'Sáb 10:30 AM': 'el sábado a las diez y media de la mañana',
        'Sábado Matutino': 'el sábado por la mañana'
    }
    for k, v in time_replacements.items():
        s = s.replace(f"a las {k}", f"a {v}").replace(k, v)

    # Reemplazos de precios y promociones
    price_replacements = {
        '$1,999 MXN': 'mil novecientos noventa y nueve pesos',
        '$1,999': 'mil novecientos noventa y nueve pesos',
        '$4,500 MXN': 'cuatro mil quinientos pesos',
        '$4,500': 'cuatro mil quinientos pesos',
        '$3,800 MXN': 'tres mil ochocientos pesos',
        '$3,800': 'tres mil ochocientos pesos',
        '$2,400 MXN': 'dos mil cuatrocientos pesos',
        '$2,400': 'dos mil cuatrocientos pesos',
        '$950 MXN': 'novecientos cincuenta pesos',
        '$950': 'novecientos cincuenta pesos',
        '$250 MXN': 'doscientos cincuenta pesos',
        '$250': 'doscientos cincuenta pesos'
    }
    for k, v in price_replacements.items():
        s = s.replace(k, v)

    # Reemplazos de direcciones y sucursales para lectura fluida
    s = s.replace('#1111 Pte.', 'número mil ciento once Poniente')
    s = s.replace('#1111', 'mil ciento once')
    s = s.replace('#825', 'ochocientos veinticinco')
    s = s.replace('Pte.', 'Poniente')
    s = s.replace('3ra Av.', 'Tercera Avenida')
    s = s.replace('2do piso', 'segundo piso')
    s = s.replace('MTY', 'Monterrey')
    s = s.replace('N.L.', 'Nuevo León')
    s = s.replace('24/7/365', 'veinticuatro siete todo el año')
    s = s.replace('24/7', 'veinticuatro siete')
    s = s.replace('B2B', 'empresarial')
    s = s.replace('CRM', 'sistema de clientes')

    # Convertir fechas ISO YYYY-MM-DD en formato hablado natural
    meses = {
        '01': 'enero', '02': 'febrero', '03': 'marzo', '04': 'abril',
        '05': 'mayo', '06': 'junio', '07': 'julio', '08': 'agosto',
        '09': 'septiembre', '10': 'octubre', '11': 'noviembre', '12': 'diciembre'
    }
    def replace_iso_date(match):
        _, mm, dd = match.group(1), match.group(2), int(match.group(3))
        mes_nombre = meses.get(mm, 'este mes')
        return f"{dd} de {mes_nombre}"

    s = re.sub(r'\b(202\d)-(\d{2})-(\d{2})\b', replace_iso_date, s)

    # Limpiar paréntesis o símbolos bruscos
    s = s.replace('+', ' más ')
    s = s.replace('(', ', ').replace(')', ', ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def synthesize_speech_bytes(text: str, voice_key: str = 'dalia', eleven_key: str = '') -> bytes:
    """
    Genera audio MP3 ultra-natural usando ElevenLabs (si se provee API key) o
    Microsoft Edge Neural Voices (Dalia MX / Salomé CO / Ava DragonHD) de forma 100% gratuita.
    Guarda en caché en disco para respuesta inmediata.
    """
    spoken_text = normalize_for_natural_mexican_speech(text)
    active_eleven_key = eleven_key.strip() or ELEVENLABS_API_KEY.strip()
    engine_tag = f"eleven_{ELEVENLABS_VOICE_ID}" if active_eleven_key else f"neural_{voice_key}"
    cache_hash = hashlib.sha256(f"{engine_tag}::{spoken_text}".encode('utf-8')).hexdigest()[:24]
    cache_file = os.path.join(TTS_CACHE_DIR, f"{cache_hash}.mp3")

    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 500:
        with open(cache_file, 'rb') as f:
            return f.read()

    # 1. Si hay API key de ElevenLabs, usar eleven_multilingual_v2
    if active_eleven_key:
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
            payload = {
                "text": spoken_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.42,
                    "similarity_boost": 0.82,
                    "style": 0.35,
                    "use_speaker_boost": True
                }
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'xi-api-key': active_eleven_key,
                    'Content-Type': 'application/json',
                    'Accept': 'audio/mpeg'
                }
            )
            audio_bytes = urllib.request.urlopen(req, timeout=10).read()
            if len(audio_bytes) > 500:
                with open(cache_file, 'wb') as f:
                    f.write(audio_bytes)
                return audio_bytes
        except Exception as e:
            print(f"[TTS ElevenLabs Fallback a Neural Gratis]: {e}")

    # 2. Motor Neural Gratuito de Alta Naturalidad (Edge Neural HD)
    voice_name, rate, pitch = VOICE_MAP.get(voice_key, VOICE_MAP['dalia'])

    async def _run_edge():
        comm = edge_tts.Communicate(spoken_text, voice_name, rate=rate, pitch=pitch)
        await comm.save(cache_file)

    asyncio.run(_run_edge())
    with open(cache_file, 'rb') as f:
        return f.read()


DOCTOR_USERS = {
    'doctor@coba.mx': {'password': 'coba2026', 'pin': '2026', 'name': 'Dr. Mauricio Cobá', 'role': 'Director Clínico', 'email': 'doctor@coba.mx'},
    'dr.coba': {'password': 'coba2026', 'pin': '2026', 'name': 'Dr. Mauricio Cobá', 'role': 'Director Clínico', 'email': 'doctor@coba.mx'},
    'recepcion@coba.mx': {'password': 'coba2026', 'pin': '2026', 'name': 'Recepción Cobá MTY', 'role': 'Coordinadora de Agenda', 'email': 'recepcion@coba.mx'}
}
DOCTOR_SESSIONS = {}

def load_doctors():
    if os.path.exists(DOCTORS_FILE):
        try:
            with open(DOCTORS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_doctors(doctors_list):
    with open(DOCTORS_FILE, 'w', encoding='utf-8') as f:
        json.dump(doctors_list, f, ensure_ascii=False, indent=2)


DEFAULT_CLINIC_CONFIG = {
    'theme_mode': 'dark',
    'palette_key': 'coba',
    'owner_primary': '#06B6D4',
    'owner_secondary': '#10B981',
    'custom_hex': '#06B6D4',
    'clinic_name': 'Clínica Dental Cobá Monterrey',
    'clinic_tagline': 'Odontología Digital Avanzada, Implantes & Ortodoncia',
    'clinic_phone': '+52 81 1848 3941',
    'clinic_email': 'contacto@coba.mx',
    'sucursal_1_name': 'Monterrey Centro',
    'sucursal_1_address': 'Jerónimo Treviño #1111 Pte., Monterrey Centro',
    'sucursal_1_hours': 'Lun a Vie 09:00 - 19:30 | Sáb 09:00 - 15:00',
    'sucursal_2_name': 'Guadalupe Centro',
    'sucursal_2_address': 'Benito Juárez #825, Guadalupe Centro',
    'sucursal_2_hours': 'Lun a Sáb 09:00 - 18:30',
    'sofia_voice': 'dalia',
    'sofia_tone': 'profesional',
    'auto_waitlist_call': True,
    'auto_google_reviews': True,
    'auto_consent_email': True,
    'auto_reminders_24h': True,
    'pin': '2026',
    'inactivity_lock_min': 15
}


def load_clinic_config():
    cfg = dict(DEFAULT_CLINIC_CONFIG)
    if os.path.exists(CLINIC_CONFIG_PATH):
        try:
            with open(CLINIC_CONFIG_PATH, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                cfg.update(saved)
        except Exception:
            pass
    return cfg


def save_clinic_config(new_data):
    cfg = load_clinic_config()
    cfg.update(new_data)
    with open(CLINIC_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    # Sincronizar PIN de desbloqueo rápido con cuentas en memoria si cambió
    if 'pin' in new_data and new_data['pin']:
        new_pin = str(new_data['pin']).strip()
        for k in DOCTOR_USERS:
            DOCTOR_USERS[k]['pin'] = new_pin
    return cfg


TREATMENT_VALUES = {
    'alineador': 28000,
    'invisible': 28000,
    'implante': 12500,
    'carilla': 7200,
    'zirconia': 4500,
    'corona': 4500,
    'puente': 4500,
    'blanqueamiento': 3800,
    'diseño': 3800,
    'cirug': 3200,
    'tercer': 3200,
    'endodoncia': 2400,
    'bracket': 1999,
    'ortodoncia': 1999,
    'pediatr': 1650,
    'sellador': 1650,
    'limpieza': 950,
    'profilaxis': 950,
    'resina': 950,
    'valoración': 250
}

TREATMENT_LAB_COSTS = {
    'alineador': 6200,
    'invisible': 6200,
    'implante': 2400,
    'carilla': 1450,
    'zirconia': 950,
    'corona': 950,
    'puente': 950,
    'blanqueamiento': 420,
    'diseño': 420,
    'cirug': 350,
    'tercer': 350,
    'endodoncia': 320,
    'bracket': 380,
    'ortodoncia': 380,
    'pediatr': 210,
    'sellador': 210,
    'limpieza': 120,
    'profilaxis': 120,
    'resina': 150,
    'valoración': 40
}


def get_treatment_estimated_value(treatment_str):
    t = (treatment_str or '').lower()
    for k, v in TREATMENT_VALUES.items():
        if k in t:
            return v
    return 950


def get_treatment_lab_cost(treatment_str):
    t = (treatment_str or '').lower()
    for k, v in TREATMENT_LAB_COSTS.items():
        if k in t:
            return v
    return 150


def get_doctor_commission_pct(doc_obj_or_spec):
    if isinstance(doc_obj_or_spec, dict) and doc_obj_or_spec.get('comision_pct'):
        return int(doc_obj_or_spec['comision_pct'])
    spec = (doc_obj_or_spec.get('specialty', '') if isinstance(doc_obj_or_spec, dict) else str(doc_obj_or_spec)).lower()
    if 'endo' in spec:
        return 50
    if 'implan' in spec or 'cirug' in spec:
        return 45
    if 'protes' in spec or 'prótes' in spec or 'zirconia' in spec:
        return 45
    if 'orto' in spec or 'alineador' in spec:
        return 40
    if 'estét' in spec or 'estet' in spec or 'diseño' in spec:
        return 42
    if 'pediatr' in spec:
        return 45
    return 40


def normalize_text_match(s):
    if not s:
        return ''
    s = urllib.parse.unquote(str(s)).lower()
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def compute_doctor_stats(leads, doctor_filter=None, branch_filter=None):
    doctors = load_doctors()
    d_filt = (doctor_filter or '').strip()
    b_filt = (branch_filter or '').strip()

    selected_doctor_profile = None
    target_doc_name = None
    if d_filt and d_filt.lower() not in ('todos', 'todas', 'all', ''):
        d_norm = normalize_text_match(d_filt)
        for d in doctors:
            if d['id'].lower() == d_filt.lower() or normalize_text_match(d['name']) == d_norm or d_norm in normalize_text_match(d['name']) or normalize_text_match(d['name']) in d_norm:
                selected_doctor_profile = d
                target_doc_name = normalize_text_match(d['name'])
                break
        if not target_doc_name:
            target_doc_name = d_norm

    filtered_leads = []
    for l in leads:
        if target_doc_name:
            doc_str = normalize_text_match(l.get('doctor_asignado', ''))
            if target_doc_name not in doc_str and doc_str not in target_doc_name:
                continue
        if b_filt and b_filt.lower() not in ('todas', 'todos', 'all', ''):
            b_norm = normalize_text_match(b_filt)
            branch_str = normalize_text_match(l.get('sucursal', ''))
            if b_norm not in branch_str:
                continue
        filtered_leads.append(l)

    total = len(filtered_leads)
    confirmadas = sum(1 for l in filtered_leads if str(l.get('status', '')).lower() in ('confirmada', 'confirmado', 'agendada'))
    asistidas = sum(1 for l in filtered_leads if str(l.get('status', '')).lower() in ('asistió', 'asistio', 'atendida', 'completada'))
    pendientes = sum(1 for l in filtered_leads if str(l.get('status', '')).lower() in ('pendiente', 'por confirmar'))
    canceladas = sum(1 for l in filtered_leads if str(l.get('status', '')).lower() in ('cancelada', 'cancelado'))
    
    ingresos_proyectados = sum(get_treatment_estimated_value(l.get('tratamiento')) for l in filtered_leads if str(l.get('status', '')).lower() not in ('cancelada', 'cancelado'))
    ingresos_confirmados = sum(get_treatment_estimated_value(l.get('tratamiento')) for l in filtered_leads if str(l.get('status', '')).lower() in ('confirmada', 'confirmado', 'asistió', 'asistio', 'atendida', 'completada'))
    costo_lab_filtrado = sum(get_treatment_lab_cost(l.get('tratamiento')) for l in filtered_leads if str(l.get('status', '')).lower() not in ('cancelada', 'cancelado'))
    
    fuera_horario = 0
    for l in filtered_leads:
        ts = str(l.get('timestamp', ''))
        ts_time = ts.split('T')[-1] if 'T' in ts else (ts.split(' ')[-1] if ' ' in ts else '')
        try:
            h = int(ts_time.split(':')[0])
            if h >= 19 or h < 8:
                fuera_horario += 1
        except Exception:
            if 'IA' in str(l.get('source', '')) or 'IA' in str(l.get('estado_ia', '')):
                fuera_horario += 1
                
    mty_centro = sum(1 for l in filtered_leads if 'Centro' in str(l.get('sucursal', '')) or 'Treviño' in str(l.get('sucursal', '')))
    guadalupe = sum(1 for l in filtered_leads if 'Guadalupe' in str(l.get('sucursal', '')) or 'Juárez' in str(l.get('sucursal', '')))
    
    trat_counts = {}
    for l in filtered_leads:
        t = str(l.get('tratamiento', 'General'))
        simple_t = 'Brackets Metálicos' if 'bracket' in t.lower() else (
            'Alineadores Invisibles' if 'alineador' in t.lower() or 'invisible' in t.lower() else (
            'Zirconia & Coronas' if 'zirconia' in t.lower() or 'corona' in t.lower() or 'puente' in t.lower() else (
            'Implantes Dentales' if 'implante' in t.lower() else (
            'Endodoncia Micro' if 'endodoncia' in t.lower() else (
            'Diseño & Blanqueamiento' if 'diseño' in t.lower() or 'blanqueamiento' in t.lower() or 'carilla' in t.lower() else (
            'Limpieza & Profilaxis' if 'limpieza' in t.lower() or 'profilaxis' in t.lower() else (
            'Cirugía Oral' if 'cirug' in t.lower() or 'tercer' in t.lower() else (
            'Odontopediatría' if 'pediatr' in t.lower() else 'Valoración General'))))))))
        trat_counts[simple_t] = trat_counts.get(simple_t, 0) + 1

    ratio_conf = round((confirmadas + asistidas) / total * 100, 1) if total > 0 else 0.0

    # Generar ranking de especialistas médicos con comisiones y liquidación quincenal
    doctors = load_doctors()
    doc_stats_map = {}
    for d in doctors:
        comm_pct = get_doctor_commission_pct(d)
        doc_entry = dict(d)  # Contiene todos los aditamentos y perfil clínico del doctor
        doc_entry.update({
            'citas_total': 0,
            'citas_asistidas': 0,
            'citas_confirmadas': 0,
            'citas_canceladas': 0,
            'ingresos_mxn': 0,
            'costo_lab_mxn': 0,
            'ingreso_neto_base_mxn': 0,
            'comision_pct': comm_pct,
            'pago_neto_doctor_mxn': 0,
            'liquidacion_quincenal_mxn': 0,
            'utilidad_neta_clinica_mxn': 0
        })
        doc_stats_map[d['name']] = doc_entry

    for l in leads:
        if b_filt and b_filt not in ('todas', 'todos', 'all', ''):
            if b_filt not in str(l.get('sucursal', '')).lower():
                continue
        doc_name = l.get('doctor_asignado', '')
        matched_key = None
        for k in doc_stats_map.keys():
            if k in doc_name or doc_name in k:
                matched_key = k
                break
        if matched_key:
            st = str(l.get('status', '')).lower()
            val = get_treatment_estimated_value(l.get('tratamiento'))
            lab = get_treatment_lab_cost(l.get('tratamiento'))
            doc_stats_map[matched_key]['citas_total'] += 1
            if 'asist' in st or 'atend' in st or 'complet' in st:
                doc_stats_map[matched_key]['citas_asistidas'] += 1
            elif 'confirm' in st or 'agend' in st:
                doc_stats_map[matched_key]['citas_confirmadas'] += 1
            elif 'cancel' in st:
                doc_stats_map[matched_key]['citas_canceladas'] += 1
            
            if 'cancel' not in st:
                doc_stats_map[matched_key]['ingresos_mxn'] += val
                doc_stats_map[matched_key]['costo_lab_mxn'] += lab

    for k, d_stat in doc_stats_map.items():
        base_neta = max(0, d_stat['ingresos_mxn'] - d_stat['costo_lab_mxn'])
        pct = d_stat['comision_pct']
        pago_doc = round(base_neta * (pct / 100.0))
        utilidad_clinica = base_neta - pago_doc
        d_stat['ingreso_neto_base_mxn'] = base_neta
        d_stat['pago_neto_doctor_mxn'] = pago_doc
        d_stat['liquidacion_quincenal_mxn'] = round(pago_doc / 4.0)
        d_stat['utilidad_neta_clinica_mxn'] = utilidad_clinica

    rankings = list(doc_stats_map.values())
    rankings.sort(key=lambda x: x['ingresos_mxn'], reverse=True)

    # Cálculos financieros netos del filtro actual (Doctor individual o Clínica global)
    if selected_doctor_profile:
        active_comm_pct = get_doctor_commission_pct(selected_doctor_profile)
    else:
        active_comm_pct = 43  # Promedio ponderado de especialistas
    base_neta_filtrada = max(0, ingresos_proyectados - costo_lab_filtrado)
    pago_neto_doctor_actual = round(base_neta_filtrada * (active_comm_pct / 100.0))
    liquidacion_quincenal_actual = round(pago_neto_doctor_actual / 4.0)
    utilidad_neta_clinica_actual = base_neta_filtrada - pago_neto_doctor_actual

    # Evolución mensual en 2 meses intensos
    monthly_trend = {
        'Agosto 2026': {'citas': 0, 'ingresos': 0},
        'Septiembre 2026': {'citas': 0, 'ingresos': 0},
        'Octubre 2026': {'citas': 0, 'ingresos': 0}
    }
    for l in filtered_leads:
        f_cita = str(l.get('fecha_cita', ''))
        st = str(l.get('status', '')).lower()
        val = get_treatment_estimated_value(l.get('tratamiento'))
        if f_cita.startswith('2026-08'):
            monthly_trend['Agosto 2026']['citas'] += 1
            if 'cancel' not in st:
                monthly_trend['Agosto 2026']['ingresos'] += val
        elif f_cita.startswith('2026-09'):
            monthly_trend['Septiembre 2026']['citas'] += 1
            if 'cancel' not in st:
                monthly_trend['Septiembre 2026']['ingresos'] += val
        elif f_cita.startswith('2026-10'):
            monthly_trend['Octubre 2026']['citas'] += 1
            if 'cancel' not in st:
                monthly_trend['Octubre 2026']['ingresos'] += val

    return {
        'total_citas': total,
        'confirmadas': confirmadas,
        'asistidas': asistidas,
        'pendientes': pendientes,
        'canceladas': canceladas,
        'tasa_confirmacion': ratio_conf,
        'ingresos_proyectados_mxn': ingresos_proyectados,
        'ingresos_confirmados_mxn': ingresos_confirmados,
        'costo_lab_mxn': costo_lab_filtrado,
        'ingreso_neto_base_mxn': base_neta_filtrada,
        'comision_pct': active_comm_pct,
        'pago_neto_doctor_mxn': pago_neto_doctor_actual,
        'liquidacion_quincenal_mxn': liquidacion_quincenal_actual,
        'utilidad_neta_clinica_mxn': utilidad_neta_clinica_actual,
        'citas_fuera_horario_ia': fuera_horario,
        'sucursal_centro': mty_centro,
        'sucursal_guadalupe': guadalupe,
        'tratamientos': trat_counts,
        'doctor_rankings': rankings,
        'monthly_trend': monthly_trend,
        'selected_doctor_profile': selected_doctor_profile
    }


def validate_doctor_auth(handler):
    auth_header = handler.headers.get('Authorization', '')
    token = ''
    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()
    if not token:
        parsed = urllib.parse.urlparse(handler.path)
        qs = urllib.parse.parse_qs(parsed.query)
        token = qs.get('token', [''])[0]
    if token and token in DOCTOR_SESSIONS:
        return DOCTOR_SESSIONS[token]
    return None


def ensure_crm_files():
    if not os.path.exists(CSV_CRM_PATH):
        with open(CSV_CRM_PATH, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Fecha_Registro', 'Nombre', 'Telefono', 'Email',
                'Sucursal', 'Tratamiento', 'Fecha_Cita', 'Hora_Cita',
                'Doctor', 'Estado', 'Mensaje', 'Medio', 'Estado_Llamada_IA'
            ])
    if not os.path.exists(JSON_CRM_PATH):
        with open(JSON_CRM_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def save_lead_to_crm(payload):
    ensure_crm_files()
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    record = {
        'id': payload.get('id') or f"coba-{int(time.time() * 1000)}",
        'timestamp': payload.get('timestamp') or now_str,
        'nombre': payload.get('nombre', 'Sin Nombre'),
        'telefono': payload.get('telefono', ''),
        'email': payload.get('email', ''),
        'sucursal': payload.get('sucursal', 'Monterrey Centro (Jerónimo Treviño #1111 Pte.)'),
        'tratamiento': payload.get('tratamiento', 'Valoración General'),
        'fecha_cita': payload.get('fecha_cita', 'Por confirmar'),
        'hora_cita': payload.get('hora_cita', '11:00 AM'),
        'doctor_asignado': payload.get('doctor_asignado', 'Dr. Mauricio Cobá'),
        'status': payload.get('status', 'Confirmada'),
        'mensaje': payload.get('mensaje', ''),
        'source': payload.get('source', 'Sistema AUTOMATIC Monterrey'),
        'estado_ia': payload.get('estado_ia', 'Llamada IA Disparada + Registrado en CRM AUTOMATIC')
    }

    with open(CSV_CRM_PATH, 'a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow([
            record['id'], record['timestamp'], record['nombre'], record['telefono'], record['email'],
            record['sucursal'], record['tratamiento'], record['fecha_cita'], record['hora_cita'],
            record['doctor_asignado'], record['status'], record['mensaje'], record['source'], record['estado_ia']
        ])

    try:
        with open(JSON_CRM_PATH, 'r', encoding='utf-8') as f:
            leads = json.load(f)
    except Exception:
        leads = []
    leads.append(record)
    with open(JSON_CRM_PATH, 'w', encoding='utf-8') as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

    return record


def forward_to_external_integrations(record):
    results = {'n8n_forwarded': False, 'retell_called': False}
    if N8N_PRODUCTION_WEBHOOK:
        try:
            req = urllib.request.Request(
                N8N_PRODUCTION_WEBHOOK,
                data=json.dumps({'body': record}).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=5)
            results['n8n_forwarded'] = True
        except Exception as e:
            results['n8n_error'] = str(e)

    if RETELL_API_KEY:
        try:
            retell_payload = {
                'from_number': RETELL_FROM_NUMBER,
                'to_number': record['telefono'],
                'call_type': 'phone_call',
                'retell_llm_dynamic_variables': {
                    'nombre': record['nombre'],
                    'sucursal': record['sucursal'],
                    'tratamiento': record['tratamiento'],
                    'fecha_cita': record['fecha_cita'],
                    'hora_cita': record['hora_cita'],
                    'mensaje': record['mensaje']
                },
                'override_agent_id': RETELL_AGENT_ID
            }
            req = urllib.request.Request(
                'https://api.retellai.com/v2/create-phone-call',
                data=json.dumps(retell_payload).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {RETELL_API_KEY}',
                    'Content-Type': 'application/json'
                }
            )
            urllib.request.urlopen(req, timeout=6)
            results['retell_called'] = True
        except Exception as e:
            results['retell_error'] = str(e)

    # Despacho automático de correo HTML con diseño de Clínica Cobá
    results['email'] = dispatch_confirmation_email(record)
    return results


def build_appointment_email_html(record: dict) -> str:
    """
    Genera una plantilla de correo electrónico HTML ultra-premium, responsiva y
    adaptada al diseño Dark Luxury y cyan (#06B6D4) de Clínica Dental Cobá.
    """
    nombre = record.get('nombre', 'Estimado Paciente')
    sucursal = record.get('sucursal', 'Monterrey Centro')
    is_guadalupe = 'Guadalupe' in sucursal

    if is_guadalupe:
        sucursal_nombre = "Sucursal Guadalupe Centro"
        direccion_linea = "Benito Juárez #825, Local D (entre 5 de Mayo y 3ra Av.), Guadalupe, N.L."
        telefono_sucursal = "81 8070 1778"
        maps_link = "https://maps.google.com/?q=Benito+Juarez+825+Guadalupe+Centro+Nuevo+Leon"
    else:
        sucursal_nombre = "Sucursal Monterrey Centro"
        direccion_linea = "Jerónimo Treviño #1111 Pte. (entre Juan Álvarez y Serafín Peña), Centro, Monterrey, N.L."
        telefono_sucursal = "81 8374 6726"
        maps_link = "https://maps.google.com/?q=Jeronimo+Trevino+1111+Centro+Monterrey"

    fecha = record.get('fecha_cita', 'Fecha por definir')
    hora = record.get('hora_cita', '11:00 AM')
    tratamiento = record.get('tratamiento', 'Consulta Odontológica General')
    whatsapp_link = "https://wa.me/528118483941?text=" + urllib.parse.quote(f"Hola Clínica Dental Cobá, tengo cita confirmada para {nombre} el {fecha} a las {hora}.")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pase Digital de Cita Confirmada — Clínica Dental Cobá</title>
</head>
<body style="margin: 0; padding: 0; background-color: #050507; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #ffffff;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #050507; padding: 35px 15px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 600px; background: linear-gradient(160deg, #0e1722 0%, #09090b 100%); border: 1px solid rgba(6, 182, 212, 0.45); border-radius: 20px; overflow: hidden; box-shadow: 0 25px 50px rgba(0,0,0,0.85), 0 0 35px rgba(6, 182, 212, 0.18);">
          <!-- Header Bar -->
          <tr>
            <td style="padding: 34px 30px 24px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.08); background: radial-gradient(circle at top, rgba(6,182,212,0.22) 0%, transparent 75%);">
              <div style="display: inline-block; background: rgba(6, 182, 212, 0.16); border: 1px solid rgba(6, 182, 212, 0.5); color: #38BDF8; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; padding: 6px 14px; border-radius: 999px; margin-bottom: 14px;">
                ⭐ Pase Digital de Consulta Odontológica
              </div>
              <h1 style="margin: 0; font-size: 25px; font-weight: 800; color: #ffffff; letter-spacing: -0.02em;">
                CLÍNICA DENTAL COBÁ
              </h1>
              <p style="margin: 6px 0 0; font-size: 13px; color: #06B6D4; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em;">
                Monterrey Centro &bull; Guadalupe Centro
              </p>
            </td>
          </tr>

          <!-- Body Content -->
          <tr>
            <td style="padding: 30px 30px 20px;">
              <h2 style="margin: 0 0 12px; font-size: 20px; font-weight: 700; color: #F3F4F6;">
                ¡Hola {nombre}! Tu cita ha quedado agendada con éxito.
              </h2>
              <p style="margin: 0 0 24px; font-size: 14px; line-height: 1.6; color: #94A3B8;">
                Sofía, tu Asistente Dental de Clínica Cobá, acaba de registrar y confirmar tu lugar en nuestro sistema de agenda médica. A continuación tienes tu pase digital con todos los detalles de tu consulta:
              </p>

              <!-- Ticket Info Box -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(6, 182, 212, 0.28); border-radius: 14px; margin-bottom: 24px; overflow: hidden;">
                <tr>
                  <td style="padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.06);">
                    <table width="100%">
                      <tr>
                        <td width="32%" style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">📅 Fecha:</td>
                        <td width="68%" style="font-size: 15px; color: #38BDF8; font-weight: 700;">{fecha}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.06);">
                    <table width="100%">
                      <tr>
                        <td width="32%" style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">⏰ Horario:</td>
                        <td width="68%" style="font-size: 15px; color: #FFFFFF; font-weight: 700;">{hora}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.06);">
                    <table width="100%">
                      <tr>
                        <td width="32%" style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">🏥 Sucursal:</td>
                        <td width="68%" style="font-size: 14px; color: #E2E8F0; font-weight: 600;">{sucursal_nombre}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.06);">
                    <table width="100%">
                      <tr>
                        <td width="32%" style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">🦷 Tratamiento:</td>
                        <td width="68%" style="font-size: 14px; color: #10B981; font-weight: 700;">{tratamiento}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.06);">
                    <table width="100%">
                      <tr>
                        <td width="32%" style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">📍 Dirección:</td>
                        <td width="68%" style="font-size: 13px; color: #CBD5E1; line-height: 1.4;">{direccion_linea}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
                <tr>
                  <td style="padding: 16px 20px;">
                    <table width="100%">
                      <tr>
                        <td width="32%" style="font-size: 12px; color: #94A3B8; text-transform: uppercase; font-weight: 600;">📞 Teléfono:</td>
                        <td width="68%" style="font-size: 13px; color: #38BDF8; font-weight: 600;">{telefono_sucursal}</td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- Recomendación de Asistencia -->
              <div style="background: rgba(16, 185, 129, 0.08); border-left: 3px solid #10B981; padding: 14px 16px; border-radius: 0 10px 10px 0; margin-bottom: 26px;">
                <p style="margin: 0; font-size: 13px; color: #A7F3D0; line-height: 1.5;">
                  💡 <strong>Nota de Recepción:</strong> Tu lugar en el consultorio y tu precio de promoción han quedado asegurados. Te sugerimos presentarte con 5 minutos de anticipación y mostrar este pase o tu nombre en mostrador.
                </p>
              </div>

              <!-- Action Buttons -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 10px;">
                <tr>
                  <td align="center" style="padding-bottom: 12px;">
                    <a href="{maps_link}" target="_blank" style="display: block; width: 100%; max-width: 320px; background: linear-gradient(135deg, #06B6D4 0%, #0891B2 100%); color: #000000; text-align: center; text-decoration: none; padding: 14px 20px; border-radius: 10px; font-weight: 800; font-size: 14px; box-shadow: 0 4px 15px rgba(6,182,212,0.4);">
                      📍 Abrir Ubicación en Google Maps
                    </a>
                  </td>
                </tr>
                <tr>
                  <td align="center">
                    <a href="{whatsapp_link}" target="_blank" style="display: block; width: 100%; max-width: 320px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.2); color: #E2E8F0; text-align: center; text-decoration: none; padding: 12px 20px; border-radius: 10px; font-weight: 600; font-size: 13px;">
                      💬 Escribir por WhatsApp a Recepción
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding: 20px 30px 28px; text-align: center; border-top: 1px solid rgba(255,255,255,0.08); background: rgba(0,0,0,0.4);">
              <p style="margin: 0 0 6px; font-size: 12px; color: #64748B;">
                © 2026 Clínica Dental Cobá • Monterrey, Nuevo León.
              </p>
              <p style="margin: 0; font-size: 11px; color: #475569;">
                Plataforma Digital &amp; Sistema de Confirmación Inmediata implementado por <strong>AUTOMATIC</strong>
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""
    return html


def dispatch_confirmation_email(record: dict) -> dict:
    """
    Despacha el correo de confirmación de cita al paciente registrado:
      1. Genera y guarda el pase HTML en disco (disponible en /api/email/preview)
      2. Si existe RESEND_API_KEY, envía a través de la API de Resend
      3. Si existe GMAIL_USER y GMAIL_APP_PASSWORD, envía por SMTP directo de Gmail
    """
    recipient = (record.get('email') or '').strip()
    if not recipient or '@' not in recipient:
        return {'status': 'skipped', 'reason': 'No hay correo válido'}

    html_content = build_appointment_email_html(record)

    # 1. Guardar siempre en disco para trazabilidad y previsualización inmediata
    safe_email = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', recipient)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_email}.html"
    filepath = os.path.join(EMAILS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    latest_path = os.path.join(EMAILS_DIR, 'latest.html')
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    preview_url = f"/api/email/preview?email={urllib.parse.quote(recipient)}"

    # Cargar configuraciones guardadas de email si existen
    config = {}
    if os.path.exists(EMAIL_CONFIG_PATH):
        try:
            with open(EMAIL_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            config = {}

    # 2. Resend API
    resend_key = config.get('resend_api_key') or os.environ.get('RESEND_API_KEY', '').strip()
    if resend_key and resend:
        try:
            resend.api_key = resend_key
            sender = config.get('resend_sender') or os.environ.get('RESEND_SENDER', 'onboarding@resend.dev')
            res = resend.Emails.send({
                "from": f"Clínica Dental Cobá <{sender}>",
                "to": [recipient],
                "subject": f"⭐ Pase Digital: Cita Agendada en Clínica Dental Cobá",
                "html": html_content
            })
            print(f"[EMAIL RESEND] Enviado con éxito a {recipient}: {res}")
            return {
                'status': 'sent',
                'method': 'resend',
                'recipient': recipient,
                'preview_url': preview_url,
                'resend_id': res.get('id') if isinstance(res, dict) else str(res)
            }
        except Exception as e:
            print(f"[EMAIL RESEND ERROR] {e}")

    # 3. Gmail SMTP
    gmail_user = (config.get('gmail_user') or os.environ.get('GMAIL_USER', '')).strip()
    gmail_pass = (config.get('gmail_app_password') or os.environ.get('GMAIL_APP_PASSWORD', '')).strip().replace(' ', '')
    if gmail_user and gmail_pass:
        try:
            msg = EmailMessage()
            msg['Subject'] = f"⭐ Pase Digital: Cita Agendada en Clínica Dental Cobá"
            msg['From'] = f"Clínica Dental Cobá <{gmail_user}>"
            msg['To'] = recipient
            msg.set_content(f"Hola {record.get('nombre')}, tu cita para el {record.get('fecha_cita')} a las {record.get('hora_cita')} en {record.get('sucursal')} ha quedado agendada con éxito.")
            msg.add_alternative(html_content, subtype='html')

            smtp_host = config.get('smtp_host') or os.environ.get('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(config.get('smtp_port') or os.environ.get('SMTP_PORT', 587))
            with smtplib.SMTP(smtp_host, smtp_port, timeout=12) as server:
                server.starttls()
                server.login(gmail_user, gmail_pass)
                server.send_message(msg)

            print(f"[EMAIL GMAIL SMTP] Correo enviado exitosamente a {recipient} desde {gmail_user}")
            return {
                'status': 'sent',
                'method': 'smtp_gmail',
                'recipient': recipient,
                'sender': gmail_user,
                'preview_url': preview_url
            }
        except Exception as e:
            print(f"[EMAIL GMAIL SMTP ERROR] {e}")

    # 4. Modo Pase Digital Generado (Listo para envío)
    print(f"[EMAIL DISPATCH] Pase digital generado en disco para {recipient}. Ver en {preview_url}")
    return {
        'status': 'generated',
        'recipient': recipient,
        'preview_url': preview_url,
        'filepath': filepath,
        'note': 'Pase digital generado con éxito. Conecta tu Gmail o Resend para envío directo a bandeja de entrada.'
    }


def dispatch_custom_clinical_email(recipient: str, subject: str, html_content: str, plain_text: str, tag_prefix: str = 'clinical') -> dict:
    """
    Envía cualquier correo clínico oficial (Consentimiento Informado, Reactivación VIP,
    Endodoncia sin Corona, Control de Ortodoncia, Lista de Espera, Reseñas Google Maps)
    a través del SMTP de Gmail configurado y guarda copia en disco.
    """
    recipient = (recipient or '').strip()
    if not recipient or '@' not in recipient:
        return {'status': 'skipped', 'reason': 'Correo electrónico no válido'}

    safe_email = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', recipient)
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{tag_prefix}_{safe_email}.html"
    filepath = os.path.join(EMAILS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    latest_path = os.path.join(EMAILS_DIR, 'latest.html')
    with open(latest_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    preview_url = f"/api/email/preview?email={urllib.parse.quote(recipient)}"

    config = {}
    if os.path.exists(EMAIL_CONFIG_PATH):
        try:
            with open(EMAIL_CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception:
            config = {}

    gmail_user = (config.get('gmail_user') or os.environ.get('GMAIL_USER', '')).strip()
    gmail_pass = (config.get('gmail_app_password') or os.environ.get('GMAIL_APP_PASSWORD', '')).strip().replace(' ', '')
    if gmail_user and gmail_pass:
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = f"Clínica Dental Cobá Monterrey <{gmail_user}>"
            msg['To'] = recipient
            msg.set_content(plain_text)
            msg.add_alternative(html_content, subtype='html')

            smtp_host = config.get('smtp_host') or os.environ.get('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(config.get('smtp_port') or os.environ.get('SMTP_PORT', 587))
            with smtplib.SMTP(smtp_host, smtp_port, timeout=12) as server:
                server.starttls()
                server.login(gmail_user, gmail_pass)
                server.send_message(msg)

            print(f"[CLINICAL EMAIL SMTP] Enviado ({tag_prefix}) a {recipient}")
            return {
                'status': 'sent',
                'method': 'smtp_gmail',
                'recipient': recipient,
                'sender': gmail_user,
                'preview_url': preview_url
            }
        except Exception as e:
            print(f"[CLINICAL EMAIL SMTP ERROR] {e}")

    return {
        'status': 'generated',
        'recipient': recipient,
        'preview_url': preview_url,
        'filepath': filepath
    }


def build_informed_consent_email_html(data: dict) -> str:
    nombre = data.get('patient_name', 'Paciente')
    email = data.get('email', '')
    doctor = data.get('doctor_name', 'Dr. Mauricio Cobá')
    cedula = data.get('doctor_cedula', 'Ced. Prof. 8492019 • SSA 39482')
    sucursal = data.get('sucursal', 'Monterrey Centro (Jerónimo Treviño #1111 Pte.)')
    tratamiento = data.get('tratamiento', 'Procedimiento Odontológico Especializado')
    riesgos = data.get('procedure_risks', 'Inflamación post-operatoria leve, sensibilidad térmica temporal, necesidad de medicación analgésica/antibiótica y cuidados de higiene específicos.')
    folio = data.get('folio') or f"NOM004-{int(time.time())}"
    fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    is_signed = bool(data.get('is_signed', True))
    badge_text = "DOCUMENTO LEGAL FIRMADO Y CERTIFICADO (NOM-004-SSA3-2012)" if is_signed else "SOLICITUD DE LECTURA Y FIRMA DE CONSENTIMIENTO INFORMADO"
    status_box = f"""
    <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.45); border-radius: 12px; padding: 16px; margin-top: 20px; text-align: center;">
      <div style="font-size: 12px; font-weight: 800; color: #10B981; text-transform: uppercase; letter-spacing: 0.08em;">✓ Firma Digital Registrada en Expediente Clínico</div>
      <div style="font-size: 13px; color: #E2E8F0; margin-top: 6px;">Firmado por: <strong>{nombre}</strong> &bull; Folio Legal: <strong>{folio}</strong></div>
      <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">Sello de Tiempo: {fecha_hora} &bull; Respaldo Digital COFEPRIS / NOM-013-SSA2</div>
    </div>
    """ if is_signed else f"""
    <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.45); border-radius: 12px; padding: 16px; margin-top: 20px; text-align: center;">
      <div style="font-size: 12px; font-weight: 800; color: #F59E0B; text-transform: uppercase; letter-spacing: 0.08em;">⏳ Pendiente de Firma Presencial o Digital</div>
      <div style="font-size: 13px; color: #E2E8F0; margin-top: 6px;">Por favor revisa este documento antes de tu intervención en {sucursal}.</div>
    </div>
    """

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Consentimiento Informado NOM-004 — Clínica Dental Cobá</title></head>
<body style="margin:0;padding:0;background-color:#050507;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#ffffff;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#050507;padding:30px 15px;">
    <tr><td align="center">
      <table role="presentation" width="100%" style="max-width:620px;background:linear-gradient(160deg,#0e1722 0%,#09090b 100%);border:1px solid rgba(6,182,212,0.45);border-radius:20px;overflow:hidden;">
        <tr>
          <td style="padding:28px 30px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.08);background:radial-gradient(circle at top,rgba(6,182,212,0.22) 0%,transparent 75%);">
            <div style="display:inline-block;background:rgba(6,182,212,0.16);border:1px solid rgba(6,182,212,0.5);color:#38BDF8;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;padding:5px 12px;border-radius:999px;margin-bottom:10px;">
              🛡️ {badge_text}
            </div>
            <h1 style="margin:0;font-size:22px;font-weight:800;color:#ffffff;">CLÍNICA DENTAL COBÁ MONTERREY</h1>
            <p style="margin:4px 0 0;font-size:12px;color:#06B6D4;font-weight:600;">Carta de Consentimiento Informado Odontológico &bull; Folio #{folio}</p>
          </td>
        </tr>
        <tr>
          <td style="padding:26px 30px;">
            <p style="margin:0 0 16px;font-size:14px;line-height:1.6;color:#E2E8F0;">
              Estimado(a) <strong>{nombre}</strong>, en cumplimiento con la <strong>Norma Oficial Mexicana NOM-004-SSA3-2012</strong> (Del Expediente Clínico) y <strong>NOM-013-SSA2-2015</strong>, te enviamos el respaldo oficial de tu Consentimiento Informado para tu expediente médico y protección mutua:
            </p>
            <table width="100%" cellspacing="0" cellpadding="0" style="background:rgba(15,23,42,0.8);border:1px solid rgba(6,182,212,0.28);border-radius:12px;padding:16px;margin-bottom:18px;font-size:13px;color:#CBD5E1;">
              <tr><td style="padding:6px 0;"><strong>👤 Paciente:</strong> {nombre} ({email})</td></tr>
              <tr><td style="padding:6px 0;"><strong>👨‍⚕️ Especialista Tratante:</strong> {doctor} ({cedula})</td></tr>
              <tr><td style="padding:6px 0;"><strong>🏥 Sucursal:</strong> {sucursal}</td></tr>
              <tr><td style="padding:6px 0;"><strong>🦷 Procedimiento Autorizado:</strong> <span style="color:#38BDF8;font-weight:700;">{tratamiento}</span></td></tr>
            </table>
            <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:12px;padding:16px;font-size:12px;line-height:1.6;color:#94A3B8;">
              <strong style="color:#FFF;display:block;margin-bottom:6px;">DECLARACIÓN CLÍNICA Y AUTORIZACIÓN:</strong>
              Declaro que el especialista me ha explicado de forma clara la naturaleza y propósito del tratamiento (<strong>{tratamiento}</strong>), las alternativas terapéuticas, el uso de anestesia local odontológica y los alcances esperados.<br><br>
              <strong>Riesgos y consideraciones informadas:</strong> {riesgos}<br><br>
              Autorizo libremente al equipo médico de Clínica Dental Cobá a realizar dicho procedimiento y me comprometo a seguir las indicaciones post-operatorias y asistir puntualmente a mis citas de control.
            </div>
            {status_box}
          </td>
        </tr>
        <tr>
          <td style="padding:18px 30px;text-align:center;border-top:1px solid rgba(255,255,255,0.08);background:rgba(0,0,0,0.4);font-size:11px;color:#64748B;">
            © 2026 Clínica Dental Cobá Monterrey &bull; Documento Legal Protegido
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def build_followup_email_html(data: dict) -> str:
    nombre = data.get('patient_name', 'Estimado Paciente')
    case_type = data.get('case_type', 'endodoncia_sin_corona')
    doctor = data.get('doctor_name', 'Dr. Mauricio Cobá')
    sucursal = data.get('sucursal', 'Monterrey Centro (Jerónimo Treviño #1111 Pte.)')
    custom_note = data.get('custom_note', '')

    if case_type == 'endodoncia_sin_corona':
        badge = "⚠️ ALERTA DE PROTECCIÓN DENTAL • FASE 2 PENDIENTE"
        headline = f"¡Hola {nombre}! Tu diente con endodoncia necesita su Corona de Zirconia para no fracturarse."
        body_text = (
            f"Te escribimos personalmente del equipo del <strong>{doctor}</strong> en Clínica Dental Cobá. "
            f"Notamos en tu expediente clínico que concluimos con éxito tu tratamiento de conductos (Endodoncia), pero <strong>aún tienes pendiente colocar tu Corona de Zirconia de protección</strong>.<br><br>"
            f"💡 <strong>¿Por qué es urgente?</strong> Un diente con endodoncia ya no tiene irrigación interna y se vuelve frágil como el cristal. Si masticas algo duro sin su corona definitiva, la raíz puede fracturarse verticalmente y perderse la pieza por completo.<br><br>"
            f"¿Cómo te has sentido? ¿Has tenido alguna molestia al masticar o necesitas ayuda con facilidades de pago? Queremos cuidarte y por eso activamos para ti un <strong>Bono de Lealtad VIP de $600 MXN de descuento directo</strong> + escaneo 3D sin costo si agendas tu rehabilitación esta semana."
        )
        promo_box = "🎁 BENEFICIO EXCLUSIVO ACTIVADO: Bono de $600 MXN en tu Corona de Zirconia + Prioridad sin fila en sala"
    elif case_type == 'ortodoncia_control':
        badge = "🦷 CONTROL MENSUAL DE ORTODONCIA Y BRACKETS"
        headline = f"¡Hola {nombre}! Es momento de tu ajuste mensual de Brackets y cambio de arcos."
        body_text = (
            f"La <strong>{doctor}</strong> revisó tu bitácora de ortodoncia y notó que ya corresponde tu <strong>control y activación mensual</strong>.<br><br>"
            f"Recuerda que cada mes que pasa sin activar tus arcos o renovar ligas y cadenas elásticas retrasa el resultado final de tu sonrisa y puede descontrolar el movimiento radicular.<br><br>"
            f"¿Se te despegó algún bracket, te lastima algún alambre o necesitas un horario especial? Contéstanos este correo o haz clic abajo para apartar tu ajuste mensual con trato preferencial."
        )
        promo_box = "✨ PACIENTE ACTIVO DE ORTODONCIA: Reposición de 1 bracket sin costo + Limpieza interproximal en tu control"
    else:
        badge = "👑 INVITACIÓN VIP DE LEALTAD • TRATO PREFERENCIAL ÚNICO"
        headline = f"¡Te extrañamos en Clínica Dental Cobá, {nombre}! Tienes un Pase VIP reservado."
        body_text = (
            f"Vimos que anteriormente solicitaste informes o tuviste que cancelar tu cita con nosotros en <strong>{sucursal}</strong>. "
            f"Para nosotros tú no eres un paciente más: queremos saber cómo sigues de tu salud dental y si podemos ayudarte en algo.<br><br>"
            f"Hemos desbloqueado para ti un <strong>Pase de Trato Preferencial Único por Lealtad</strong> por encima de la lista general: tendrás acceso directo al especialista sin tiempo de espera en recepción, valoración diagnóstica de cortesía y precio congelado de promoción."
        )
        promo_box = "👑 TRATO PREFERENCIAL VIP: Recepción Directa sin Espera + Diagnóstico 3D de Cortesía + 15% Adicional por Lealtad"

    if custom_note:
        body_text += f"<br><br><strong>Nota personal de tu doctor:</strong> <em>\"{custom_note}\"</em>"

    wa_link = "https://wa.me/528118483941?text=" + urllib.parse.quote(f"Hola Clínica Dental Cobá, soy {nombre}, recibí mi correo de seguimiento VIP y quiero agendar mi cita prioritaria.")

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Seguimiento Preferencial VIP — Clínica Dental Cobá</title></head>
<body style="margin:0;padding:0;background-color:#050507;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#ffffff;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#050507;padding:30px 15px;">
    <tr><td align="center">
      <table role="presentation" width="100%" style="max-width:600px;background:linear-gradient(160deg,#0e1722 0%,#09090b 100%);border:1px solid rgba(245,158,11,0.5);border-radius:20px;overflow:hidden;">
        <tr>
          <td style="padding:28px 30px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.08);background:radial-gradient(circle at top,rgba(245,158,11,0.2) 0%,transparent 75%);">
            <div style="display:inline-block;background:rgba(245,158,11,0.18);border:1px solid rgba(245,158,11,0.5);color:#FBBF24;font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;padding:5px 14px;border-radius:999px;margin-bottom:12px;">
              {badge}
            </div>
            <h1 style="margin:0;font-size:23px;font-weight:800;color:#ffffff;">CLÍNICA DENTAL COBÁ MONTERREY</h1>
          </td>
        </tr>
        <tr>
          <td style="padding:28px 30px;">
            <h2 style="margin:0 0 14px;font-size:19px;font-weight:700;color:#F8FAFC;line-height:1.4;">{headline}</h2>
            <p style="margin:0 0 20px;font-size:14px;line-height:1.65;color:#CBD5E1;">{body_text}</p>
            <div style="background:rgba(245,158,11,0.12);border:1px solid rgba(245,158,11,0.4);border-radius:12px;padding:15px;margin-bottom:24px;text-align:center;font-size:13px;font-weight:700;color:#FDE68A;">
              {promo_box}
            </div>
            <div style="text-align:center;">
              <a href="{wa_link}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#F59E0B 0%,#D97706 100%);color:#000000;text-decoration:none;padding:14px 28px;border-radius:10px;font-weight:800;font-size:14px;">
                💬 Reclamar mi Espacio Preferencial Ahora
              </a>
            </div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def build_waitlist_recovery_email_html(data: dict) -> str:
    nombre = data.get('patient_name', 'Paciente Preferencial')
    doctor = data.get('doctor_name', 'Dr. Mauricio Cobá')
    fecha = data.get('fecha_liberada', 'Hoy / Mañana')
    hora = data.get('hora_liberada', '04:00 PM')
    sucursal = data.get('sucursal', 'Monterrey Centro (Jerónimo Treviño #1111 Pte.)')
    tratamiento = data.get('tratamiento', 'Consulta de Especialidad')
    wa_link = "https://wa.me/528118483941?text=" + urllib.parse.quote(f"¡SÍ! Soy {nombre}, quiero tomar el espacio liberado del {fecha} a las {hora} con {doctor}.")

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>¡Espacio Liberado en Lista de Espera! — Clínica Dental Cobá</title></head>
<body style="margin:0;padding:0;background-color:#050507;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#ffffff;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#050507;padding:30px 15px;">
    <tr><td align="center">
      <table role="presentation" width="100%" style="max-width:600px;background:linear-gradient(160deg,#0e1722 0%,#09090b 100%);border:1px solid rgba(16,185,129,0.5);border-radius:20px;overflow:hidden;">
        <tr>
          <td style="padding:26px 30px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.08);background:radial-gradient(circle at top,rgba(16,185,129,0.22) 0%,transparent 75%);">
            <div style="display:inline-block;background:rgba(16,185,129,0.18);border:1px solid rgba(16,185,129,0.5);color:#34D399;font-size:11px;font-weight:800;text-transform:uppercase;padding:5px 14px;border-radius:999px;margin-bottom:10px;">
              ⚡ ALERTA EN TIEMPO REAL • LISTA DE ESPERA INTELIGENTE
            </div>
            <h1 style="margin:0;font-size:22px;font-weight:800;color:#ffffff;">¡SE LIBERÓ UN HORARIO PRIORITARIO PARA TI!</h1>
          </td>
        </tr>
        <tr>
          <td style="padding:26px 30px;">
            <p style="font-size:15px;line-height:1.6;color:#E2E8F0;margin:0 0 18px;">
              ¡Hola <strong>{nombre}</strong>! Te estamos marcando por teléfono con nuestra asistente de voz IA Sofía y enviándote este aviso urgente porque <strong>se acaba de liberar un espacio exclusivo</strong> que coincide con tu solicitud en nuestra Lista de Espera:
            </p>
            <div style="background:rgba(15,23,42,0.85);border:1px solid rgba(16,185,129,0.4);border-radius:14px;padding:18px;margin-bottom:22px;">
              <div style="font-size:14px;color:#34D399;font-weight:800;margin-bottom:8px;">📅 Horario Disponible Inmediato: {fecha} a las {hora}</div>
              <div style="font-size:13px;color:#CBD5E1;margin-bottom:4px;"><strong>👨‍⚕️ Especialista:</strong> {doctor}</div>
              <div style="font-size:13px;color:#CBD5E1;margin-bottom:4px;"><strong>🏥 Sucursal:</strong> {sucursal}</div>
              <div style="font-size:13px;color:#CBD5E1;"><strong>🦷 Tratamiento:</strong> {tratamiento}</div>
            </div>
            <div style="text-align:center;">
              <a href="{wa_link}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#10B981 0%,#059669 100%);color:#000000;text-decoration:none;padding:14px 28px;border-radius:10px;font-weight:800;font-size:14px;">
                ⚡ Confirmar y Tomar este Lugar Ahora
              </a>
            </div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def build_google_review_email_html(data: dict) -> str:
    nombre = data.get('patient_name', 'Estimado Paciente')
    doctor = data.get('doctor_name', 'Dr. Mauricio Cobá')
    sucursal = data.get('sucursal', 'Monterrey Centro')
    is_guadalupe = 'Guadalupe' in sucursal
    if is_guadalupe:
        maps_review_url = "https://www.google.com/maps/search/?api=1&query=Clinica+Dental+Coba+Benito+Juarez+825+Guadalupe+Nuevo+Leon"
        branch_label = "Sucursal Guadalupe Centro (Benito Juárez #825)"
    else:
        maps_review_url = "https://www.google.com/maps/search/?api=1&query=Clinica+Dental+Coba+Jeronimo+Trevino+1111+Monterrey+Centro"
        branch_label = "Sucursal Monterrey Centro (Jerónimo Treviño #1111 Pte.)"

    wa_feedback = "https://wa.me/528118483941?text=" + urllib.parse.quote(f"Hola Dirección Clínica Cobá, soy {nombre} y quiero compartir un comentario sobre mi consulta.")

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><title>Califica tu Experiencia en Google Maps — Clínica Dental Cobá</title></head>
<body style="margin:0;padding:0;background-color:#050507;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#ffffff;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color:#050507;padding:30px 15px;">
    <tr><td align="center">
      <table role="presentation" width="100%" style="max-width:600px;background:linear-gradient(160deg,#0e1722 0%,#09090b 100%);border:1px solid rgba(6,182,212,0.45);border-radius:20px;overflow:hidden;">
        <tr>
          <td style="padding:28px 30px;text-align:center;border-bottom:1px solid rgba(255,255,255,0.08);">
            <div style="font-size:28px;margin-bottom:8px;">⭐⭐⭐⭐⭐</div>
            <h1 style="margin:0;font-size:22px;font-weight:800;color:#ffffff;">¿Cómo te atendió hoy {doctor}?</h1>
            <p style="margin:6px 0 0;font-size:13px;color:#06B6D4;">{branch_label}</p>
          </td>
        </tr>
        <tr>
          <td style="padding:26px 30px;text-align:center;">
            <p style="font-size:14px;line-height:1.6;color:#CBD5E1;margin:0 0 22px;">
              ¡Hola <strong>{nombre}</strong>! Fue un gusto atenderte hoy en Clínica Dental Cobá. Tu opinión en <strong>Google Maps</strong> nos ayuda muchísimo a que más familias de Monterrey conozcan el cuidado de nuestros especialistas.<br><br>
              Por compartir tu reseña de 5 estrellas, en tu próxima visita tienes un <strong>Kit Dental de Viaje + Aplicación de Flúor de Cortesía</strong>.
            </p>
            <div style="margin-bottom:16px;">
              <a href="{maps_review_url}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#F59E0B 0%,#D97706 100%);color:#000000;text-decoration:none;padding:15px 30px;border-radius:12px;font-weight:800;font-size:15px;">
                ⭐⭐⭐⭐⭐ Dejar 5 Estrellas en Google Maps Oficial
              </a>
            </div>
            <div>
              <a href="{wa_feedback}" target="_blank" style="display:inline-block;color:#94A3B8;font-size:12px;text-decoration:underline;">
                ¿Algo no estuvo perfecto (1 a 3 ★)? Escríbenos directo a Dirección Médica aquí
              </a>
            </div>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def generate_dental_ai_response(user_text: str, lead: dict) -> dict:
    """
    Motor de Inteligencia Clínica Dental y Triaje Conversacional para Sofía.
    Interpreta dolores dentales agudos, caries profundas, pericoronitis, ortodoncia,
    estética, costos y confirmación de citas.
    """
    t = (user_text or "").lower().strip()
    nombre = (lead.get('nombre') or 'Alejandro').replace('Lic.', '').replace('Ing.', '').split()[0]
    sucursal = lead.get('sucursal') or 'Monterrey Centro'
    sucursal_corta = "Guadalupe Centro" if "Guadalupe" in sucursal else "Monterrey Centro"
    fecha = lead.get('fecha_cita') or 'mañana'
    hora = lead.get('hora_cita') or '11:00 AM'
    tratamiento = lead.get('tratamiento') or 'consulta de valoración'

    # 1. Dolor agudo / Urgencias dentales / Molestias / Endodoncia / Muelas del Juicio
    pain_keywords = [
        'dolor', 'duele', 'muela', 'picada', 'sensibilidad', 'sensible', 'frio', 'frío', 'caliente',
        'inflamad', 'hinchad', 'absceso', 'sangr', 'encía', 'nervio', 'endodoncia', 'muela del juicio',
        'tercer molar', 'no aguanto', 'punzante', 'agudo', 'infeccion', 'infección', 'antibiotico',
        'molestia', 'latido', 'pulsada'
    ]
    if any(k in t for k in pain_keywords):
        return {
            'reply': f"Ay no me digas {nombre}, qué feo el dolor de muela. Por lo que me estás diciendo, puede ser una inflamación del nervio o una caries profunda que requiera endodoncia o valoración urgente. No te preocupes, ahorita mismo le pongo nota de máxima prioridad al doctor para que en cuanto llegues a nuestra sucursal de {sucursal_corta} te tomen tu radiografía digital y te pasen directo al sillón sin esperar nada. ¿Te queda bien que te dejemos apartado para el {fecha} a las {hora}, o prefieres que te atendamos hoy mismo?",
            'intent': 'pain_emergency',
            'is_confirmed': False
        }

    # 2. Confirmación afirmativa
    confirm_keywords = [
        'sí', 'si', 'confirmo', 'confírmala', 'confirmala', 'me queda bien', 'a esa hora',
        'está perfecto', 'esta perfecto', 'agenda', 'agéndame', 'agendame', 'apartámela', 'apartamela',
        'de acuerdo', 'sale', 'va', 'perfecto', 'ok', 'nos vemos', 'ahí nos vemos', 'claro'
    ]
    negation_keywords = ['no me queda', 'no puedo', 'cambiar', 'otro día', 'otra hora', 'más tarde']
    if any(k in t for k in confirm_keywords) and not any(k in t for k in negation_keywords):
        return {
            'reply': f"¡Listo {nombre}! Ya quedó cien por ciento confirmada tu cita en nuestro sistema para el {fecha} a las {hora} en {sucursal_corta}. Ya te agendé tu lugar en el consultorio y te aseguré tu precio de promoción. Ahorita mismo te llega tu confirmación por correo y WhatsApp con la ubicación en Google Maps. ¡Muchísimas gracias y nos vemos muy pronto por acá!",
            'intent': 'confirmation',
            'is_confirmed': True
        }

    # 3. Preguntas de Precios, Pagos y Costos
    pricing_keywords = ['pago', 'pagos', 'tarjeta', 'efectivo', 'transferencia', 'meses', 'cuánto', 'cuanto', 'precio', 'cuesta', 'costo', 'cotiz', 'cobran']
    if any(k in t for k in pricing_keywords):
        return {
            'reply': f"Mira {nombre}, en Clínica Cobá aceptamos efectivo, transferencias y cualquier tarjeta de crédito o débito, además de que te ofrecemos facilidades de pagos parciales súper cómodos. Y tu valoración incluye diagnóstico con cámara intraoral para que veas todo con total transparencia. ¿Te parece bien que te deje confirmada tu cita para el {fecha} a las {hora}?",
            'intent': 'pricing',
            'is_confirmed': False
        }

    # 4. Brackets y Ortodoncia
    bracket_keywords = ['bracket', 'brackets', 'freno', 'frenos', 'chueco', 'alinear', 'ortodoncia']
    if any(k in t for k in bracket_keywords):
        return {
            'reply': f"¡Te va a encantar la promoción {nombre}! El paquete de brackets metálicos está en solo mil novecientos noventa y nueve pesos e incluye la instalación de ambas arcadas y tu limpieza ultrasónica gratis. Las citas mensuales de control quedan en doscientos cincuenta pesos. ¿Te dejo confirmado este precio en tu cita para el {fecha} a las {hora}?",
            'intent': 'brackets',
            'is_confirmed': False
        }

    # 5. Coronas, Zirconia, Diente Quebrado, Implantes
    zirconia_keywords = ['zirconia', 'corona', 'puente', 'diente roto', 'quebrado', 'fractura', 'implante', 'postizo', 'porcelana']
    if any(k in t for k in zirconia_keywords):
        return {
            'reply': f"Claro {nombre}. Para dientes dañados o ausentes trabajamos con zirconia europea de alta estética, que queda idéntica a tus dientes naturales y sin bordes oscuros, además de implantes de titanio. Manejamos pagos parciales para que no desembolses todo de golpe. ¿Te confirmo tu valoración para el {fecha} a las {hora}?",
            'intent': 'zirconia',
            'is_confirmed': False
        }

    # 6. Limpieza, Resinas, Blanqueamiento
    clean_keywords = ['limpieza', 'profilaxis', 'sarro', 'resina', 'amalgama', 'blanqueamiento', 'manchas']
    if any(k in t for k in clean_keywords):
        return {
            'reply': f"Súper bien {nombre}. Nuestro paquete preventivo incluye la valoración, limpieza ultrasónica sin dolor y dos resinas del color exacto de tu diente por novecientos cincuenta pesos. Sales con tu boca impecable el mismo día. ¿Te aparto el espacio para el {fecha} a las {hora}?",
            'intent': 'hygiene',
            'is_confirmed': False
        }

    # 7. Ubicación y Horarios
    loc_keywords = ['dónde', 'donde', 'ubicacion', 'ubicación', 'dirección', 'direccion', 'llegar', 'horario', 'abierto', 'sábado', 'sabado', 'domingo']
    if any(k in t for k in loc_keywords):
        return {
            'reply': f"Estamos súper bien ubicados {nombre}: en Monterrey Centro sobre Jerónimo Treviño número mil ciento once Poniente, y en Guadalupe Centro sobre Benito Juárez ochocientos veinticinco. Atendemos de lunes a viernes de nueve de la mañana a seis de la tarde, y los sábados de nueve a cinco. ¿En cuál de las dos sucursales te queda más cerca?",
            'intent': 'location',
            'is_confirmed': False
        }

    # Fallback conversacional empático
    return {
        'reply': f"Entendido perfectamente {nombre}. Ya anoté todos tus comentarios para el doctor especialista en {sucursal_corta}. Para darte la mejor atención personalizada, ¿te parece bien que ya te deje confirmado tu lugar para el {fecha} a las {hora}?",
        'intent': 'general',
        'is_confirmed': False
    }


class UnifiedAgencyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _get_client_ip(self):
        forwarded = self.headers.get('CF-Connecting-IP') or self.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return self.client_address[0] if self.client_address else '127.0.0.1'

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def end_headers(self):
        for h_name, h_val in cybersecurity_shield.get_hardened_security_headers().items():
            self.send_header(h_name, h_val)
        super().end_headers()

    def translate_path(self, path):
        clean_path = path.split('?', 1)[0].split('#', 1)[0]

        # Telemetría y Ciberseguridad del MVP Full-Stack
        if clean_path in ('/telemetria', '/telemetria/', '/telemetria.html', '/mvp', '/mvp/', '/status', '/status/'):
            return os.path.join(BASE_DIR, 'telemetria.html')

        # Portal Médico Cobá
        if clean_path in ('/doctor', '/doctor/', '/portal-medico', '/portal-medico/', '/portal-doctor', '/portal-doctor/', '/clinica-coba/admin', '/clinica-coba/admin/'):
            return os.path.join(BASE_DIR, 'portal_doctor.html')

        # Agencia AUTOMATIC (si se solicita explícitamente)
        if clean_path in ('/automatic', '/automatic/', '/agency', '/agency/'):
            return os.path.join(AUTOMATIC_DIR, 'index.html')
        if clean_path.startswith('/automatic/'):
            rel = clean_path[len('/automatic/'):]
            return os.path.join(AUTOMATIC_DIR, rel.replace('/', os.sep))

        # Clínica Dental Cobá (predeterminado en raíz, /index.html, /coba, /clinica-coba)
        if clean_path in ('/', '/index.html', '/coba', '/coba/', '/coba.html', '/clinica-coba', '/clinica-coba/'):
            return os.path.join(BASE_DIR, 'index.html')
        if clean_path.startswith('/clinica-coba/'):
            rel = clean_path[len('/clinica-coba/'):]
            return os.path.join(BASE_DIR, rel.replace('/', os.sep))

        # Enrutamiento de imágenes comerciales si el referer es la agencia
        referer = self.headers.get('Referer', '')
        if '/automatic' in referer and clean_path.startswith('/images/'):
            candidate = os.path.join(AUTOMATIC_DIR, clean_path.lstrip('/').replace('/', os.sep))
            if os.path.exists(candidate):
                return candidate

        return super().translate_path(path)

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        client_ip = self._get_client_ip()
        parsed = urllib.parse.urlparse(self.path)

        # Inspección Activa de Ciberseguridad (WAF)
        is_safe, block_info = cybersecurity_shield.inspect_request(
            client_ip=client_ip,
            method='GET',
            raw_path=self.path,
            headers=dict(self.headers),
            body_bytes=None
        )
        if not is_safe:
            status_code = block_info.get('status_code', 403)
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            if status_code == 429:
                self.send_header('Retry-After', '60')
            self._send_cors_headers()
            self.end_headers()
            resp_body = {
                'error': block_info.get('error', 'FORBIDDEN'),
                'reason': block_info.get('reason', 'Acceso bloqueado por el firewall WAF.'),
                'incident_id': block_info.get('incident_id', 'UNKNOWN'),
                'status': 'BLOCKED',
                'defense': 'Cobá Military-Grade WAF Shield'
            }
            self.wfile.write(json.dumps(resp_body, ensure_ascii=False).encode('utf-8'))
            return

        # Telemetría del Escudo de Ciberseguridad en Tiempo Real
        if parsed.path == '/api/security/stats':
            stats = cybersecurity_shield.get_security_telemetry()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(stats, ensure_ascii=False).encode('utf-8'))
            return

        # Webhook GET de verificación oficial de Meta (WhatsApp Cloud API)
        if parsed.path == '/webhook/whatsapp':
            qs = urllib.parse.parse_qs(parsed.query)
            hub_mode = qs.get('hub.mode', [''])[0]
            hub_token = qs.get('hub.verify_token', [''])[0]
            hub_challenge = qs.get('hub.challenge', [''])[0]
            challenge = whatsapp_bot_service.verify_meta_webhook(hub_mode, hub_token, hub_challenge)
            if challenge:
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(challenge.encode('utf-8'))
                return
            else:
                self.send_response(403)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b'Verification token mismatch')
                return

        # Consultar sesiones activas de WhatsApp
        if parsed.path == '/api/whatsapp/conversations':
            sessions_data = []
            for phone, sess in whatsapp_bot_service.CONVERSATION_SESSIONS.items():
                sessions_data.append({
                    "phone": phone,
                    "patient_name": sess.get("patient_name"),
                    "extracted": sess.get("extracted"),
                    "last_active": sess.get("last_active"),
                    "message_count": len(sess.get("history", []))
                })
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "sessions": sessions_data}, ensure_ascii=False).encode('utf-8'))
            return

        # Configuración de WhatsApp Cloud API
                # Estado de Salud y Arquitectura del MVP Full-Stack
        if parsed.path == '/api/mvp/status':
            health_report = mvp_database.get_mvp_system_health()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(health_report, ensure_ascii=False).encode('utf-8'))
            return

        if parsed.path == '/api/whatsapp/config':
            cfg = whatsapp_bot_service.load_whatsapp_config()
            safe_cfg = cfg.copy()
            if safe_cfg.get("WHATSAPP_TOKEN"):
                t = safe_cfg["WHATSAPP_TOKEN"]
                safe_cfg["WHATSAPP_TOKEN_MASKED"] = t[:6] + "..." + t[-4:] if len(t) > 10 else "***"
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "config": safe_cfg}, ensure_ascii=False).encode('utf-8'))
            return

        # Endpoint GET /api/tts?text=...&voice=dalia
        if parsed.path == '/api/tts':
            qs = urllib.parse.parse_qs(parsed.query)
            text = qs.get('text', ['Hola, te hablo de Clínica Dental Cobá en Monterrey.'])[0]
            voice = qs.get('voice', ['dalia'])[0]
            eleven_key = qs.get('eleven_key', [''])[0]
            try:
                audio_data = synthesize_speech_bytes(text, voice, eleven_key)
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Content-Length', str(len(audio_data)))
                self.send_header('Cache-Control', 'public, max-age=86400')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(audio_data)
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            return

        if parsed.path == '/api/leads':
            ensure_crm_files()
            try:
                with open(JSON_CRM_PATH, 'r', encoding='utf-8') as f:
                    leads = json.load(f)
            except Exception:
                leads = []
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'count': len(leads), 'leads': leads}, ensure_ascii=False).encode('utf-8'))
            return

        if parsed.path == '/api/outreach-links':
            pitch_text = (
                "¡Hola equipo de Clínica Dental Cobá! 👋 Les escribo de AUTOMATIC, agencia de Ingeniería de Automatización e IA aquí en Monterrey. "
                "Vimos sus promociones de brackets de $1,999 y coronas de zirconia en Facebook y notamos que el link de su página web (clinicadentalcoba.com) está caído y marca error. "
                "Les construimos su nueva plataforma web completa con sus 2 sucursales (Jerónimo Treviño en MTY Centro y Benito Juárez en Guadalupe), cotizador de promociones y una recepcionista de Inteligencia Artificial por voz que llama al paciente en 10 segundos para confirmar su cita. "
                "¿A quién le comparto el enlace público para que la prueben desde su celular?"
            )
            encoded = urllib.parse.quote(pitch_text)
            data = {
                'agencia': 'AUTOMATIC — Ingeniería de Automatización & IA Monterrey',
                'prospecto_principal': 'Clínica Dental Cobá (Monterrey & Guadalupe)',
                'dominio_caido': 'clinicadentalcoba.com (NXDOMAIN)',
                'whatsapp_monterrey_link': f'https://wa.me/528118483941?text={encoded}',
                'whatsapp_guadalupe_link': f'https://wa.me/528180701778?text={encoded}',
                'instagram_dm': 'https://www.instagram.com/clinicadentalcoba/'
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
            return

        # Previsualización directa del Pase Digital / Correo HTML de la Cita
        if parsed.path in ('/api/email/preview', '/api/email/latest'):
            qs = urllib.parse.parse_qs(parsed.query)
            req_email = qs.get('email', [''])[0]

            target_file = os.path.join(EMAILS_DIR, 'latest.html')
            if req_email:
                safe = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', req_email)
                files = [f for f in os.listdir(EMAILS_DIR) if safe in f and f.endswith('.html')]
                if files:
                    files.sort(reverse=True)
                    target_file = os.path.join(EMAILS_DIR, files[0])

            if os.path.exists(target_file):
                with open(target_file, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b"<h1>No hay pase de cita registrado todavia. Envia una cita primero.</h1>")
            return

        # =========================================================================
        # ENDPOINTS DEL PORTAL MÉDICO COBÁ (PROTEGIDOS POR AUTENTICACIÓN)
        # =========================================================================

        # Verificación de sesión activa
        if parsed.path == '/api/doctor/session':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized', 'message': 'Sesión no válida o expirada.'}).encode('utf-8'))
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'user': user}).encode('utf-8'))
            return

        # Catálogo de especialistas médicos registrados
        if parsed.path == '/api/doctor/doctors':
            doctors = load_doctors()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'doctors': doctors}, ensure_ascii=False).encode('utf-8'))
            return

        # Obtener configuración global de clínica y personalización
        if parsed.path == '/api/doctor/config':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            config = load_clinic_config()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'config': config}, ensure_ascii=False).encode('utf-8'))
            return

        # Obtener inventario de insumos, costos por consulta y balance por doctor
        if parsed.path == '/api/doctor/inventory':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            inv_metrics = calculate_inventory_metrics()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(inv_metrics, ensure_ascii=False).encode('utf-8'))
            return

        # Generar y Descargar Documento PDF Oficial de Liquidación Quincenal de Doctor
        if parsed.path == '/api/doctor/payroll/pdf':
            # Aceptar token en cabecera o en query string para descarga directa
            user = validate_doctor_auth(self)
            if not user:
                query_params = urllib.parse.parse_qs(parsed.query)
                token_q = query_params.get('token', [''])[0]
                if token_q and token_q in SESSIONS:
                    user = SESSIONS[token_q]
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return

            query_params = urllib.parse.parse_qs(parsed.query)
            doc_id = query_params.get('doctor_id', ['doc-1'])[0]
            period = query_params.get('period', ['2ª Quincena Octubre 2026'])[0]

            try:
                pdf_bytes = pdf_receipt_service.generate_doctor_payroll_pdf(doc_id, period)
                clean_name = doc_id.replace(" ", "_")
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'attachment; filename="Liquidacion_{clean_name}_Octubre2026.pdf"')
                self.send_header('Content-Length', str(len(pdf_bytes)))
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(pdf_bytes)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
            return

        # Generar y Descargar Recibo Oficial de Honorarios para Paciente en PDF
        if parsed.path == '/api/doctor/patient/receipt-pdf':
            user = validate_doctor_auth(self)
            if not user:
                query_params = urllib.parse.parse_qs(parsed.query)
                token_q = query_params.get('token', [''])[0]
                if token_q and token_q in SESSIONS:
                    user = SESSIONS[token_q]
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return

            query_params = urllib.parse.parse_qs(parsed.query)
            appt_id = query_params.get('appointment_id', ['coba-1'])[0]

            try:
                pdf_bytes = pdf_receipt_service.generate_patient_receipt_pdf(appt_id)
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'attachment; filename="Recibo_Honorarios_Cobro_{appt_id}.pdf"')
                self.send_header('Content-Length', str(len(pdf_bytes)))
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(pdf_bytes)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
            return

        # Consultar Estado de Liquidaciones Quincenales
        if parsed.path == '/api/doctor/payroll/status':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            statuses = pdf_receipt_service.load_payroll_status()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'payroll_status': statuses}, ensure_ascii=False).encode('utf-8'))
            return

        # Consultar Historial y Resumen de Asistencia, Llegadas y Salidas con QR
        if parsed.path == '/api/doctor/attendance':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            qs = urllib.parse.parse_qs(parsed.query)
            doc_id = qs.get('doctor_id', ['all'])[0]
            status_f = qs.get('status', ['all'])[0]
            range_f = qs.get('range', ['all'])[0]
            summary = doctor_attendance_service.calculate_attendance_summary(doc_id, status_f, range_f)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(summary, ensure_ascii=False).encode('utf-8'))
            return

        # Consultar Gafete Digital y Código QR Personal de un Doctor
        if parsed.path == '/api/doctor/attendance/badge':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            qs = urllib.parse.parse_qs(parsed.query)
            doc_id = qs.get('doc_id', ['doc-1'])[0]
            badge_data = doctor_attendance_service.get_doctor_digital_badge(doc_id)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(badge_data, ensure_ascii=False).encode('utf-8'))
            return

        # Descargar Reporte PDF Formal de Asistencia de Doctores
        if parsed.path == '/api/doctor/attendance/pdf':
            user = validate_doctor_auth(self)
            if not user:
                qs = urllib.parse.parse_qs(parsed.query)
                token_q = qs.get('token', [''])[0]
                if token_q and token_q in DOCTOR_SESSIONS:
                    user = DOCTOR_SESSIONS[token_q]
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            qs = urllib.parse.parse_qs(parsed.query)
            doc_id = qs.get('doctor_id', ['all'])[0]
            try:
                pdf_bytes = doctor_attendance_service.generate_attendance_pdf(doc_id)
                self.send_response(200)
                self.send_header('Content-Type', 'application/pdf')
                self.send_header('Content-Disposition', f'attachment; filename="Reporte_Asistencia_{doc_id}.pdf"')
                self.send_header('Content-Length', str(len(pdf_bytes)))
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(pdf_bytes)
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
            return

        # Listado de citas para el doctor
        if parsed.path == '/api/doctor/appointments':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized', 'error': 'Acceso protegido. Datos clínicos sensibles.'}).encode('utf-8'))
                return

            ensure_crm_files()
            try:
                with open(JSON_CRM_PATH, 'r', encoding='utf-8') as f:
                    leads = json.load(f)
            except Exception:
                leads = []

            qs = urllib.parse.parse_qs(parsed.query)
            q_search = (qs.get('q', [''])[0]).strip().lower()
            q_status = (qs.get('status', [''])[0]).strip().lower()
            q_branch = (qs.get('sucursal', [''])[0]).strip()
            q_doctor = (qs.get('doctor', [''])[0]).strip()

            target_doc_name = None
            if q_doctor and q_doctor.lower() not in ('todos', 'todas', 'all', ''):
                d_norm = normalize_text_match(q_doctor)
                doctors = load_doctors()
                for d in doctors:
                    if d['id'].lower() == q_doctor.lower() or normalize_text_match(d['name']) == d_norm or d_norm in normalize_text_match(d['name']) or normalize_text_match(d['name']) in d_norm:
                        target_doc_name = normalize_text_match(d['name'])
                        break
                if not target_doc_name:
                    target_doc_name = d_norm

            filtered = []
            for l in reversed(leads):
                if q_search:
                    text_blob = f"{l.get('id', '')} {l.get('nombre', '')} {l.get('telefono', '')} {l.get('email', '')} {l.get('tratamiento', '')} {l.get('mensaje', '')}".lower()
                    if q_search not in text_blob:
                        continue
                if q_status and q_status not in ('todas', 'todos'):
                    if str(l.get('status', '')).lower() != q_status:
                        continue
                if q_branch and q_branch.lower() not in ('todas', 'todos', 'all'):
                    if normalize_text_match(q_branch) not in normalize_text_match(l.get('sucursal', '')):
                        continue
                if target_doc_name:
                    doc_str = normalize_text_match(l.get('doctor_asignado', ''))
                    if target_doc_name not in doc_str and doc_str not in target_doc_name:
                        continue
                filtered.append(l)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'count': len(filtered), 'total_original': len(leads), 'appointments': filtered, 'doctor': user.get('name')}, ensure_ascii=False).encode('utf-8'))
            return

        # Métricas y estadísticas clínicas en tiempo real
        if parsed.path == '/api/doctor/stats':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized', 'error': 'Acceso no autorizado.'}).encode('utf-8'))
                return

            ensure_crm_files()
            try:
                with open(JSON_CRM_PATH, 'r', encoding='utf-8') as f:
                    leads = json.load(f)
            except Exception:
                leads = []

            qs = urllib.parse.parse_qs(parsed.query)
            q_branch = (qs.get('sucursal', [''])[0]).strip()
            q_doctor = (qs.get('doctor', [''])[0]).strip()

            stats = compute_doctor_stats(leads, doctor_filter=q_doctor, branch_filter=q_branch)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'stats': stats, 'timestamp': datetime.now().isoformat()}, ensure_ascii=False).encode('utf-8'))
            return

        # Exportación de base de datos a CSV oficial
        if parsed.path == '/api/doctor/export-csv':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return

            ensure_crm_files()
            if os.path.exists(CSV_CRM_PATH):
                with open(CSV_CRM_PATH, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv; charset=utf-8-sig')
                self.send_header('Content-Disposition', 'attachment; filename="agenda_clinica_dental_coba.csv"')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()
            return

        # Previsualización de pase digital por ID de cita
        if parsed.path == '/api/doctor/pass-preview':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.end_headers()
                return

            qs = urllib.parse.parse_qs(parsed.query)
            cid = qs.get('id', [''])[0]
            ensure_crm_files()
            target_lead = None
            try:
                with open(JSON_CRM_PATH, 'r', encoding='utf-8') as f:
                    leads = json.load(f)
                for l in leads:
                    if str(l.get('id')) == str(cid):
                        target_lead = l
                        break
            except Exception:
                pass

            if target_lead:
                html = generate_digital_pass_html(target_lead)
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(html.encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(b"<h1>Cita no encontrada</h1>")
            return

        return super().do_GET()

    def do_POST(self):
        client_ip = self._get_client_ip()
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        # Reset rfile a un stream BytesIO para que los manejadores posteriores lean transparentemente
        self.rfile = io.BytesIO(post_data)

        parsed = urllib.parse.urlparse(self.path)

        # Inspección Activa de Ciberseguridad (WAF & Anti-Inyecciones)
        is_safe, block_info = cybersecurity_shield.inspect_request(
            client_ip=client_ip,
            method='POST',
            raw_path=self.path,
            headers=dict(self.headers),
            body_bytes=post_data if parsed.path != '/api/security/simulate-attack' else None
        )
        if not is_safe:
            status_code = block_info.get('status_code', 403)
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            if status_code == 429:
                self.send_header('Retry-After', '60')
            self._send_cors_headers()
            self.end_headers()
            resp_body = {
                'error': block_info.get('error', 'FORBIDDEN'),
                'reason': block_info.get('reason', 'Petición bloqueada por el Escudo de Ciberseguridad.'),
                'incident_id': block_info.get('incident_id', 'UNKNOWN'),
                'status': 'BLOCKED',
                'defense': 'Cobá Military-Grade WAF Shield'
            }
            self.wfile.write(json.dumps(resp_body, ensure_ascii=False).encode('utf-8'))
            return

        # Pen-Testing Seguro y Simulación de Ataques en Vivo
        if parsed.path == '/api/security/simulate-attack':
            try:
                payload = json.loads(post_data.decode('utf-8', errors='ignore')) if post_data else {}
            except Exception:
                payload = {}
            attack_type = payload.get('type') or urllib.parse.parse_qs(parsed.query).get('type', ['sqli'])[0]
            result = cybersecurity_shield.simulate_test_attack(attack_type)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
            return

        # Webhook POST oficial de Meta (Recepción de mensajes de WhatsApp)
        if parsed.path == '/webhook/whatsapp':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception:
                data = {}

            # Responder 200 OK inmediatamente a Meta
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "received"}).encode('utf-8'))

            # Procesar el mensaje con el agente conversacional
            extracted = whatsapp_bot_service.extract_meta_message(data)
            if extracted and extracted.get('text'):
                reply = whatsapp_bot_service.process_conversational_turn(
                    phone=extracted['phone'],
                    patient_name=extracted['name'],
                    user_text=extracted['text']
                )
                # Enviar respuesta saliente vía WhatsApp Cloud API
                whatsapp_bot_service.send_meta_outbound_whatsapp_message(
                    to_phone=extracted['phone'],
                    text_body=reply
                )
            return

        # Endpoint de simulación para pruebas en vivo desde el panel del doctor o frontend
        if parsed.path == '/api/whatsapp/simulate-incoming':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception:
                data = {}

            phone = data.get('phone', '+528118483941')
            name = data.get('name', 'Paciente WhatsApp')
            text_msg = data.get('text', 'Hola, quiero información.')

            ai_reply = whatsapp_bot_service.process_conversational_turn(
                phone=phone,
                patient_name=name,
                user_text=text_msg
            )
            clean_phone = re.sub(r'[^0-9+]', '', phone)
            session = whatsapp_bot_service.CONVERSATION_SESSIONS.get(clean_phone, {})

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "ok",
                "phone": phone,
                "name": name,
                "user_text": text_msg,
                "ai_reply": ai_reply,
                "extracted_lead": session.get("extracted", {}),
                "timestamp": datetime.now().isoformat()
            }, ensure_ascii=False).encode('utf-8'))
            return

        # Guardar credenciales de WhatsApp Cloud API
        if parsed.path == '/api/whatsapp/config':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
            except Exception:
                data = {}
            saved = whatsapp_bot_service.save_whatsapp_config(data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "message": "Configuración guardada", "config": saved}, ensure_ascii=False).encode('utf-8'))
            return

        if self.path == '/api/tts':
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
            text = body.get('text', '')
            voice = body.get('voice', 'dalia')
            eleven_key = body.get('eleven_key', '')
            try:
                audio_data = synthesize_speech_bytes(text, voice, eleven_key)
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mpeg')
                self.send_header('Content-Length', str(len(audio_data)))
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(audio_data)
            except Exception as e:
                self.send_response(500)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            return

        if self.path.startswith('/webhook/clinica-coba-leads') or self.path.startswith('/api/webhook/lead'):
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                payload = json.loads(raw_body)
            except Exception:
                payload = {}

            record = save_lead_to_crm(payload)
            ext = forward_to_external_integrations(record)

            response_data = {
                'status': 'success',
                'message': 'Lead registrado en CRM AUTOMATIC, correo generado y agente de voz disparado.',
                'lead': record,
                'integrations': ext,
                'email_preview_url': ext.get('email', {}).get('preview_url', f"/api/email/preview?email={urllib.parse.quote(record.get('email', ''))}")
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            print(f"[AUTOMATIC CRM] Nuevo registro: {record['nombre']} | {record['telefono']} | {record['email']} | Correo: {ext.get('email', {}).get('status')}")
            return

        if self.path == '/api/dental-chat':
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                data = json.loads(raw_body)
            except Exception:
                data = {}
            user_text = data.get('message', '')
            lead = data.get('lead') or {}
            ai_res = generate_dental_ai_response(user_text, lead)

            # Si el paciente confirmó en la llamada, actualizar CRM y despachar correo
            if ai_res.get('is_confirmed'):
                lead['estado_ia'] = 'Confirmado 100% por Voz Telefónica (Sofía)'
                save_lead_to_crm(lead)
                email_res = dispatch_confirmation_email(lead)
                ai_res['email'] = email_res

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(ai_res, ensure_ascii=False).encode('utf-8'))
            return

        if self.path == '/api/config/email':
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                new_cfg = json.loads(raw_body)
            except Exception:
                new_cfg = {}
            with open(EMAIL_CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(new_cfg, f, ensure_ascii=False, indent=2)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'message': 'Configuración de correo guardada con éxito.'}).encode('utf-8'))
            return

        # =========================================================================
        # ENDPOINTS POST/PUT/DELETE DEL PORTAL MÉDICO
        # =========================================================================

        # Login del Doctor / Clínica
        if self.path == '/api/doctor/login':
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
            username = (body.get('username') or body.get('email') or '').strip().lower()
            password = (body.get('password') or '').strip()
            pin = (body.get('pin') or '').strip()

            matched_user = None
            if username in DOCTOR_USERS and DOCTOR_USERS[username]['password'] == password:
                matched_user = DOCTOR_USERS[username]
            elif pin == '2026':
                matched_user = DOCTOR_USERS['doctor@coba.mx']

            if matched_user:
                token = f"coba_auth_{uuid.uuid4().hex}"
                user_info = {
                    'username': matched_user['email'],
                    'name': matched_user['name'],
                    'role': matched_user['role'],
                    'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                DOCTOR_SESSIONS[token] = user_info
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'token': token, 'user': user_info}).encode('utf-8'))
                print(f"[PORTAL MÉDICO COBÁ] Acceso autorizado: {user_info['name']} ({user_info['role']})")
            else:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': 'Credenciales o PIN incorrectos. Revisa usuario y contraseña.'}).encode('utf-8'))
            return

        # Logout del Doctor
        if self.path == '/api/doctor/logout':
            auth_header = self.headers.get('Authorization', '')
            token = auth_header[7:].strip() if auth_header.startswith('Bearer ') else ''
            if token and token in DOCTOR_SESSIONS:
                del DOCTOR_SESSIONS[token]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'message': 'Sesión cerrada con éxito.'}).encode('utf-8'))
            return

        # Crear nueva cita manual desde el portal médico
        if self.path == '/api/doctor/appointments':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return

            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                payload = json.loads(raw_body)
            except Exception:
                payload = {}

            new_id = f"coba-{int(time.time() * 1000)}"
            payload['id'] = new_id
            payload['source'] = 'Portal Médico Directo (Recepción Cobá)'
            payload['estado_ia'] = 'Agendada Manualmente por Doctor'
            payload['doctor_asignado'] = payload.get('doctor_asignado') or user.get('name', 'Dr. Mauricio Cobá')
            payload['status'] = payload.get('status') or 'Confirmada'

            record = save_lead_to_crm(payload)
            if payload.get('send_email') and payload.get('email'):
                try:
                    dispatch_confirmation_email(record)
                except Exception as e:
                    print(f"[PORTAL MÉDICO] Error despachando correo de pase: {e}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'appointment': record, 'message': 'Cita registrada y confirmada en sistema.'}, ensure_ascii=False).encode('utf-8'))
            print(f"[PORTAL MÉDICO] Nueva cita anotada: {record['nombre']} | {record['fecha_cita']} {record['hora_cita']} | {record['tratamiento']}")
            return

        # Actualizar cita existente (cambiar status, fecha, notas, etc.)
        if self.path in ('/api/doctor/appointments/update', '/api/doctor/appointment/update'):
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return

            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            target_id = body.get('id')
            if not target_id:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': 'ID de cita requerido.'}).encode('utf-8'))
                return

            ensure_crm_files()
            updated_record = None
            try:
                with open(JSON_CRM_PATH, 'r', encoding='utf-8') as f:
                    leads = json.load(f)
                for l in leads:
                    if str(l.get('id')) == str(target_id):
                        if 'status' in body:
                            l['status'] = body['status']
                        if 'doctor_asignado' in body:
                            l['doctor_asignado'] = body['doctor_asignado']
                        if 'fecha_cita' in body:
                            l['fecha_cita'] = body['fecha_cita']
                        if 'hora_cita' in body:
                            l['hora_cita'] = body['hora_cita']
                        if 'sucursal' in body:
                            l['sucursal'] = body['sucursal']
                        if 'mensaje' in body:
                            l['mensaje'] = body['mensaje']
                        updated_record = l
                        break
                if updated_record:
                    with open(JSON_CRM_PATH, 'w', encoding='utf-8') as f:
                        json.dump(leads, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[PORTAL MÉDICO] Error actualizando cita: {e}")

            if updated_record:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'appointment': updated_record, 'message': 'Cita actualizada con éxito.'}, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'not_found', 'message': 'Cita no encontrada.'}).encode('utf-8'))
            return

        # Eliminar / archivar cita
        if self.path in ('/api/doctor/appointments/delete', '/api/doctor/appointment/delete'):
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return

            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            target_id = body.get('id')
            ensure_crm_files()
            found = False
            try:
                with open(JSON_CRM_PATH, 'r', encoding='utf-8') as f:
                    leads = json.load(f)
                new_leads = [l for l in leads if str(l.get('id')) != str(target_id)]
                if len(new_leads) < len(leads):
                    found = True
                    with open(JSON_CRM_PATH, 'w', encoding='utf-8') as f:
                        json.dump(new_leads, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"[PORTAL MÉDICO] Error eliminando cita: {e}")

            self.send_response(200 if found else 404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok' if found else 'not_found', 'deleted_id': target_id}).encode('utf-8'))
            return

        # Registrar nuevo doctor
        if self.path in ('/api/doctor/doctors', '/api/doctor/doctors/create'):
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return

            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            name = body.get('name', '').strip()
            if not name:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': 'Nombre del doctor requerido.'}).encode('utf-8'))
                return

            doctors = load_doctors()
            new_id = f"doc-{len(doctors) + 1}"
            initials = ''.join([w[0] for w in name.replace('Dr.', '').replace('Dra.', '').strip().split()[:2]]).upper() or 'DR'
            colors = ['#06B6D4', '#10B981', '#EC4899', '#8B5CF6', '#F59E0B', '#3B82F6', '#14B8A6']
            color = body.get('color') or random.choice(colors)
            
            photo = body.get('photo', '').strip()
            if not photo:
                photo = f"https://ui-avatars.com/api/?name={urllib.parse.quote(name)}&background=0F172A&color=06B6D4&size=400&bold=true"

            new_doctor = {
                'id': new_id,
                'name': name,
                'specialty': body.get('specialty', 'Especialista Dental'),
                'cedula': body.get('cedula', 'Ced. Prof. en trámite'),
                'phone': body.get('phone', '+52 81 0000 0000'),
                'email': body.get('email', f"{name.lower().replace(' ', '')}@coba.mx"),
                'branch': body.get('branch', 'Monterrey Centro (Jerónimo Treviño #1111 Pte.)'),
                'color': color,
                'avatar': initials,
                'photo': photo,
                'bio': body.get('bio', 'Especialista clínico integrado al equipo de Clínica Dental Cobá.'),
                'status': 'Activo'
            }
            doctors.append(new_doctor)
            save_doctors(doctors)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'doctor': new_doctor, 'message': f'{name} registrado con éxito.'}, ensure_ascii=False).encode('utf-8'))
            print(f"[PORTAL MÉDICO] Nuevo especialista registrado: {name} | {new_doctor['specialty']}")
            return

        # Actualizar perfil y foto de doctor
        if self.path in ('/api/doctor/doctors/update', '/api/doctor/doctor/update'):
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return

            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            target_id = body.get('id')
            doctors = load_doctors()
            updated_doc = None
            for d in doctors:
                if d.get('id') == target_id or d.get('name') == body.get('name'):
                    allowed_fields = (
                        'name', 'title', 'specialty', 'subspecialties', 'cedula', 'cedula_esp',
                        'phone', 'email', 'branch', 'unidad_clinica', 'color', 'photo',
                        'universidad_lic', 'posgrado', 'anos_experiencia', 'certificaciones',
                        'idiomas', 'dias_consulta', 'horario_consulta', 'duracion_cita_promedio',
                        'asistente_dental', 'comision_pct', 'banco', 'cuenta_clabe', 'rfc',
                        'tipo_contrato', 'filosofia', 'bio'
                    )
                    for k in allowed_fields:
                        if k in body and body[k] is not None:
                            d[k] = body[k]
                    updated_doc = d
                    break

            if updated_doc:
                save_doctors(doctors)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'doctor': updated_doc, 'message': 'Perfil de doctor actualizado.'}, ensure_ascii=False).encode('utf-8'))
                print(f"[PORTAL MÉDICO] Perfil actualizado para: {updated_doc['name']}")
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'not_found', 'message': 'Doctor no encontrado.'}).encode('utf-8'))
            return

        # Guardar configuración global de clínica y personalización
        if self.path == '/api/doctor/config':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
            saved = save_clinic_config(body)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'config': saved, 'message': 'Configuración de clínica guardada con éxito.'}, ensure_ascii=False).encode('utf-8'))
            return

        # Actualizar precio unitario de un insumo y recalcular balances
        if self.path == '/api/doctor/inventory/price':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
            item_id = body.get('id')
            new_price = body.get('cost_unit')
            if not item_id or new_price is None:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': 'ID y precio requeridos'}).encode('utf-8'))
                return
            update_supply_price(item_id, new_price)
            fresh_metrics = calculate_inventory_metrics()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'message': 'Precio de insumo reajustado con éxito.', 'data': fresh_metrics}, ensure_ascii=False).encode('utf-8'))
            return

        # Guardar o crear insumo en el inventario
        if self.path == '/api/doctor/inventory/item':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
            saved_item = save_or_create_supply(body)
            fresh_metrics = calculate_inventory_metrics()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'message': 'Insumo guardado en inventario.', 'item': saved_item, 'data': fresh_metrics}, ensure_ascii=False).encode('utf-8'))
            return

        # Eliminar insumo del inventario
        if self.path == '/api/doctor/inventory/delete':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
            item_id = body.get('id')
            deleted = delete_supply(item_id)
            fresh_metrics = calculate_inventory_metrics()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok' if deleted else 'not_found', 'message': 'Insumo eliminado del inventario.' if deleted else 'Insumo no encontrado.', 'data': fresh_metrics}, ensure_ascii=False).encode('utf-8'))
            return

        # Ajustar stock físico de un insumo
        if self.path == '/api/doctor/inventory/stock':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
            item_id = body.get('id')
            new_stock = body.get('stock_current')
            update_supply_stock(item_id, new_stock)
            fresh_metrics = calculate_inventory_metrics()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'message': 'Stock actualizado.', 'data': fresh_metrics}, ensure_ascii=False).encode('utf-8'))
            return

        # Registrar Liquidación Oficial de Honorarios de Doctor
        if self.path == '/api/doctor/payroll/liquidate':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
            doc_id = body.get('doctor_id', 'doc-1')
            payment_method = body.get('payment_method', 'Transferencia Bancaria SPEI')
            notes = body.get('notes', '')

            liq_record = pdf_receipt_service.record_liquidation(doc_id, payment_method, notes)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'message': f'Doctor {doc_id} liquidado con éxito.', 'liquidation': liq_record}, ensure_ascii=False).encode('utf-8'))
            return

        # Registrar Checada de Llegada o Salida con Código QR de Doctor
        if self.path == '/api/doctor/attendance/scan':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
            identifier = body.get('identifier', '').strip()
            method = body.get('method', 'qr_mobile')
            notes = body.get('notes', '')
            if not identifier:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'message': 'Identificador o token QR del doctor requerido.'}).encode('utf-8'))
                return
            scan_res = doctor_attendance_service.record_attendance_scan(identifier, method, notes)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(scan_res, ensure_ascii=False).encode('utf-8'))
            return

        # Justificar inasistencia o retardo de doctor
        if self.path == '/api/doctor/attendance/justify':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'unauthorized'}).encode('utf-8'))
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}
            record_id = body.get('record_id', '')
            reason = body.get('reason', 'Permiso justificado por Dirección Médica')
            just_res = doctor_attendance_service.justify_attendance_record(record_id, reason)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(just_res, ensure_ascii=False).encode('utf-8'))
            return

        # Enviar Consentimiento Informado NOM-004 (Previo a cita o Copia Firmada Digitalmente)
        if self.path == '/api/doctor/send-consent':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.end_headers()
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            folio = body.get('folio') or f"NOM004-{int(time.time())}"
            body['folio'] = folio
            email = (body.get('email') or '').strip()
            is_signed = bool(body.get('is_signed', True))
            html_content = build_informed_consent_email_html(body)
            subject = (
                f"🛡️ Copia Certificada de Consentimiento Informado Firmado (#{folio}) — Clínica Dental Cobá"
                if is_signed else
                f"📋 Consentimiento Informado Pre-Consulta (#{folio}) — Clínica Dental Cobá"
            )
            plain_text = f"Consentimiento Informado NOM-004-SSA3 Folio {folio} para {body.get('patient_name', 'Paciente')} - {body.get('tratamiento', 'Tratamiento Dental')}."
            email_res = dispatch_custom_clinical_email(email, subject, html_content, plain_text, tag_prefix='consent_nom004')

            # Guardar registro en consents.json
            consents_path = os.path.join(AUTOMATION_DIR, 'consents_log.json')
            consents = []
            if os.path.exists(consents_path):
                try:
                    with open(consents_path, 'r', encoding='utf-8') as f:
                        consents = json.load(f)
                except Exception:
                    consents = []
            record = {
                'folio': folio,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'patient_name': body.get('patient_name', 'Paciente'),
                'email': email,
                'doctor_name': body.get('doctor_name', 'Dr. Mauricio Cobá'),
                'tratamiento': body.get('tratamiento', ''),
                'sucursal': body.get('sucursal', ''),
                'is_signed': is_signed,
                'email_status': email_res.get('status', 'generated')
            }
            consents.insert(0, record)
            with open(consents_path, 'w', encoding='utf-8') as f:
                json.dump(consents[:200], f, ensure_ascii=False, indent=2)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'folio': folio,
                'email_result': email_res,
                'record': record,
                'message': f"Consentimiento #{folio} procesado y enviado a {email}."
            }, ensure_ascii=False).encode('utf-8'))
            return

        # Enviar correo de seguimiento por caso (Endodoncia sin corona, Control Ortodoncia, Clientes Fallidos VIP)
        if self.path == '/api/doctor/send-followup-email':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.end_headers()
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            recipients = body.get('recipients')
            results = []
            if isinstance(recipients, list) and len(recipients) > 0:
                for item in recipients:
                    item_data = dict(body)
                    item_data.update(item)
                    rec_email = (item_data.get('email') or '').strip()
                    case_type = item_data.get('case_type', 'cliente_fallido_vip')
                    html_c = build_followup_email_html(item_data)
                    if case_type == 'endodoncia_sin_corona':
                        subj = f"⚠️ {item_data.get('patient_name', 'Paciente')}: Protege tu Endodoncia con tu Corona de Zirconia (Bono VIP)"
                    elif case_type == 'ortodoncia_control':
                        subj = f"🦷 {item_data.get('patient_name', 'Paciente')}: Recordatorio de tu Control Mensual de Ortodoncia y Brackets"
                    else:
                        subj = f"👑 {item_data.get('patient_name', 'Paciente')}: Tienes un Pase de Trato Preferencial Único en Clínica Dental Cobá"
                    res = dispatch_custom_clinical_email(rec_email, subj, html_c, subj, tag_prefix=f"followup_{case_type}")
                    results.append({'patient_name': item_data.get('patient_name'), 'email': rec_email, 'result': res})
            else:
                rec_email = (body.get('email') or '').strip()
                case_type = body.get('case_type', 'endodoncia_sin_corona')
                html_c = build_followup_email_html(body)
                if case_type == 'endodoncia_sin_corona':
                    subj = f"⚠️ {body.get('patient_name', 'Paciente')}: Protege tu Endodoncia con tu Corona de Zirconia (Bono VIP)"
                elif case_type == 'ortodoncia_control':
                    subj = f"🦷 {body.get('patient_name', 'Paciente')}: Recordatorio de tu Control Mensual de Ortodoncia y Brackets"
                else:
                    subj = f"👑 {body.get('patient_name', 'Paciente')}: Tienes un Pase de Trato Preferencial Único en Clínica Dental Cobá"
                res = dispatch_custom_clinical_email(rec_email, subj, html_c, subj, tag_prefix=f"followup_{case_type}")
                results.append({'patient_name': body.get('patient_name'), 'email': rec_email, 'result': res})

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'sent_count': len(results),
                'results': results,
                'message': f"Se despacharon {len(results)} correo(s) de seguimiento clínico preferencial."
            }, ensure_ascii=False).encode('utf-8'))
            return

        # Lista de Espera Inteligente: Llamada IA Sofía + Correo Urgente para recuperar tiempo muerto
        if self.path == '/api/doctor/waitlist-blast':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.end_headers()
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            nombre = body.get('patient_name', 'Paciente en Lista de Espera')
            email = (body.get('email') or '').strip()
            telefono = (body.get('telefono') or '').strip()
            doctor = body.get('doctor_name', 'Dr. Mauricio Cobá')
            fecha = body.get('fecha_liberada', 'Hoy')
            hora = body.get('hora_liberada', '04:00 PM')
            sucursal = body.get('sucursal', 'Monterrey Centro')
            tratamiento = body.get('tratamiento', 'Consulta de Especialidad')

            # 1. Despachar correo urgente
            html_c = build_waitlist_recovery_email_html(body)
            subj = f"⚡ ¡Espacio Liberado Hoy ({hora}) con {doctor}! — Clínica Dental Cobá"
            email_res = dispatch_custom_clinical_email(email, subj, html_c, subj, tag_prefix='waitlist_recovery')

            # 2. Preparar script de llamada de voz IA (Sofía) y URL de audio neural en vivo
            voice_script = (
                f"Hola {nombre.split()[0]}, te habla Sofía, asistente de Clínica Dental Cobá en {sucursal.split('(')[0].strip()}. "
                f"Te marco de urgencia porque un paciente acaba de cancelar su cita de hoy a las {hora} con {doctor}, "
                f"y como estás en nuestra lista de espera prioritaria para tu {tratamiento}, te guardé el lugar a ti primero. "
                f"También te acabo de mandar los detalles a tu correo. ¿Confirmamos tu asistencia para pasarte directo sin fila?"
            )
            tts_url = f"/api/tts?voice=dalia&text={urllib.parse.quote(voice_script)}"

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'patient_name': nombre,
                'telefono': telefono,
                'email': email,
                'email_result': email_res,
                'voice_call': {
                    'status': 'calling',
                    'agent': 'Sofía IA (Voz Neural es-MX-Dalia)',
                    'script': voice_script,
                    'tts_audio_url': tts_url
                },
                'message': f"Llamada IA iniciada a {telefono} y correo urgente enviado a {email}."
            }, ensure_ascii=False).encode('utf-8'))
            return

        # Enviar solicitud de Reseña 5 Estrellas en Google Maps
        if self.path == '/api/doctor/send-review-request':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.end_headers()
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            email = (body.get('email') or '').strip()
            nombre = body.get('patient_name', 'Paciente')
            doctor = body.get('doctor_name', 'Dr. Mauricio Cobá')
            html_c = build_google_review_email_html(body)
            subj = f"⭐⭐⭐⭐⭐ {nombre}, ¿cómo fue tu experiencia hoy con {doctor} en Clínica Dental Cobá?"
            email_res = dispatch_custom_clinical_email(email, subj, html_c, subj, tag_prefix='google_maps_review')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'email_result': email_res,
                'message': f"Invitación a reseña en Google Maps enviada a {email}."
            }, ensure_ascii=False).encode('utf-8'))
            return

        # Guardar Odontograma Clínico y opcionalmente enviar presupuesto por correo
        if self.path == '/api/doctor/odontogram/save':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.end_headers()
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            odontograms_path = os.path.join(AUTOMATION_DIR, 'odontograms.json')
            odontograms = []
            if os.path.exists(odontograms_path):
                try:
                    with open(odontograms_path, 'r', encoding='utf-8') as f:
                        odontograms = json.load(f)
                except Exception:
                    odontograms = []

            record = {
                'id': f"odo-{int(time.time())}",
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'patient_name': body.get('patient_name', 'Paciente General'),
                'patient_age': body.get('patient_age', 30),
                'dentition_type': body.get('dentition_type', 'hombre'),
                'doctor_name': body.get('doctor_name', 'Dr. Mauricio Cobá'),
                'sucursal': body.get('sucursal', 'Monterrey Centro'),
                'email': body.get('email', ''),
                'teeth_state': body.get('teeth_state', {}),
                'treatments_summary': body.get('treatments_summary', []),
                'total_budget_mxn': body.get('total_budget_mxn', 0)
            }
            odontograms.insert(0, record)
            with open(odontograms_path, 'w', encoding='utf-8') as f:
                json.dump(odontograms[:200], f, ensure_ascii=False, indent=2)

            email_res = None
            if body.get('send_email') and body.get('email'):
                items_html = "".join([
                    f"<tr><td style='padding:8px;border-bottom:1px solid rgba(255,255,255,0.08);'>Pieza #{it.get('tooth')} ({it.get('name','')})</td>"
                    f"<td style='padding:8px;border-bottom:1px solid rgba(255,255,255,0.08);color:#38BDF8;font-weight:700;'>{it.get('state_label')}</td>"
                    f"<td style='padding:8px;border-bottom:1px solid rgba(255,255,255,0.08);text-align:right;color:#10B981;font-weight:700;'>${it.get('price',0):,} MXN</td></tr>"
                    for it in record['treatments_summary']
                ]) or "<tr><td colspan='3' style='padding:10px;text-align:center;'>Revisión preventiva general</td></tr>"
                odo_html = f"""<!DOCTYPE html><html lang="es"><body style="margin:0;padding:24px;background:#050507;color:#fff;font-family:sans-serif;">
                <div style="max-width:600px;margin:0 auto;background:#0e1722;border:1px solid rgba(6,182,212,0.45);border-radius:18px;padding:26px;">
                  <div style="color:#06B6D4;font-size:11px;font-weight:800;text-transform:uppercase;">🦷 PLAN DE TRATAMIENTO Y ODONTOGRAMA DIGITAL</div>
                  <h2 style="margin:8px 0 14px;color:#fff;">Paciente: {record['patient_name']} ({record['dentition_type'].upper()})</h2>
                  <p style="font-size:13px;color:#CBD5E1;">Especialista: <strong>{record['doctor_name']}</strong> &bull; Sucursal: {record['sucursal']}</p>
                  <table width="100%" cellspacing="0" cellpadding="0" style="font-size:13px;color:#E2E8F0;margin:16px 0;">
                    <thead><tr style="color:#94A3B8;text-align:left;"><th style="padding:8px;">Pieza Dental</th><th style="padding:8px;">Diagnóstico / Tratamiento</th><th style="padding:8px;text-align:right;">Inversión</th></tr></thead>
                    <tbody>{items_html}</tbody>
                  </table>
                  <div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.4);border-radius:12px;padding:14px;text-align:right;font-size:16px;font-weight:800;color:#10B981;">
                    Presupuesto Total Estimado: ${record['total_budget_mxn']:,} MXN
                  </div>
                </div></body></html>"""
                subj = f"🦷 Tu Odontograma Digital y Plan Dental — Clínica Dental Cobá (${record['total_budget_mxn']:,} MXN)"
                email_res = dispatch_custom_clinical_email(body['email'], subj, odo_html, subj, tag_prefix='odontogram_plan')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'odontogram': record,
                'email_result': email_res,
                'message': 'Odontograma guardado en expediente clínico.'
            }, ensure_ascii=False).encode('utf-8'))
            return

        # Enviar Receta Médica Oficial e Indicaciones Post-Operatorias por Correo
        if self.path == '/api/doctor/send-prescription':
            user = validate_doctor_auth(self)
            if not user:
                self.send_response(401)
                self.end_headers()
                return
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8', errors='ignore') if content_length > 0 else '{}'
            try:
                body = json.loads(raw_body)
            except Exception:
                body = {}

            folio = f"RX-{int(time.time())}"
            nombre = body.get('patient_name', 'Paciente')
            email = (body.get('email') or '').strip()
            doctor = body.get('doctor_name', 'Dr. Mauricio Cobá')
            cedula = body.get('doctor_cedula', 'Ced. Prof. 8492019 • SSA 39482')
            sucursal = body.get('sucursal', 'Monterrey Centro')
            meds = body.get('medications', '')
            postop = body.get('postop_care', '')

            rx_html = f"""<!DOCTYPE html><html lang="es"><body style="margin:0;padding:24px;background:#050507;color:#fff;font-family:sans-serif;">
            <div style="max-width:600px;margin:0 auto;background:#0e1722;border:1px solid rgba(6,182,212,0.5);border-radius:18px;padding:28px;">
              <div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:16px;margin-bottom:18px;">
                <div>
                  <div style="color:#06B6D4;font-size:11px;font-weight:800;text-transform:uppercase;">💊 RECETA MÉDICA ODONTOLÓGICA E INDICACIONES POST-OPERATORIAS</div>
                  <h2 style="margin:6px 0 4px;color:#fff;">Clínica Dental Cobá Monterrey</h2>
                  <div style="font-size:12px;color:#94A3B8;">{doctor} &bull; {cedula} &bull; {sucursal}</div>
                </div>
                <div style="background:rgba(6,182,212,0.15);border:1px solid #06B6D4;color:#38BDF8;padding:6px 12px;border-radius:8px;font-size:12px;font-weight:800;">Folio #{folio}</div>
              </div>
              <p style="font-size:14px;color:#E2E8F0;"><strong>👤 Paciente:</strong> {nombre} &bull; <strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
              <div style="background:rgba(15,23,42,0.9);border:1px solid rgba(6,182,212,0.35);border-radius:12px;padding:16px;margin:16px 0;">
                <div style="color:#38BDF8;font-size:12px;font-weight:800;text-transform:uppercase;margin-bottom:8px;">℞ Esquema Farmacológico Indicado:</div>
                <div style="font-size:13px;color:#F8FAFC;line-height:1.6;white-space:pre-line;">{meds}</div>
              </div>
              <div style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.35);border-radius:12px;padding:16px;margin:16px 0;">
                <div style="color:#10B981;font-size:12px;font-weight:800;text-transform:uppercase;margin-bottom:8px;">🛡️ Cuidados Post-Operatorios en Casa:</div>
                <div style="font-size:13px;color:#CBD5E1;line-height:1.6;white-space:pre-line;">{postop}</div>
              </div>
              <div style="font-size:11px;color:#64748B;text-align:center;margin-top:20px;">Documento médico expedido conforme a la NOM-004-SSA3-2012 &bull; Urgencias 24/7: +52 81 1848 3941</div>
            </div></body></html>"""
            subj = f"💊 Receta Médica #{folio} y Cuidados Post-Operatorios — {doctor} (Clínica Dental Cobá)"
            email_res = dispatch_custom_clinical_email(email, subj, rx_html, meds, tag_prefix='prescription_rx')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'folio': folio,
                'email_result': email_res,
                'message': f"Receta #{folio} enviada al correo {email}."
            }, ensure_ascii=False).encode('utf-8'))
            return

        self.send_response(404)
        self._send_cors_headers()
        self.end_headers()

    def do_PUT(self):
        if self.path.startswith('/api/doctor/appointments'):
            self.path = '/api/doctor/appointments/update'
            return self.do_POST()
        self.send_response(404)
        self._send_cors_headers()
        self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/api/doctor/appointments'):
            self.path = '/api/doctor/appointments/delete'
            return self.do_POST()
        self.send_response(404)
        self._send_cors_headers()
        self.end_headers()


if __name__ == '__main__':
    ensure_crm_files()
    port = int(os.environ.get('PORT', 8090))
    server = ThreadingHTTPServer(('0.0.0.0', port), UnifiedAgencyHandler)
    print(f"==================================================================")
    print(f"⚡ AUTOMATIC AGENCY + CLÍNICA DENTAL COBÁ MONTERREY — SERVER ONLINE")
    print(f"🎙️ Motor Neural de Voz Femenina Natural (/api/tts): ACTIVO")
    print(f"🏛️ Agencia AUTOMATIC (Con Comercial): http://localhost:{port}/automatic/")
    print(f"🦷 Demo Cliente Clínica Dental Cobá:  http://localhost:{port}/clinica-coba/")
    print(f"==================================================================")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
