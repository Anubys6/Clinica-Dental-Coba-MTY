"""
Script de Campaña de Prospección Fría para Clínicas Dentales de Monterrey
Emisor: mujica360@gmail.com (Agencia AUTOMATIC)
"""

import json
import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AUTO_DIR = BASE_DIR / "automation"
CONFIG_PATH = AUTO_DIR / "email_config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

SMTP_USER = config["gmail_user"]
SMTP_PASS = config["gmail_app_password"]
SMTP_HOST = config.get("smtp_host", "smtp.gmail.com")
SMTP_PORT = int(config.get("smtp_port", 587))

DEMO_URL = "https://dec-convertible-bin-looks.trycloudflare.com/clinica-coba/"
AGENCY_URL = "https://dec-convertible-bin-looks.trycloudflare.com/"

CLINICAS = [
    {
        "id": 1,
        "name": "Dentaltek Clínica Dental",
        "contact_name": "Equipo Directivo Dentaltek",
        "email": "dentaltek.citas@gmail.com",
        "whatsapp": "+528117984513",
        "location": "Colinas de San Jerónimo, Monterrey, N.L.",
        "social": "Instagram: @dentaltek.mty | Facebook: Dentaltek Monterrey",
        "bottleneck": "Atención telefónica manual en horario de oficina; pérdida de prospectos en fines de semana."
    },
    {
        "id": 2,
        "name": "OMA Clínica Dental",
        "contact_name": "Dres. Directores de OMA Clínica Dental",
        "email": "omaclinicadental@gmail.com",
        "whatsapp": "+528187998864",
        "location": "Mitras Centro, Monterrey, N.L.",
        "social": "Instagram: @omaclinicadental | Facebook: OMA Clínica Dental",
        "bottleneck": "Fuga de pacientes que preguntan cotizaciones en redes y tardan en recibir confirmación formal."
    },
    {
        "id": 3,
        "name": "Dr. Daniel Fernández - Periodoncia e Implantes",
        "contact_name": "Dr. Daniel Fernández",
        "email": "periodoncista.mx@gmail.com",
        "whatsapp": "+528118809351",
        "location": "Centro Profesional Delta, Sertoma, Monterrey, N.L.",
        "social": "Instagram: @drdanielfernandez | Facebook: Periodoncia e Implantes MTY",
        "bottleneck": "Consultas de alta especialidad con tiempo de espera en recepción para apartar valoración."
    },
    {
        "id": 4,
        "name": "Dental Clinic Monterrey",
        "contact_name": "Administración Dental Clinic Garza Sada",
        "email": "dentalclinicgarzasada@gmail.com",
        "whatsapp": "+528183570000",
        "location": "Lagos del Bosque / Garza Sada, Monterrey, N.L.",
        "social": "Facebook: Dental Clinic Garza Sada",
        "bottleneck": "Recepción tradicional sin sistema de retención interactiva por voz ni confirmación digital inmediata."
    },
    {
        "id": 5,
        "name": "MAAS Dentistas",
        "contact_name": "Dra. y Dr. Fundadores de MAAS Dentistas",
        "email": "maasdentistas@gmail.com",
        "whatsapp": "+528113603501",
        "location": "Contry, Monterrey, N.L.",
        "social": "Instagram: @maasdentistas | Facebook: MAAS Dentistas Contry",
        "bottleneck": "Interés en estética dental sin precalificación automática de presupuesto antes de la visita."
    },
    {
        "id": 6,
        "name": "Universo Dental Monterrey",
        "contact_name": "Coordinación Universo Dental",
        "email": "universodentalmty@gmail.com",
        "whatsapp": "+528183711200",
        "location": "Col. Central, Monterrey, N.L.",
        "social": "Facebook: Universo Dental Monterrey",
        "bottleneck": "Inasistencias a citas agendadas por falta de recordatorio y pase de confirmación digital con QR."
    },
    {
        "id": 7,
        "name": "Cosmetic Dental Center Monterrey",
        "contact_name": "Dirección Médica Cosmetic Dental Center",
        "email": "cosmeticdentalcenter.mty@gmail.com",
        "whatsapp": "+528120001234",
        "location": "San Jerónimo, Monterrey, N.L.",
        "social": "Instagram: @cosmeticdentalcentermty",
        "bottleneck": "Costosas campañas de redes con fuga de prospectos por demora en el primer contacto."
    },
    {
        "id": 8,
        "name": "DENTALY Cumbres",
        "contact_name": "Equipo Clínico DENTALY",
        "email": "dentaly@hotmail.com",
        "whatsapp": "+528181612713",
        "location": "Cumbres 1er Sector, Monterrey, N.L.",
        "social": "Instagram: @dentaly_mty",
        "bottleneck": "Atención reactiva manual en bandeja de entrada de Instagram y WhatsApp."
    },
    {
        "id": 9,
        "name": "DentaLumex Consultorio Dental",
        "contact_name": "Dra. Titular DentaLumex",
        "email": "dentalumex.mty@gmail.com",
        "whatsapp": "+528115010451",
        "location": "Centro de Monterrey, N.L.",
        "social": "Facebook: DentaLumex Monterrey",
        "bottleneck": "Citas agendadas por libreta sin envío automático de confirmaciones ni soporte 24/7."
    },
    {
        "id": 10,
        "name": "Clínica Dental Cobá",
        "contact_name": "Dirección General Clínica Dental Cobá",
        "email": "clinicadentalcoba@gmail.com",
        "whatsapp": "+528118483941",
        "location": "Jerónimo Treviño Centro Monterrey / Guadalupe, N.L.",
        "social": "Instagram: @clinicadentalcoba | Facebook: Clínica Dental Cobá",
        "bottleneck": "Sitio web oficial caído actualmente; todo el tráfico depende de WhatsApp sin asistente de voz."
    }
]

