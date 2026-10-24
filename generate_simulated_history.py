import json
import csv
import os
import random
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTO_DIR = os.path.join(BASE_DIR, "automation")
DOCTORS_FILE = os.path.join(AUTO_DIR, "doctors.json")
JSON_CRM = os.path.join(AUTO_DIR, "crm_leads_coba.json")
CSV_CRM = os.path.join(AUTO_DIR, "crm_leads_coba.csv")

# 1. DOCTORS SEED DATA
DOCTORS = [
    {
        "id": "doc-1",
        "name": "Dr. Mauricio Cobá",
        "specialty": "Implantología & Cirugía Oral",
        "cedula": "Ced. Prof. 8492019 • SSA 39482",
        "phone": "+52 81 1848 3941",
        "email": "mauricio.coba@coba.mx",
        "branch": "Monterrey Centro (Jerónimo Treviño #1111 Pte.)",
        "color": "#06B6D4",
        "avatar": "MC",
        "photo": "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=400&auto=format&fit=crop&q=80",
        "bio": "Director y fundador. Especialista en implantes de titanio, carga inmediata y rehabilitación quirúrgica avanzada con más de 12 años de trayectoria médica.",
        "status": "Activo"
    },
    {
        "id": "doc-2",
        "name": "Dra. Valeria Garza Treviño",
        "specialty": "Ortodoncia & Alineadores Invisibles",
        "cedula": "Ced. Prof. 9283104 • UANL",
        "phone": "+52 81 8392 4810",
        "email": "valeria.garza@coba.mx",
        "branch": "Monterrey Centro (Jerónimo Treviño #1111 Pte.)",
        "color": "#EC4899",
        "avatar": "VG",
        "photo": "https://images.unsplash.com/photo-1594824813508-4ba3a059b56f?w=400&auto=format&fit=crop&q=80",
        "bio": "Certificada internacional en Invisalign® y ortodoncia biomecánica de baja fricción. Más de 1,200 casos de éxito en Monterrey y San Pedro.",
        "status": "Activo"
    },
    {
        "id": "doc-3",
        "name": "Dr. Daniel Fernández S.",
        "specialty": "Endodoncia Microscópica",
        "cedula": "Ced. Prof. 7392011 • SSA 28410",
        "phone": "+52 81 2940 1827",
        "email": "daniel.fernandez@coba.mx",
        "branch": "Guadalupe Centro (Benito Juárez #825)",
        "color": "#8B5CF6",
        "avatar": "DF",
        "photo": "https://images.unsplash.com/photo-1537368910025-700350fe46c7?w=400&auto=format&fit=crop&q=80",
        "bio": "Especialista en tratamiento de conductos bajo microscopio óptico Zeiss en una sola sesión. Alivio inmediato de dolor agudo e infecciones periapicales.",
        "status": "Activo"
    },
    {
        "id": "doc-4",
        "name": "Dra. Sofía Valdés Cantú",
        "specialty": "Prótesis Dental & Coronas de Zirconia",
        "cedula": "Ced. Prof. 6192840 • UDEM",
        "phone": "+52 81 8070 1778",
        "email": "sofia.valdes@coba.mx",
        "branch": "Guadalupe Centro (Benito Juárez #825)",
        "color": "#10B981",
        "avatar": "SV",
        "photo": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=400&auto=format&fit=crop&q=80",
        "bio": "Maestría en rehabilitación oral y prótesis fija CAD/CAM. Experta en coronas monolíticas de zirconia alemana y carillas ultrafinas.",
        "status": "Activo"
    },
    {
        "id": "doc-5",
        "name": "Dr. Alejandro Sada Benavides",
        "specialty": "Estética Dental & Diseño Digital DSD",
        "cedula": "Ced. Prof. 1049281 • ITESM",
        "phone": "+52 81 1234 9988",
        "email": "alejandro.sada@coba.mx",
        "branch": "Monterrey Centro (Jerónimo Treviño #1111 Pte.)",
        "color": "#F59E0B",
        "avatar": "AS",
        "photo": "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=400&auto=format&fit=crop&q=80",
        "bio": "Pionero en Monterrey en diseño digital 3D de sonrisa (DSD), armonización de arcos dentales y blanqueamiento fotoactivado láser de alta estética.",
        "status": "Activo"
    },
    {
        "id": "doc-6",
        "name": "Dra. Mariana Villarreal Elizondo",
        "specialty": "Odontopediatría & Profilaxis Preventiva",
        "cedula": "Ced. Prof. 1184920 • UANL",
        "phone": "+52 81 8820 4411",
        "email": "mariana.villarreal@coba.mx",
        "branch": "Guadalupe Centro (Benito Juárez #825)",
        "color": "#3B82F6",
        "avatar": "MV",
        "photo": "https://images.unsplash.com/photo-1623854767648-e7bb8009f0db?w=400&auto=format&fit=crop&q=80",
        "bio": "Especialista en atención dental infantil sin dolor ni ansiedad, profilaxis ultrasónica sin dolor, selladores y ortopedia maxilar temprana.",
        "status": "Activo"
    }
]

