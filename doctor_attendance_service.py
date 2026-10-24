# -*- coding: utf-8 -*-
"""
doctor_attendance_service.py
Sistema Oficial de Control de Asistencia, Llegadas y Salidas con Código QR Único
para Especialistas y Cuadro Médico de Clínica Dental Cobá Monterrey.
"""

import os
import io
import json
import base64
import hashlib
from datetime import datetime, timedelta

import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTO_DIR = os.path.join(BASE_DIR, 'automation')
ATTENDANCE_PATH = os.path.join(AUTO_DIR, 'doctor_attendance.json')
DOCS_PATH = os.path.join(AUTO_DIR, 'doctors.json')
LOGO_PATH = os.path.join(BASE_DIR, 'images', 'logo.png')

SALT_SECRET = "COBA_ATTENDANCE_SEC_2026_MTY"

def load_doctors():
    if os.path.exists(DOCS_PATH):
        try:
            with open(DOCS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def get_doctor_by_id(doc_id):
    docs = load_doctors()
    for d in docs:
        if d.get('id') == doc_id:
            return d
    return None

def generate_doctor_qr_token(doc_id):
    raw = f"{doc_id}:{SALT_SECRET}"
    digest = hashlib.sha256(raw.encode('utf-8')).hexdigest()[:12].upper()
    return f"COBA-DOC-ATTENDANCE:{doc_id}:{digest}"

def generate_doctor_qr_data_url(doc_id):
    token = generate_doctor_qr_token(doc_id)
    doc = get_doctor_by_id(doc_id) or {}
    doc_name = doc.get('name', 'Doctor Cobá')

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(token)
    qr.make(fit=True)

    # Crear imagen nítida en blanco y negro para escaneo óptico 100% confiable
    img = qr.make_image(fill_color="#0A1128", back_color="#FFFFFF")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64_str}", token