def build_email_content(clinic):
    subject = f"Automatización con IA para {clinic['name']} — Más pacientes confirmados con el costo más bajo de Monterrey"
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0b0f19; margin: 0; padding: 24px; color: #e2e8f0; }}
  .container {{ max-width: 600px; margin: 0 auto; background: #111827; border: 1px solid #1f2937; border-radius: 14px; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
  .header {{ background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); padding: 32px 28px; border-bottom: 2px solid #06b6d4; text-align: left; }}
  .badge {{ display: inline-block; background: rgba(6, 182, 212, 0.15); color: #22d3ee; padding: 4px 12px; border-radius: 999px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; border: 1px solid rgba(6, 182, 212, 0.3); margin-bottom: 12px; }}
  .title {{ font-size: 22px; font-weight: 800; color: #ffffff; margin: 0 0 6px 0; line-height: 1.25; }}
  .subtitle {{ font-size: 13px; color: #94a3b8; margin: 0; }}
  .content {{ padding: 28px; line-height: 1.6; font-size: 14px; color: #cbd5e1; }}
  .highlight-box {{ background: #1a2234; border-left: 4px solid #10b981; padding: 14px 18px; border-radius: 0 8px 8px 0; margin: 20px 0; }}
  .feature-list {{ list-style: none; padding: 0; margin: 18px 0; }}
  .feature-item {{ margin-bottom: 10px; display: flex; align-items: flex-start; }}
  .feature-icon {{ color: #22d3ee; font-weight: bold; margin-right: 10px; }}
  .cta-block {{ background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 20px; text-align: center; margin: 24px 0; }}
  .btn {{ display: inline-block; background: linear-gradient(135deg, #06b6d4, #0284c7); color: #ffffff !important; text-decoration: none; font-weight: 700; font-size: 14px; padding: 12px 26px; border-radius: 8px; margin: 6px; box-shadow: 0 4px 14px rgba(6, 182, 212, 0.35); }}
  .btn-alt {{ display: inline-block; background: #1e293b; color: #f1f5f9 !important; text-decoration: none; font-weight: 600; font-size: 14px; padding: 12px 22px; border-radius: 8px; margin: 6px; border: 1px solid #475569; }}
  .footer {{ background: #0a0e17; padding: 20px 28px; font-size: 12px; color: #64748b; border-top: 1px solid #1e293b; text-align: center; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="badge">AUTOMATIC • INGENIERÍA EN MONTERREY</div>
    <h1 class="title">Hola {clinic['contact_name']},</h1>
    <p class="subtitle">Propuesta tecnológica exclusiva para {clinic['name']} ({clinic['location']})</p>
  </div>
  <div class="content">
    <p>Sé que su tiempo es muy valioso, por lo que seré directo. He estado analizando el flujo de atracción de pacientes dentales en Monterrey y noté que hoy en día la mayoría de las clínicas pierden entre un <strong>30% y 40% de nuevos pacientes potenciales</strong> debido a dos factores críticos:</p>
    
    <div class="highlight-box">
      <strong>1. Pacientes nocturnos y de fin de semana:</strong> Prospectos que buscan atención a las 9:00 PM o domingos y nadie les responde en el momento.<br>
      <strong>2. Citas no confirmadas:</strong> Pacientes que se agendan por WhatsApp pero cancelan o no asisten por falta de un pase digital formal y seguimiento automático.
    </div>

    <p>Para solucionar esto, desarrollamos en <strong>AUTOMATIC</strong> un sistema integral de Inteligencia Artificial diseñado específicamente para consultorios dentales en Monterrey:</p>

    <ul class="feature-list">
      <li class="feature-item"><span class="feature-icon">✓</span> <strong>Asistente de Voz con IA humana 24/7:</strong> Contesta dudas de tratamientos (brackets, implantes, limpiezas, urgencias) y agenda citas de forma natural directo en su web.</li>
      <li class="feature-item"><span class="feature-icon">✓</span> <strong>Generación instantánea de Pase Digital:</strong> Cada paciente recibe en su correo y pantalla un boleto premium con folio y código QR con la ubicación de su clínica en Google Maps.</li>
      <li class="feature-item"><span class="feature-icon">✓</span> <strong>Costo más económico de la competencia:</strong> Sin cobros abusivos de agencias extranjeras (de $500 o $1,000 USD/mes). Nuestro plan está adaptado a clínicas locales en Monterrey y es <strong>el más accesible del mercado</strong>.</li>
      <li class="feature-item"><span class="feature-icon">✓</span> <strong>Soporte técnico directo incluido:</strong> Implementación llave en mano, ajustes inmediatos y soporte local en Monterrey garantizado.</li>
    </ul>

    <div class="cta-block">
      <p style="margin: 0 0 14px 0; font-size: 13px; color: #94a3b8; font-weight: 600;">PRUEBA EL SISTEMA FUNCIONANDO EN VIVO AHORA:</p>
      <a href="{DEMO_URL}" class="btn" target="_blank">Ver Prototipo Dental en Vivo</a>
      <a href="{AGENCY_URL}" class="btn-alt" target="_blank">Conocer AUTOMATIC</a>
    </div>

    <p>Construimos este prototipo en vivo para que puedan ver con sus propios ojos la fluidez de la voz y el pase digital. Me encantaría ponerme en contacto con ustedes esta misma semana para una breve llamada de 10 minutos o una visita a su consultorio y mostrarles cómo podemos activarlo para <strong>{clinic['name']}</strong> sin complicaciones técnicas.</p>

    <p style="margin-top: 24px; color: #ffffff;">
      Quedo a su entera disposición,<br><br>
      <strong>Director de Proyectos y Automatización</strong><br>
      <span style="color: #22d3ee; font-weight: bold;">AUTOMATIC — Soluciones de IA y Crecimiento</span><br>
      Correo directo: <a href="mailto:{SMTP_USER}" style="color: #38bdf8;">{SMTP_USER}</a><br>
      Monterrey, Nuevo León, México
    </p>
  </div>
  <div class="footer">
    AUTOMATIC © 2026 • Innovación en automatización médica • Monterrey, N.L.<br>
    Si no deseas recibir más información técnica, simplemente responde a este correo indicándolo.
  </div>
</div>
</body>
</html>"""

    plain = f"""Hola {clinic['contact_name']},

Espero que se encuentren muy bien. Les escribo para presentarles una solución de automatización diseñada específicamente para clínicas dentales en Monterrey, pensando en el crecimiento de {clinic['name']} ({clinic['location']}).

Hoy en día, muchas clínicas en Monterrey pierden pacientes potenciales en las noches o fines de semana porque no hay quién conteste de inmediato, o sufren de inasistencias porque las citas quedan en un chat informal de WhatsApp.

En AUTOMATIC desarrollamos un sistema de Inteligencia Artificial para consultorios dentales:
- Recepcionista con voz IA ultra-natural 24/7 que atiende en su sitio web, responde dudas de ortodoncia, implantes y urgencias, y agenda citas automáticamente.
- Emisión inmediata de Pase Digital con QR y mapa de su consultorio enviado al correo del paciente.
- La opción MÁS ECONÓMICA de la competencia en el mercado, sin costos excesivos de agencias extranjeras.
- Soporte técnico local continuo en Monterrey incluido.

Pueden probar la demostración interactiva en vivo aquí:
- Prototipo Clínico Dental: {DEMO_URL}
- Nuestra Agencia AUTOMATIC: {AGENCY_URL}

Me encantaría ponerme en contacto con ustedes para coordinar una breve llamada de 10 minutos o visita y platicarles cómo implementarlo fácilmente en {clinic['name']}.

Quedo a su disposición.

Atentamente,
Director de Proyectos y Automatización
AUTOMATIC Monterrey
Correo: {SMTP_USER}
Monterrey, N.L., México
"""
    return subject, html, plain

def send_campaign():
    results = []
    print(f"Iniciando conexión segura con {SMTP_HOST}:{SMTP_PORT} para {SMTP_USER}...")
    
    context = ssl.create_default_context()
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(SMTP_USER, SMTP_PASS)
        print("Autenticación SMTP exitosa en Gmail.")
        
        for clinic in CLINICAS:
            target_email = clinic["email"]
            subject, html_body, plain_body = build_email_content(clinic)
            
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"AUTOMATIC Monterrey <{SMTP_USER}>"
            msg["To"] = target_email
            msg["Reply-To"] = SMTP_USER
            
            part_text = MIMEText(plain_body, "plain", "utf-8")
            part_html = MIMEText(html_body, "html", "utf-8")
            msg.attach(part_text)
            msg.attach(part_html)
            
            try:
                server.sendmail(SMTP_USER, target_email, msg.as_string())
                print(f"[ENVIADO] #{clinic['id']} -> {clinic['name']} ({target_email})")
                results.append({"id": clinic["id"], "name": clinic["name"], "email": target_email, "status": "ENVIADO"})
            except Exception as e:
                print(f"[ERROR] #{clinic['id']} -> {clinic['name']} ({target_email}): {e}")
                results.append({"id": clinic["id"], "name": clinic["name"], "email": target_email, "status": f"ERROR: {e}"})
            
            time.sleep(1) # pausa preventiva
            
        # Enviar copia de control al correo del usuario con el resumen de la campaña
        summary_subject = "REPORTE DE CAMPAÑA: 10 Correos de Prospección Dental Enviados desde mujica360@gmail.com"
        summary_html = f"""<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; background-color: #0d1117; color: #c9d1d9; padding: 20px;">
  <div style="max-width: 650px; margin: auto; background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 24px;">
    <h2 style="color: #58a6ff; margin-top: 0;">Reporte de Campaña de Prospección — AUTOMATIC</h2>
    <p>Se ha ejecutado el envío de correos de contacto a las 10 clínicas dentales prospectadas en Monterrey, Nuevo León.</p>
    <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px;">
      <tr style="background: #21262d; color: #f0f6fc; text-align: left;">
        <th style="padding: 8px; border: 1px solid #30363d;">#</th>
        <th style="padding: 8px; border: 1px solid #30363d;">Clínica</th>
        <th style="padding: 8px; border: 1px solid #30363d;">Destinatario</th>
        <th style="padding: 8px; border: 1px solid #30363d;">Estado</th>
      </tr>
      {"".join(f"<tr><td style='padding: 8px; border: 1px solid #30363d;'>{r['id']}</td><td style='padding: 8px; border: 1px solid #30363d;'>{r['name']}</td><td style='padding: 8px; border: 1px solid #30363d;'>{r['email']}</td><td style='padding: 8px; border: 1px solid #30363d; color: #3fb950; font-weight: bold;'>{r['status']}</td></tr>" for r in results)}
    </table>
    <div style="margin-top: 20px; padding: 14px; background: #0d1117; border-left: 4px solid #58a6ff; border-radius: 4px;">
      <strong>Enlaces promocionados:</strong><br>
      • Prototipo Cobá: <a href="{DEMO_URL}" style="color: #58a6ff;">{DEMO_URL}</a><br>
      • Agencia AUTOMATIC: <a href="{AGENCY_URL}" style="color: #58a6ff;">{AGENCY_URL}</a>
    </div>
  </div>
</body>
</html>"""
        summary_msg = MIMEMultipart("alternative")
        summary_msg["Subject"] = summary_subject
        summary_msg["From"] = f"AUTOMATIC Sistema <{SMTP_USER}>"
        summary_msg["To"] = SMTP_USER
        summary_msg.attach(MIMEText(summary_html, "html", "utf-8"))
        
        try:
            server.sendmail(SMTP_USER, SMTP_USER, summary_msg.as_string())
            print(f"[COPIA DE CONTROL ENVIADA A] {SMTP_USER}")
        except Exception as e:
            print(f"[ERROR COPIA CONTROL] {e}")

    # Guardar reporte en disco
    out_path = AUTO_DIR / "campaign_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Reporte guardado en", out_path)

if __name__ == "__main__":
    send_campaign()