# Write doctors.json
with open(DOCTORS_FILE, 'w', encoding='utf-8') as f:
    json.dump(DOCTORS, f, ensure_ascii=False, indent=2)
print("Saved doctors.json successfully with 6 specialists.")

# 2. GENERATE 2 MONTHS OF INTENSE REALISTIC CLINICAL SIMULATION
FIRST_NAMES_M = ["Carlos", "Gerardo", "Alejandro", "Roberto", "Mauricio", "Javier", "David", "Fernando", "Ricardo", "Eduardo", "Rodrigo", "Héctor", "Patricio", "Daniel", "Arturo", "Guillermo", "Adrián", "Andrés", "Raúl", "Gabriel", "Esteban", "Diego", "Jesús", "José Luis"]
FIRST_NAMES_F = ["Valeria", "Sofía", "Mariana", "Claudia", "Andrea", "Daniela", "Camila", "Paulina", "Regina", "Natalia", "Gabriela", "Marcela", "Lorena", "Carolina", "Diana", "Paola", "Adriana", "Cecilia", "Fernanda", "Verónica", "Lucía", "Alicia", "Karla", "Mónica"]
LAST_NAMES = ["Garza", "Treviño", "Sada", "Elizondo", "Cantú", "Chapa", "Benavides", "Villarreal", "González", "Martínez", "Rodríguez", "Lozano", "Guerra", "Zambrano", "Montemayor", "Canales", "Cavazos", "Sepúlveda", "De la Garza", "García", "Reyes", "Salinas", "Flores"]

TREATMENT_SPECS = [
    # (Treatment name, Value, Primary Doctor, Specialty category)
    ("Promo Brackets Metálicos ($1,999 MXN + Limpieza Gratis)", 1999, "Dra. Valeria Garza Treviño", "Ortodoncia"),
    ("Promo Brackets Metálicos ($1,999 MXN + Limpieza Gratis)", 1999, "Dra. Valeria Garza Treviño", "Ortodoncia"),
    ("Ortodoncia Invisible con Alineadores ($28,000 MXN)", 28000, "Dra. Valeria Garza Treviño", "Ortodoncia"),
    ("Coronas y Puentes Fijos de Zirconia ($4,500 MXN)", 4500, "Dra. Sofía Valdés Cantú", "Prótesis"),
    ("Coronas y Puentes Fijos de Zirconia ($4,500 MXN)", 4500, "Dra. Sofía Valdés Cantú", "Prótesis"),
    ("Implantes Dentales de Titanio ($12,500 MXN)", 12500, "Dr. Mauricio Cobá", "Implantología"),
    ("Implantes Dentales de Titanio ($12,500 MXN)", 12500, "Dr. Mauricio Cobá", "Implantología"),
    ("Cirugía de Terceros Molares y Muelas de Juicio ($3,200 MXN)", 3200, "Dr. Mauricio Cobá", "Cirugía Oral"),
    ("Endodoncia Microscópica ($2,400 MXN)", 2400, "Dr. Daniel Fernández S.", "Endodoncia"),
    ("Endodoncia Microscópica ($2,400 MXN)", 2400, "Dr. Daniel Fernández S.", "Endodoncia"),
    ("Diseño de Sonrisa Digital y Blanqueamiento ($3,800 MXN)", 3800, "Dr. Alejandro Sada Benavides", "Estética"),
    ("Diseño de Sonrisa Digital y Blanqueamiento ($3,800 MXN)", 3800, "Dr. Alejandro Sada Benavides", "Estética"),
    ("Carillas de Porcelana Estratificada ($7,200 MXN)", 7200, "Dr. Alejandro Sada Benavides", "Estética"),
    ("Limpieza Ultrasónica y Profilaxis sin dolor ($950 MXN)", 950, "Dra. Mariana Villarreal Elizondo", "Prevención"),
    ("Limpieza Ultrasónica y Profilaxis sin dolor ($950 MXN)", 950, "Dra. Mariana Villarreal Elizondo", "Prevención"),
    ("Odontopediatría Integral y Selladores ($1,650 MXN)", 1650, "Dra. Mariana Villarreal Elizondo", "Odontopediatría"),
    ("Valoración y Diagnóstico General ($250 MXN)", 250, "Dr. Mauricio Cobá", "Diagnóstico")
]