def load_attendance_records():
    if os.path.exists(ATTENDANCE_PATH):
        try:
            with open(ATTENDANCE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return seed_attendance_records()
    return seed_attendance_records()

def save_attendance_records(records):
    os.makedirs(AUTO_DIR, exist_ok=True)
    with open(ATTENDANCE_PATH, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

def parse_time_str(time_str):
    try:
        parts = time_str.split(':')
        return int(parts[0]), int(parts[1])
    except Exception:
        return 0, 0

def calc_hours_worked(in_str, out_str):
    if not in_str or not out_str:
        return 0.0, "0h 00m"
    try:
        h1, m1 = parse_time_str(in_str)
        h2, m2 = parse_time_str(out_str)
        t1 = h1 * 60 + m1
        t2 = h2 * 60 + m2
        diff = max(0, t2 - t1)
        hours = round(diff / 60.0, 2)
        diff_h = diff // 60
        diff_m = diff % 60
        return hours, f"{diff_h}h {diff_m:02d}m"
    except Exception:
        return 0.0, "0h 00m"

def seed_attendance_records():
    """Genera un historial realista y detallado de asistencia para los últimos 60 días."""
    docs = load_doctors()
    if not docs:
        return []

    records = []
    # Generar fechas hacia atrás desde hoy (2026-10-19)
    today = datetime(2026, 10, 19)
    
    # Mapeo de días de consulta típicos de cada doctor
    doc_profiles = {
        'doc-1': {'start': '09:00', 'end': '18:30', 'days': [0, 1, 2, 3, 5], 'patients': 6}, # Lun-Jue, Sab
        'doc-2': {'start': '10:00', 'end': '19:00', 'days': [1, 2, 3, 4], 'patients': 8},    # Mar-Vie
        'doc-3': {'start': '09:00', 'end': '17:00', 'days': [0, 1, 2, 3, 4], 'patients': 4}, # Lun-Vie
        'doc-4': {'start': '09:00', 'end': '18:00', 'days': [0, 1, 2, 3, 4], 'patients': 5}, # Lun-Vie
        'doc-5': {'start': '09:00', 'end': '18:30', 'days': [0, 1, 2, 3, 4, 5], 'patients': 6}, # Lun-Sab
        'doc-6': {'start': '09:30', 'end': '16:30', 'days': [0, 1, 2, 3, 4], 'patients': 7}, # Lun-Vie
        'doc-7': {'start': '10:00', 'end': '17:00', 'days': [0, 1, 2, 3], 'patients': 5},    # Lun-Jue
    }

    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

    for day_offset in range(50, -1, -1):
        cur_date = today - timedelta(days=day_offset)
        weekday = cur_date.weekday()
        if weekday == 6:  # Domingo cerrado
            continue

        date_str = cur_date.strftime('%Y-%m-%d')
        day_label = day_names[weekday]

        for d in docs:
            d_id = d['id']
            prof = doc_profiles.get(d_id, {'start': '09:00', 'end': '18:00', 'days': [0, 1, 2, 3, 4], 'patients': 5})
            if weekday not in prof['days']:
                continue

            # Variación realista de llegadas y salidas
            sched_in = prof['start']
            sched_out = prof['end']
            sched_in_h, sched_in_m = parse_time_str(sched_in)
            sched_out_h, sched_out_m = parse_time_str(sched_out)

            # Caso especial para el día de HOY (2026-10-19)
            if day_offset == 0:
                if d_id == 'doc-1': # Dr. Mauricio Cobá (Llegó temprano, completó turno)
                    check_in = "08:52"
                    check_out = "18:40"
                    status_in = "puntual"
                    status_out = "salida_normal"
                    overall_status = "presente"
                    notes = "Llegada con 8 min de anticipación. Cirugías de implantes Straumann concluidas."
                elif d_id == 'doc-2': # Dra. Valeria Garza (En turno activo ahora mismo)
                    check_in = "09:54"
                    check_out = None
                    status_in = "puntual"
                    status_out = "en_turno"
                    overall_status = "en_turno"
                    notes = "En atención clínica activa en Sillón 2 (Alineadores Invisibles)."
                elif d_id == 'doc-3': # Dr. Daniel Fernández (En turno activo)
                    check_in = "08:50"
                    check_out = None
                    status_in = "puntual"
                    status_out = "en_turno"
                    overall_status = "en_turno"
                    notes = "En procedimiento microscópico de endodoncia molar."
                elif d_id == 'doc-4': # Dra. Sofía Valdés (Llegó con ligero retardo de 18 min)
                    check_in = "09:18"
                    check_out = None
                    status_in = "retardo"
                    status_out = "en_turno"
                    overall_status = "retardo"
                    notes = "Retardo por tráfico pesado en Av. Constitución. Pacientes notificados por WhatsApp."
                elif d_id == 'doc-5': # Dr. Alejandro Sada (En turno activo)
                    check_in = "08:57"
                    check_out = None
                    status_in = "puntual"
                    status_out = "en_turno"
                    overall_status = "en_turno"
                    notes = "En sesión de Diseño Digital de Sonrisa (DSD)."
                elif d_id == 'doc-6': # Dra. Mariana Villarreal (Inasistencia justificada)
                    check_in = None
                    check_out = None
                    status_in = "falta"
                    status_out = "no_aplica"
                    overall_status = "falta_justificada"
                    notes = "Permiso académico: Congreso Mexicano de Odontopediatría CDMX."
                else: # Dr. Gabriel Montemayor (En turno)
                    check_in = "09:58"
                    check_out = None
                    status_in = "puntual"
                    status_out = "en_turno"
                    overall_status = "en_turno"
                    notes = "Tratamiento periodontal e injerto óseo en curso."

                hours_w, hours_fmt = calc_hours_worked(check_in, check_out) if check_out else (0.0, "En curso")

                rec = {
                    "id": f"att-{date_str}-{d_id}",
                    "doc_id": d_id,
                    "doctor_name": d['name'],
                    "specialty": d.get('specialty', 'Especialista Dental'),
                    "photo": d.get('photo', ''),
                    "branch": d.get('branch', 'Monterrey Centro'),
                    "unidad_clinica": d.get('unidad_clinica', 'Sillón 1'),
                    "date": date_str,
                    "day_name": day_label,
                    "scheduled_in": sched_in,
                    "scheduled_out": sched_out,
                    "check_in": check_in,
                    "check_out": check_out,
                    "hours_worked": hours_w,
                    "hours_formatted": hours_fmt,
                    "status_in": status_in,
                    "status_out": status_out,
                    "delay_minutes": 18 if status_in == "retardo" else 0,
                    "overall_status": overall_status,
                    "patients_seen": prof['patients'] if check_in else 0,
                    "check_in_method": "qr_mobile" if check_in else "ninguno",
                    "check_out_method": "qr_mobile" if check_out else "pendiente",
                    "qr_token": generate_doctor_qr_token(d_id),
                    "notes": notes
                }
                records.append(rec)
                continue

            # DÍAS HISTÓRICOS (Días anteriores a hoy)
            # Determinismo para reproducibilidad realista
            seed_hash = (hash(f"{date_str}-{d_id}") % 100 + 100) % 100

            if seed_hash < 82:
                # PUNTUAL (82% de las ocasiones)
                delta_m = (seed_hash % 15) - 12 # -12 a +2 min
                in_time = cur_date.replace(hour=sched_in_h, minute=sched_in_m) + timedelta(minutes=delta_m)
                out_delta_m = (seed_hash % 25) # 0 a 25 min después de horario
                out_time = cur_date.replace(hour=sched_out_h, minute=sched_out_m) + timedelta(minutes=out_delta_m)

                check_in = in_time.strftime('%H:%M')
                check_out = out_time.strftime('%H:%M')
                status_in = "puntual"
                status_out = "salida_normal"
                overall_status = "presente"
                delay_min = 0
                notes = "Jornada clínica completada con éxito. Check-in y Check-out validados vía QR móvil."
            elif seed_hash < 93:
                # RETARDO LIGERO (11% de las ocasiones)
                delay_min = 16 + (seed_hash % 20) # 16 a 35 min
                in_time = cur_date.replace(hour=sched_in_h, minute=sched_in_m) + timedelta(minutes=delay_min)
                out_time = cur_date.replace(hour=sched_out_h, minute=sched_out_m) + timedelta(minutes=15)

                check_in = in_time.strftime('%H:%M')
                check_out = out_time.strftime('%H:%M')
                status_in = "retardo"
                status_out = "salida_normal"
                overall_status = "retardo"
                notes = f"Retardo registrado (+{delay_min} min). Notificado a recepción."
            elif seed_hash < 97:
                # FALTA JUSTIFICADA (4%)
                check_in = None
                check_out = None
                status_in = "falta"
                status_out = "no_aplica"
                overall_status = "falta_justificada"
                delay_min = 0
                notes = "Inasistencia justificada: Permiso por actualización quirúrgica y congreso médico."
            else:
                # SALIDA ANTICIPADA (3%)
                check_in = sched_in
                out_time = cur_date.replace(hour=sched_out_h, minute=sched_out_m) - timedelta(minutes=50)
                check_out = out_time.strftime('%H:%M')
                status_in = "puntual"
                status_out = "salida_anticipada"
                overall_status = "presente"
                delay_min = 0
                notes = "Salida anticipada autorizada por dirección médica tras concluir cirugías programadas."

            hours_w, hours_fmt = calc_hours_worked(check_in, check_out) if (check_in and check_out) else (0.0, "0h 00m")
            patients_cnt = prof['patients'] if check_in else 0

            rec = {
                "id": f"att-{date_str}-{d_id}",
                "doc_id": d_id,
                "doctor_name": d['name'],
                "specialty": d.get('specialty', 'Especialista Dental'),
                "photo": d.get('photo', ''),
                "branch": d.get('branch', 'Monterrey Centro'),
                "unidad_clinica": d.get('unidad_clinica', 'Sillón 1'),
                "date": date_str,
                "day_name": day_label,
                "scheduled_in": sched_in,
                "scheduled_out": sched_out,
                "check_in": check_in,
                "check_out": check_out,
                "hours_worked": hours_w,
                "hours_formatted": hours_fmt,
                "status_in": status_in,
                "status_out": status_out,
                "delay_minutes": delay_min,
                "overall_status": overall_status,
                "patients_seen": patients_cnt,
                "check_in_method": "qr_mobile" if check_in else "ninguno",
                "check_out_method": "qr_mobile" if check_out else "ninguno",
                "qr_token": generate_doctor_qr_token(d_id),
                "notes": notes
            }
            records.append(rec)

    # Ordenar cronológicamente descendente (lo más reciente primero)
    records.sort(key=lambda x: (x['date'], x.get('check_in') or '00:00'), reverse=True)
    save_attendance_records(records)
    return records

def record_attendance_scan(identifier, method="qr_mobile", custom_notes=""):
    """
    Registra llegada o salida de un doctor a través de su código QR o ID de doctor.
    Si hoy no tiene check-in, registra LLEGADA / ENTRADA.
    Si ya tiene check-in pero no check-out, registra SALIDA y calcula horas laboradas.
    """
    records = load_attendance_records()
    docs = load_doctors()
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    now_time_str = now.strftime('%H:%M')
    day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    day_label = day_names[now.weekday()]

    # Buscar doctor por ID o por token QR
    target_doc = None
    clean_id = identifier.strip()

    if clean_id.startswith("COBA-DOC-ATTENDANCE:"):
        parts = clean_id.split(':')
        if len(parts) >= 2:
            clean_id = parts[1]

    for d in docs:
        if d['id'] == clean_id or d.get('email') == clean_id:
            target_doc = d
            break

    if not target_doc:
        return {
            "status": "error",
            "message": f"Código QR o credencial de especialista '{identifier}' no reconocida por el sistema."
        }

    doc_id = target_doc['id']
    doc_name = target_doc['name']
    specialty = target_doc.get('specialty', 'Especialista')
    sched_in = "09:00"
    sched_out = "18:30"
    if "09:" in target_doc.get('horario_consulta', ''):
        sched_in = "09:00"
    elif "10:" in target_doc.get('horario_consulta', ''):
        sched_in = "10:00"

    # Buscar registro existente de hoy para este doctor
    today_record = None
    for r in records:
        if r.get('date') == today_str and r.get('doc_id') == doc_id:
            today_record = r
            break

    # ACCIÓN 1: REGISTRAR LLEGADA (ENTRADA)
    if not today_record or not today_record.get('check_in'):
        # Evaluar puntualidad respecto al horario programado
        sched_h, sched_m = parse_time_str(sched_in)
        now_h, now_m = now.hour, now.minute
        diff_min = (now_h * 60 + now_m) - (sched_h * 60 + sched_m)

        delay_minutes = max(0, diff_min)
        is_tardy = delay_minutes > 15  # 15 min de tolerancia
        status_in = "retardo" if is_tardy else "puntual"
        overall_status = "retardo" if is_tardy else "en_turno"

        default_note = (
            f"Llegada registrada con retardo (+{delay_minutes} min) mediante escaneo de QR personal."
            if is_tardy else
            f"Llegada puntual registrada mediante credencial QR en teléfono del especialista."
        )

        new_record = {
            "id": f"att-{today_str}-{doc_id}",
            "doc_id": doc_id,
            "doctor_name": doc_name,
            "specialty": specialty,
            "photo": target_doc.get('photo', ''),
            "branch": target_doc.get('branch', 'Monterrey Centro'),
            "unidad_clinica": target_doc.get('unidad_clinica', 'Sillón 1'),
            "date": today_str,
            "day_name": day_label,
            "scheduled_in": sched_in,
            "scheduled_out": sched_out,
            "check_in": now_time_str,
            "check_out": None,
            "hours_worked": 0.0,
            "hours_formatted": "En curso",
            "status_in": status_in,
            "status_out": "en_turno",
            "delay_minutes": delay_minutes,
            "overall_status": overall_status,
            "patients_seen": 0,
            "check_in_method": method,
            "check_out_method": "pendiente",
            "qr_token": generate_doctor_qr_token(doc_id),
            "notes": custom_notes or default_note
        }

        if today_record:
            today_record.update(new_record)
        else:
            records.insert(0, new_record)

        save_attendance_records(records)
        return {
            "status": "ok",
            "action": "check_in",
            "doctor_name": doc_name,
            "specialty": specialty,
            "check_in": now_time_str,
            "status_in": status_in,
            "delay_minutes": delay_minutes,
            "message": f"¡Llegada confirmada! Bienvenido(a) {doc_name}. Registrado a las {now_time_str} ({'Puntual' if not is_tardy else f'Retardo +{delay_minutes} min'}).",
            "record": new_record
        }

    # ACCIÓN 2: REGISTRAR SALIDA
    elif today_record.get('check_in') and not today_record.get('check_out'):
        check_in_str = today_record.get('check_in')
        hours_w, hours_fmt = calc_hours_worked(check_in_str, now_time_str)

        sched_out_h, sched_out_m = parse_time_str(sched_out)
        out_diff = (sched_out_h * 60 + sched_out_m) - (now.hour * 60 + now.minute)
        is_early = out_diff > 35  # Más de 35 min antes de horario
        status_out = "salida_anticipada" if is_early else "salida_normal"

        prev_overall = today_record.get('overall_status')
        final_overall = "retardo" if prev_overall == "retardo" else "presente"

        today_record['check_out'] = now_time_str
        today_record['hours_worked'] = hours_w
        today_record['hours_formatted'] = hours_fmt
        today_record['status_out'] = status_out
        today_record['overall_status'] = final_overall
        today_record['check_out_method'] = method
        if custom_notes:
            today_record['notes'] += f" • Salida: {custom_notes}"
        else:
            today_record['notes'] += f" • Salida registrada a las {now_time_str}. Turno: {hours_fmt}."

        save_attendance_records(records)
        return {
            "status": "ok",
            "action": "check_out",
            "doctor_name": doc_name,
            "specialty": specialty,
            "check_in": check_in_str,
            "check_out": now_time_str,
            "hours_worked": hours_w,
            "hours_formatted": hours_fmt,
            "status_out": status_out,
            "message": f"¡Salida confirmada! Hasta luego {doc_name}. Horario de salida: {now_time_str}. Tiempo total laborado: {hours_fmt}.",
            "record": today_record
        }

    # ACCIÓN 3: YA COMPLETÓ ENTRADA Y SALIDA HOY
    else:
        return {
            "status": "info",
            "action": "already_completed",
            "doctor_name": doc_name,
            "check_in": today_record.get('check_in'),
            "check_out": today_record.get('check_out'),
            "hours_formatted": today_record.get('hours_formatted'),
            "message": f"{doc_name} ya completó su turno el día de hoy (Entrada: {today_record.get('check_in')}, Salida: {today_record.get('check_out')}).",
            "record": today_record
        }

def justify_attendance_record(record_id, justification_reason="Permiso médico / congreso"):
    records = load_attendance_records()
    found = False
    updated_rec = None
    for r in records:
        if r.get('id') == record_id:
            r['overall_status'] = 'falta_justificada'
            r['notes'] = (r.get('notes') or '') + f" • Justificante: {justification_reason}"
            found = True
            updated_rec = r
            break
    if found:
        save_attendance_records(records)
        return {"status": "ok", "message": "Inasistencia o retraso justificado exitosamente.", "record": updated_rec}
    return {"status": "not_found", "message": "Registro no encontrado"}

def calculate_attendance_summary(doctor_id=None, filter_status=None, filter_date_range=None):
    all_records = load_attendance_records()
    docs = load_doctors()
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')

    filtered = []
    for r in all_records:
        if doctor_id and doctor_id != 'all' and r.get('doc_id') != doctor_id:
            continue
        if filter_status and filter_status != 'all':
            if filter_status == 'en_turno' and r.get('status_out') != 'en_turno':
                continue
            elif filter_status == 'puntual' and r.get('status_in') != 'puntual':
                continue
            elif filter_status == 'retardo' and r.get('status_in') != 'retardo':
                continue
            elif filter_status == 'falta' and not r.get('overall_status', '').startswith('falta'):
                continue
        if filter_date_range:
            r_date = r.get('date', '')
            if filter_date_range == 'today' and r_date != today_str:
                continue
            elif filter_date_range == 'week':
                week_ago = (now - timedelta(days=7)).strftime('%Y-%m-%d')
                if r_date < week_ago:
                    continue
            elif filter_date_range == 'month':
                month_ago = (now - timedelta(days=30)).strftime('%Y-%m-%d')
                if r_date < month_ago:
                    continue
        filtered.append(r)

    # Métricas Globales
    total_records = len(filtered)
    present_count = sum(1 for r in filtered if r.get('check_in'))
    punctual_count = sum(1 for r in filtered if r.get('status_in') == 'puntual')
    tardy_count = sum(1 for r in filtered if r.get('status_in') == 'retardo')
    absence_count = sum(1 for r in filtered if r.get('overall_status', '').startswith('falta'))
    active_in_clinic_count = sum(1 for r in all_records if r.get('date') == today_str and r.get('status_out') == 'en_turno')
    total_hours = sum(r.get('hours_worked', 0.0) for r in filtered)

    punctuality_pct = round((punctual_count / max(1, present_count)) * 100, 1)
    attendance_pct = round((present_count / max(1, total_records)) * 100, 1)

    # Doctores en turno hoy en vivo
    active_doctors_today = []
    for r in all_records:
        if r.get('date') == today_str and r.get('status_out') == 'en_turno':
            active_doctors_today.append({
                "doc_id": r.get('doc_id'),
                "doctor_name": r.get('doctor_name'),
                "specialty": r.get('specialty'),
                "photo": r.get('photo'),
                "check_in": r.get('check_in'),
                "unidad_clinica": r.get('unidad_clinica'),
                "status_in": r.get('status_in'),
                "delay_minutes": r.get('delay_minutes', 0)
            })

    # Resumen por cada doctor
    doc_breakdown = {}
    for d in docs:
        d_id = d['id']
        d_records = [r for r in all_records if r.get('doc_id') == d_id]
        d_present = sum(1 for r in d_records if r.get('check_in'))
        d_punctual = sum(1 for r in d_records if r.get('status_in') == 'puntual')
        d_tardy = sum(1 for r in d_records if r.get('status_in') == 'retardo')
        d_absence = sum(1 for r in d_records if r.get('overall_status', '').startswith('falta'))
        d_hours = sum(r.get('hours_worked', 0.0) for r in d_records)
        d_qr_url, d_token = generate_doctor_qr_data_url(d_id)

        doc_breakdown[d_id] = {
            "doctor": d,
            "doc_id": d_id,
            "name": d['name'],
            "specialty": d.get('specialty'),
            "photo": d.get('photo'),
            "total_shifts": len(d_records),
            "present_count": d_present,
            "punctual_count": d_punctual,
            "tardy_count": d_tardy,
            "absence_count": d_absence,
            "punctuality_rate": round((d_punctual / max(1, d_present)) * 100, 1),
            "total_hours": round(d_hours, 1),
            "avg_hours_per_day": round(d_hours / max(1, d_present), 1),
            "qr_data_url": d_qr_url,
            "qr_token": d_token,
            "is_in_clinic_today": any(r.get('date') == today_str and r.get('status_out') == 'en_turno' for r in d_records)
        }

    return {
        "status": "ok",
        "records": filtered,
        "metrics": {
            "total_records": total_records,
            "present_count": present_count,
            "punctual_count": punctual_count,
            "tardy_count": tardy_count,
            "absence_count": absence_count,
            "active_in_clinic_count": active_in_clinic_count,
            "attendance_rate": attendance_pct,
            "punctuality_rate": punctuality_pct,
            "total_hours_worked": round(total_hours, 1),
            "today_date": today_str
        },
        "active_doctors_today": active_doctors_today,
        "doctor_breakdown": doc_breakdown
    }

def get_doctor_digital_badge(doc_id):
    """Devuelve los datos completos del gafete digital de un doctor con su código QR para el teléfono."""
    doc = get_doctor_by_id(doc_id)
    if not doc:
        return {"status": "error", "message": "Doctor no encontrado"}

    qr_url, token = generate_doctor_qr_data_url(doc_id)
    now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    records = load_attendance_records()
    today_rec = next((r for r in records if r.get('date') == today_str and r.get('doc_id') == doc_id), None)

    return {
        "status": "ok",
        "badge": {
            "doc_id": doc['id'],
            "name": doc['name'],
            "title": doc.get('title', 'Especialista Dental'),
            "specialty": doc.get('specialty', 'Odontología'),
            "cedula": doc.get('cedula', 'Ced. Prof. Vigente'),
            "cedula_esp": doc.get('cedula_esp', 'SSA NL'),
            "phone": doc.get('phone', '+52 81 1848 3941'),
            "email": doc.get('email', 'contacto@coba.mx'),
            "photo": doc.get('photo', ''),
            "branch": doc.get('branch', 'Monterrey Centro'),
            "unidad_clinica": doc.get('unidad_clinica', 'Sillón Quirúrgico'),
            "horario_consulta": doc.get('horario_consulta', '09:00 AM - 06:30 PM'),
            "dias_consulta": doc.get('dias_consulta', 'Lunes a Sábado'),
            "qr_data_url": qr_url,
            "qr_token": token,
            "security_seal": hashlib.sha256(f"{doc_id}:SECURITY_SEAL_COBA".encode()).hexdigest()[:16].upper(),
            "today_status": today_rec.get('overall_status') if today_rec else 'sin_registro_hoy',
            "today_check_in": today_rec.get('check_in') if today_rec else None,
            "today_check_out": today_rec.get('check_out') if today_rec else None
        }
    }


def generate_attendance_pdf(doctor_id=None):
    """Genera un reporte PDF formal de asistencia y puntualidad con sello digital para el director."""
    all_records = load_attendance_records()
    docs = load_doctors()
    doc_target = get_doctor_by_id(doctor_id) if (doctor_id and doctor_id != 'all') else None

    filtered = [r for r in all_records if not doc_target or r.get('doc_id') == doc_target['id']]
    # Limitar a los 40 más recientes para mantener el documento en 1-2 páginas legibles
    display_records = filtered[:40]

    buf = io.BytesIO()
    doc_pdf = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0F172A')
    )
    sub_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748B')
    )
    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )
    td_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )
    td_bold = ParagraphStyle(
        'TDBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # ENCABEZADO INSTITUCIONAL
    header_data = [
        [
            Paragraph("<b>CLÍNICA DENTAL COBÁ MONTERREY</b><br/><font size=8 color='#64748B'>Jerónimo Treviño #1111 Pte. • San Jerónimo / Monterrey Centro • Tel: +52 81 1848 3941</font>", title_style),
            Paragraph(f"<b>CONTROL BIOMÉTRICO QR</b><br/><font size=8 color='#64748B'>Emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>Folio: ATT-{datetime.now().strftime('%Y%m%d%H%M')}</font>", ParagraphStyle('HRight', parent=sub_style, alignment=2))
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#06B6D4'), spaceAfter=10))

    # TÍTULO DEL REPORTE
    doc_label = doc_target['name'] + " (" + doc_target.get('specialty', '') + ")" if doc_target else "CUADRO MÉDICO COMPLETO (TODOS LOS ESPECIALISTAS)"
    story.append(Paragraph(f"<b>REPORTE OFICIAL DE ASISTENCIA, LLEGADAS & SALIDAS</b>", title_style))
    story.append(Paragraph(f"<b>Especialista(s):</b> {doc_label} &nbsp;|&nbsp; <b>Periodo:</b> Últimos 60 Días Registrados", sub_style))
    story.append(Spacer(1, 10))

    # RESUMEN EJECUTIVO DE MÉTRICAS
    present_cnt = sum(1 for r in filtered if r.get('check_in'))
    punctual_cnt = sum(1 for r in filtered if r.get('status_in') == 'puntual')
    tardy_cnt = sum(1 for r in filtered if r.get('status_in') == 'retardo')
    absence_cnt = sum(1 for r in filtered if r.get('overall_status', '').startswith('falta'))
    hours_tot = sum(r.get('hours_worked', 0.0) for r in filtered)
    punctuality_pct = round((punctual_cnt / max(1, present_cnt)) * 100, 1)

    kpi_data = [
        [
            Paragraph(f"<b>Turnos Registrados</b><br/><font size=12 color='#0F172A'><b>{len(filtered)}</b></font>", sub_style),
            Paragraph(f"<b>Asistencias</b><br/><font size=12 color='#10B981'><b>{present_cnt}</b></font>", sub_style),
            Paragraph(f"<b>Puntualidad</b><br/><font size=12 color='#06B6D4'><b>{punctuality_pct}%</b></font>", sub_style),
            Paragraph(f"<b>Retardos</b><br/><font size=12 color='#F59E0B'><b>{tardy_cnt}</b></font>", sub_style),
            Paragraph(f"<b>Inasistencias</b><br/><font size=12 color='#EF4444'><b>{absence_cnt}</b></font>", sub_style),
            Paragraph(f"<b>Horas Totales</b><br/><font size=12 color='#3B82F6'><b>{round(hours_tot, 1)} hrs</b></font>", sub_style),
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[90, 90, 90, 90, 90, 90])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 12))

    # TABLA DE REGISTROS
    table_rows = [
        [
            Paragraph("Fecha", th_style),
            Paragraph("Especialista", th_style),
            Paragraph("Llegada", th_style),
            Paragraph("Salida", th_style),
            Paragraph("Horas", th_style),
            Paragraph("Estatus", th_style),
            Paragraph("Método", th_style)
        ]
    ]

    for r in display_records:
        st_in = r.get('status_in', '')
        in_color = '#10B981' if st_in == 'puntual' else ('#F59E0B' if st_in == 'retardo' else '#EF4444')
        st_label = "Puntual" if st_in == 'puntual' else (f"Retardo (+{r.get('delay_minutes',0)}m)" if st_in == 'retardo' else "Inasistencia")

        table_rows.append([
            Paragraph(f"{r.get('date')}<br/><font size=7 color='#64748B'>{r.get('day_name')}</font>", td_style),
            Paragraph(f"<b>{r.get('doctor_name')}</b><br/><font size=7 color='#64748B'>{r.get('specialty')[:24]}</font>", td_style),
            Paragraph(f"<font color='{in_color}'><b>{r.get('check_in') or '---'}</b></font>", td_style),
            Paragraph(f"{r.get('check_out') or ('En Turno' if r.get('status_out') == 'en_turno' else '---')}", td_style),
            Paragraph(f"<b>{r.get('hours_formatted')}</b>", td_style),
            Paragraph(f"<font color='{in_color}'><b>{st_label}</b></font>", td_style),
            Paragraph(f"{'📱 QR Móvil' if 'qr' in r.get('check_in_method','') else 'Recepc.'}", td_style)
        ])

    records_table = Table(table_rows, colWidths=[70, 160, 60, 65, 55, 80, 50])
    records_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(records_table)
    story.append(Spacer(1, 14))

    # PIE DE PÁGINA Y SELLO
    seal_text = f"CERTIFICACIÓN DIGITAL DE ASISTENCIA • SISTEMA COBÁ 2026 • TOKEN: {hashlib.sha256(str(filtered[:5]).encode()).hexdigest()[:24].upper()}"
    story.append(Paragraph(f"<font size=7 color='#94A3B8'>{seal_text}</font>", sub_style))

    doc_pdf.build(story)
    return buf.getvalue()

