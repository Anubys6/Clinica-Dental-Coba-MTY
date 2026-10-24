# 🦷 Clínica Dental Cobá Monterrey — Sistema Completo Web Dark Luxury + Automatización n8n + Agente de Voz IA

Proyecto desarrollado con **Google Antigravity + n8n + Retell AI + ElevenLabs**, clonando y superando la arquitectura de **Álvaro Morales (`7gvlm6ZaJEQ`)**, adaptado al 100% para un cliente real detectado en **Monterrey, Nuevo León**: **Clínica Dental Cobá** (`@clinicadentalcoba`).

---

## 🎯 ¿Por qué Clínica Dental Cobá (Monterrey y Guadalupe) es el Cliente Ideal?

1. **Tienen 2 Sucursales Físicas en Operación (Capacidad de Pago Comprobada):**
   - **Sucursal Monterrey Centro:** Jerónimo Treviño #1111 Pte. (entre Juan Álvarez y Serafín Peña), Zona Centro, Monterrey, N.L. (`81 8374 6726` / `81 1848 3941`)
   - **Sucursal Guadalupe Centro:** Benito Juárez #825, Local D, 2do piso (entre 5 de Mayo y 3ra Av.), Centro de Guadalupe, N.L. (`81 8070 1778`)
2. **Su Dominio Web Actual está CAÍDO (`clinicadentalcoba.com` -> `NXDOMAIN`):**
   - En su página oficial de Facebook siguen mostrando `clinicadentalcoba.com`, pero el dominio no resuelve. Todo paciente que intenta entrar a su web ve un error de navegador.
3. **Saturación Operativa en Días de Promoción:**
   - Manejan promociones agresivas (Brackets Metálicos de $4,500 a **$1,999 MXN con limpieza gratis**, Coronas de Zirconia, Endodoncia) que saturan sus líneas telefónicas y mensajes de Instagram/Facebook.

---

## 📁 Estructura del Proyecto

```text
clinica-dental-coba-mty/
├── index.html                                      # Landing Dark Luxury + Cotizador + Booking + Simulador IA
├── styles.css                                      # Sistema de Diseño Dark Luxury (#06B6D4 Cian + #10B981 Esmeralda)
├── script.js                                       # 50 partículas, Flip Cards 3D, Webhook POST, Voz IA en vivo
├── server.py                                       # Servidor local (Puerto 8090) + Webhook CRM CSV/JSON + Retell Proxy
├── README.md                                       # Documentación completa
├── images/                                         # 10 imágenes generadas con IA (Nano Banana Pro)
│   ├── logo.png                                    # Logo minimalista Dark Luxury
│   ├── hero_visual.png                             # Elemento 3D principal del Hero
│   ├── service_1.png                               # Ortodoncia y Brackets
│   ├── service_2.png                               # Coronas y Puentes de Zirconia
│   ├── service_3.png                               # Diseño de Sonrisa Digital y Blanqueamiento
│   ├── service_4.png                               # Endodoncia Especializada Sin Dolor
│   ├── service_5.png                               # Implantes de Titanio y Cirugía
│   ├── service_6.png                               # Profilaxis Ultrasónica y Resinas
│   ├── showcase_1.png                              # Caso Antes y Después en Zirconia
│   └── showcase_2.png                              # Instalaciones modernas en Monterrey (Vista Cerro de la Silla)
└── automation/
    ├── n8n_workflow_clinica_coba.json              # Workflow n8n listo para importar (Webhook -> Sheets -> Retell AI)
    ├── n8n_workflow_prospeccion_agencia_mty.json   # Workflow n8n Outbound para prospectar negocios en Monterrey
    ├── prompts_agentes_voz_retell.md               # Prompts completos para Retell AI (Clínica Cobá + Agencia B2B)
    ├── kit_ventas_outreach_monterrey.md            # Guiones de WhatsApp, llamada en frío, Loom y precios en MXN
    ├── crm_leads_coba.csv                          # Base de datos CRM local (compatible con Excel / Google Sheets)
    └── crm_leads_coba.json                         # Base de datos CRM en formato JSON
```

---

## 🚀 Cómo Ejecutar y Probar Todo el Sistema Ahora Mismo

1. Inicia el servidor de automatización y web:
   ```powershell
   python server.py
   ```
2. Abre en tu navegador:
   - **Landing Page + Monitor n8n + Agente de Voz IA:** `http://localhost:8090`
   - **API de Leads Guardados en CRM:** `http://localhost:8090/api/leads`
   - **Enlaces Directos de WhatsApp para Venderle a Clínica Dental Cobá:** `http://localhost:8090/api/outreach-links`