BRANCHES = [
    "Monterrey Centro (Jerónimo Treviño #1111 Pte.)",
    "Monterrey Centro (Jerónimo Treviño #1111 Pte.)",
    "Guadalupe Centro (Benito Juárez #825)"
]

HOURS = ["09:00 AM", "09:30 AM", "10:15 AM", "11:00 AM", "11:45 AM", "12:30 PM", "02:00 PM", "03:15 PM", "04:00 PM", "04:45 PM", "05:30 PM", "06:15 PM"]

CLINICAL_NOTES_ATENDIDAS = [
    "Procedimiento completado con éxito. Paciente refiere alivio inmediato. Control programado en 21 días.",
    "Colocación de aparatología fija superior con alambre Niti .014. Excelente cooperación del paciente.",
    "Toma de escaneo intraoral 3D Medit i700 para corona de zirconia monolítica. Se colocó provisional pulido.",
    "Limpieza ultrasónica sin dolor completada, eliminación de cálculo subgingival y pulido Airflow.",
    "Apertura cameral e instrumentación rotatoria hasta calibre 25/.06. Medicación intraconducto hidróxido de calcio.",
    "Obturación termoplástica con técnica de condensación continua. Radiografía de control perfecta.",
    "Fase quirúrgica de colocación de implante 4.1x10mm con torque de 40 Ncm. Se colocó tornillo de cicatrización.",
    "Blanqueamiento fotoactivado LED en 3 ciclos de 15 minutos con peróxido de hidrógeno al 35%. Aclaró 4 tonos Vita.",
    "Cementación adhesiva definitiva de 2 coronas de zirconia con resina dual RelyX Ultimate. Oclusión ajustada.",
    "Extracción atraumática de molar retenido 48 bajo anestesia local con lidocaína 2%. Sutura reabsorbible 4-0.",
    "Revisión y cambio de elásticos intermaxilares clase II. Progresión del tratamiento al 65%.",
    "Tratamiento infantil libre de lágrimas. Aplicación de barniz de flúor al 5% y 4 selladores de fosetas."
]

# Read existing leads to keep them
existing_leads = []
if os.path.exists(JSON_CRM):
    try:
        with open(JSON_CRM, 'r', encoding='utf-8') as f:
            existing_leads = json.load(f)
    except Exception:
        existing_leads = []

# Preserve existing test leads and generate ~145 realistic historical appointments
start_date = datetime(2026, 8, 17)
end_date = datetime(2026, 10, 26)
current_date = datetime(2026, 10, 19, 12, 0)

simulated_leads = []
lead_seq = 2000

curr = start_date
random.seed(42)  # reproducible high quality dataset

