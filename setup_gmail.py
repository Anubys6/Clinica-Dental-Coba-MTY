#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utilidad para conectar tu cuenta de Gmail al Servidor de Clínica Dental Cobá / AUTOMATIC
Permite enviar los Pases Digitales de Cita a cualquier correo registrado en la web.
"""

import os
import sys
import json
import smtplib
from email.message import EmailMessage

AUTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'automation')
CONFIG_PATH = os.path.join(AUTO_DIR, 'email_config.json')
os.makedirs(AUTO_DIR, exist_ok=True)

def configure_gmail(gmail_user, app_password, test_recipient=None):
    gmail_user = gmail_user.strip()
    app_password = app_password.strip().replace(' ', '')

    print(f"\n🔐 Probando conexión con Gmail SMTP (smtp.gmail.com:587) para {gmail_user}...")
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=12) as server:
            server.starttls()
            server.login(gmail_user, app_password)
            print("✅ ¡Autenticación exitosa con Google! Las credenciales son 100% correctas.")

        # Guardar en archivo de configuración local
        config = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except Exception:
                config = {}

        config['provider'] = 'gmail'
        config['gmail_user'] = gmail_user
        config['gmail_app_password'] = app_password
        config['smtp_host'] = 'smtp.gmail.com'
        config['smtp_port'] = 587

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"💾 Configuración guardada en: {CONFIG_PATH}")

        # Enviar prueba si se indicó destinatario
        if test_recipient:
            print(f"📧 Enviando pase digital de prueba a: {test_recipient}...")
            import server
            test_record = {
                'nombre': 'Prueba Exitosa de Envío',
                'telefono': '+52 81 8374 6726',
                'email': test_recipient,
                'sucursal': 'Monterrey Centro (Jerónimo Treviño #1111 Pte.)',
                'tratamiento': 'Promo Brackets Metálicos ($1,999 MXN + Limpieza Gratis)',
                'fecha_cita': '2026-10-21',
                'hora_cita': '11:00 AM'
            }
            res = server.dispatch_confirmation_email(test_record)
            print("Resultado del envío:", res)
            print(f"\n🎉 ¡LISTO! Revisa tu bandeja de entrada en {test_recipient}. El correo ya debe estar ahí.")

        return True

    except Exception as e:
        print(f"\n❌ Error al conectar con Gmail: {e}")
        print("\nVerifica que:")
        print("  1. Tengas la 'Verificación en dos pasos' activa en tu cuenta de Google.")
        print("  2. La contraseña sea de 'Contraseña de aplicación' (16 letras), no tu contraseña normal.")
        return False

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        user = sys.argv[1]
        pw = sys.argv[2]
        recipient = sys.argv[3] if len(sys.argv) > 3 else user
        configure_gmail(user, pw, recipient)
    else:
        print("Uso: python setup_gmail.py tu_correo@gmail.com 'tu_clave_de_16_letras' [correo_destinatario_prueba]")