while curr <= end_date:
    # Sunday has fewer appointments (0-1), weekdays have 2-4 appointments, Saturdays have 2-3
    weekday = curr.weekday() # 0 Mon, 6 Sun
    if weekday == 6:
        n_appointments = random.choice([0, 1])
    elif weekday == 5:
        n_appointments = random.choice([2, 3, 4])
    else:
        n_appointments = random.choice([2, 3, 4])

    for _ in range(n_appointments):
        lead_seq += 1
        is_female = random.choice([True, False])
        fn = random.choice(FIRST_NAMES_F if is_female else FIRST_NAMES_M)
        ln1 = random.choice(LAST_NAMES)
        ln2 = random.choice(LAST_NAMES)
        full_name = f"{fn} {ln1} {ln2}"
        
        # Monterrey phone
        phone_prefix = random.choice(["811", "812", "818", "813"])
        phone = f"+52 {phone_prefix} {random.randint(100, 999)} {random.randint(1000, 9999)}"
        email_user = f"{fn.lower()}.{ln1.lower()}{random.randint(10, 99)}"
        domain = random.choice(["gmail.com", "hotmail.com", "outlook.com", "yahoo.com.mx", "regiomail.mx"])
        email = f"{email_user}@{domain}"

        trat_spec = random.choice(TREATMENT_SPECS)
        tratamiento_nombre, _, default_doc, _ = trat_spec
        
        # Doctor assignment: 85% primary specialist, 15% director or another
        doctor_assigned = default_doc
        
        # Branch
        if "Sofía Valdés" in doctor_assigned or "Mariana Villarreal" in doctor_assigned:
            sucursal = "Guadalupe Centro (Benito Juárez #825)"
        elif "Valeria Garza" in doctor_assigned or "Alejandro Sada" in doctor_assigned:
            sucursal = "Monterrey Centro (Jerónimo Treviño #1111 Pte.)"
        else:
            sucursal = random.choice(BRANCHES)

        hora = random.choice(HOURS)
        date_str = curr.strftime("%Y-%m-%d")

        # Determine status based on whether date is in the past or future
        is_past = curr < current_date.replace(hour=0, minute=0, second=0)
        is_today = curr.date() == current_date.date()

        # Origin / Source
        source_roll = random.random()
        if source_roll < 0.44:
            source = "Recepción Inteligente Voz IA (Sofía)"
            estado_ia = "Llamada IA Exitosa + Confirmación Automática"
            # Outside business hours registration
            reg_hour = random.choice([19, 20, 21, 22, 23, 7])
            reg_min = random.randint(10, 59)
            reg_date = curr - timedelta(days=random.randint(1, 3))
            ts_str = f"{reg_date.strftime('%Y-%m-%d')} {reg_hour:02d}:{reg_min:02d}:{random.randint(10, 59):02d}"
        elif source_roll < 0.78:
            source = "Landing Oficial Clínica Dental Cobá MTY"
            estado_ia = "Pase Digital Emitido + Sincronizado en CRM"
            reg_hour = random.randint(8, 18)
            reg_min = random.randint(10, 59)
            reg_date = curr - timedelta(days=random.randint(1, 4))
            ts_str = f"{reg_date.strftime('%Y-%m-%d')} {reg_hour:02d}:{reg_min:02d}:{random.randint(10, 59):02d}"
        else:
            source = "Recepción Mostrador Cobá Directa"
            estado_ia = "Agendada en Terminal Clínica"
            reg_date = curr - timedelta(days=random.randint(1, 2))
            ts_str = f"{reg_date.strftime('%Y-%m-%d')} 11:30:00"

        if is_past:
            # 88% Atendida / Asistió, 7% Confirmada, 5% Cancelada
            status_roll = random.random()
            if status_roll < 0.88:
                status = "Asistió"
                mensaje = random.choice(CLINICAL_NOTES_ATENDIDAS)
            elif status_roll < 0.95:
                status = "Confirmada"
                mensaje = f"Tratamiento {tratamiento_nombre} concluido en tiempo y forma."
            else:
                status = "Cancelada"
                mensaje = "Paciente canceló 24h antes por motivo de viaje de trabajo. Se reprogramará el próximo mes."
        elif is_today:
            status = "Confirmada"
            mensaje = f"Cita para hoy {hora}. Pase Digital escaneado y paciente en sala de espera."
        else:
            status = random.choice(["Confirmada", "Confirmada", "Agendada"])
            mensaje = f"Cita confirmada mediante Pase Digital QR para {date_str} a las {hora}."

        record = {
            "id": f"coba-{lead_seq}",
            "timestamp": ts_str,
            "nombre": full_name,
            "telefono": phone,
            "email": email,
            "sucursal": sucursal,
            "tratamiento": tratamiento_nombre,
            "fecha_cita": date_str,
            "hora_cita": hora,
            "doctor_asignado": doctor_assigned,
            "status": status,
            "mensaje": mensaje,
            "source": source,
            "estado_ia": estado_ia
        }
        simulated_leads.append(record)

    curr += timedelta(days=1)

print(f"Generated {len(simulated_leads)} realistic appointments over 2 months.")

# Combine: existing test leads first (so user test data stays intact), then simulated leads
all_leads = existing_leads + simulated_leads

with open(JSON_CRM, 'w', encoding='utf-8') as f:
    json.dump(all_leads, f, ensure_ascii=False, indent=2)

with open(CSV_CRM, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow([
        'ID', 'Fecha_Registro', 'Nombre', 'Telefono', 'Email',
        'Sucursal', 'Tratamiento', 'Fecha_Cita', 'Hora_Cita',
        'Doctor', 'Estado', 'Mensaje', 'Medio', 'Estado_Llamada_IA'
    ])
    for l in all_leads:
        writer.writerow([
            l.get('id', ''),
            l.get('timestamp', ''),
            l.get('nombre', ''),
            l.get('telefono', ''),
            l.get('email', ''),
            l.get('sucursal', ''),
            l.get('tratamiento', ''),
            l.get('fecha_cita', ''),
            l.get('hora_cita', ''),
            l.get('doctor_asignado', ''),
            l.get('status', ''),
            l.get('mensaje', ''),
            l.get('source', ''),
            l.get('estado_ia', '')
        ])

print("Saved combined leads to crm_leads_coba.json and CSV successfully.")
