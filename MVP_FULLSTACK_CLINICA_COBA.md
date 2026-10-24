# 🦷 MANIFIESTO Y ARQUITECTURA: MVP FULL-STACK (CLÍNICA DENTAL COBÁ)

> **"Un MVP Full-Stack es la versión inicial de un software que incluye únicamente las funciones indispensables para resolver el problema del cliente y empezar a cobrar, cubriendo de extremo a extremo la Cara Visual (Frontend), el Cerebro (Backend) y la Memoria (Base de Datos)."**

---

## 🏛️ 1. Arquitectura de las 3 Capas (End-to-End)

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CAPA 1: FRONTEND (La Cara Visual)                    │
│                                                                        │
│   [PACIENTE / B2C]                      [DOCTOR & CLÍNICA / B2B]       │
│   • index.html                          • portal_doctor.html           │
│   • Odontograma 3D (Three.js WebGL)     • Dashboard Financiero & Citas │
│   • Cotizador en 30 segundos            • Recibos de Pago PDF Formales │
│   • Simulador WhatsApp Interactivo      • Asistencia QR por Doctor     │
│   • Dark Luxury Glassmorphism CSS       • Semáforo de Inventario       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Peticiones HTTP / Fetch / REST APIs
┌───────────────────────────────────▼────────────────────────────────────┐
│                   CAPA 2: BACKEND (El Cerebro)                         │
│                                                                        │
│   • server.py: Servidor HTTP con enrutamiento y CORS habilitado        │
│   • whatsapp_bot_service.py: Webhook Meta Cloud API + Gemini 3.8 Flash │
│   • pdf_receipt_service.py: Generador de Recibos de Honorarios PDF     │
│   • doctor_attendance_service.py: Validador Criptográfico de QR Entrada│
│   • inventory_service.py: Algoritmo de consumo y reajuste de insumos   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Transacciones ACID / SQL Queries
┌───────────────────────────────────▼────────────────────────────────────┐
│                   CAPA 3: BASE DE DATOS (La Memoria)                   │
│                                                                        │
│   Motor Relacional: SQLite 3 (automation/clinica_coba.db)              │
│   • pacientes (222 registros)     • asistencia_qr (244 eventos)        │
│   • doctores (7 especialistas)    • inventario_insumos (55 insumos)    │
│   • recibos_liquidacion           • conversaciones_whatsapp            │
│   Redundancia: Sincronización continua con JSON & CSV de auditoría     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 💎 2. Desglose Detallado de Cada Capa

### 🎨 Capa 1: Frontend (La Cara Visual)
1. **Experiencia del Paciente (`index.html`)**:
   - **Odontograma 3D Articulado**: Modelo en Three.js con maxilar superior, mandíbula con bisagra temporomandibular que se abre con un slider del 0% al 100%, selección clínica de dientes (FDI 11 al 48) y diagnóstico en vivo.
   - **Cotizador Inteligente en 30 Segundos**: Preguntas clínicas necesarias (nombre, WhatsApp, sucursal Monterrey o Guadalupe, tratamiento, nivel de dolor/urgencia, fecha y turno).
   - **Menú Interactivo de WhatsApp**: Canaliza la intención de compra del paciente directamente al WhatsApp de la clínica.

2. **Panel de Control del Cliente / Doctor (`portal_doctor.html`)**:
   - **Métricas de Facturación & Cobros**: Total facturado, comisiones médicas pendientes, tratamientos realizados.
   - **Generador de Recibos PDF**: Liquidación formal con desglose de honorarios, retenciones y botón directo de descarga PDF.
   - **Reloj Checador QR**: Escáner de entrada y salida con código QR único para cada doctor, detección automática de retardos y cálculo de horas trabajadas.
   - **Control de Inventario**: Alerta visual con semáforo (Verde, Amarillo, Rojo) de materiales gastados.
   - **Consola WhatsApp Meta**: Prueba en vivo del bot conversacional Gemini y datos del Webhook oficial.

---

### 🧠 Capa 2: Backend (El Cerebro)
1. **Servidor API REST (`server.py`)**:
   - Atiende peticiones en el puerto 8090 y canaliza peticiones a través del túnel seguro Cloudflare.
   - Endpoints clave:
     - `GET /api/mvp/status`: Reporte del estado de salud de las 3 capas del Full-Stack.
     - `GET /api/leads` y `POST /webhook/clinica-coba-leads`: Gestión de expedientes clínicos.
     - `GET /api/receipts/pdf`: Emisión de recibos formales en PDF.
     - `POST /api/attendance/check`: Registro de entrada/salida de doctores con token QR.
     - `GET/POST /webhook/whatsapp`: Integración oficial con Meta WhatsApp Business Cloud API.
2. **Cerebro de Inteligencia Artificial (`whatsapp_bot_service.py`)**:
   - Impulsado por **Gemini 3.8 Flash** (`google.genai`).
   - Mantiene memoria conversacional por paciente, responde con empatía clínica y extrae automáticamente los datos para insertarlos en la base de datos.

---

### 🗄️ Capa 3: Base de Datos (La Memoria Relacional)
1. **Motor SQL Transaccional (`automation/clinica_coba.db`)**:
   - Estructurado en SQLite 3 con transacciones ACID para evitar cualquier pérdida o corrupción de datos.
   - **Tablas Creadas y Pobladas**:
     - `pacientes`: **222 registros** con folio, datos de contacto, tratamiento y urgencia.
     - `doctores`: **7 especialistas** registrados con cédula, especialidad y token QR.
     - `asistencia_qr`: **244 eventos** de entrada y salida con minutos de retardo y puntualidad.
     - `inventario_insumos`: **55 insumos** médicos con stock mínimo y costo unitario.
     - `recibos_liquidacion`: Historial de liquidaciones con folio único.
     - `conversaciones_whatsapp`: Bitácora de chats y extracciones de la IA.

---

## 💰 3. ¿Por qué este MVP Full-Stack permite cobrar desde el Día 1?

Un software comercial solo se puede cobrar si **resuelve dolores críticos que le ahorran o le hacen ganar dinero al dueño del negocio**:

1. **Captación y Cierre de Pacientes 24/7**:
   - En lugar de perder pacientes que escriben de noche o fines de semana, el Bot de WhatsApp con IA y el cotizador los atienden en menos de 5 segundos, apartan el sillón y los meten a la base de datos.
2. **Cero Fugas en Comisiones de Doctores**:
   - El dueño ya no tiene que hacer cuentas a mano en libretas: con un solo clic en **"Liquidar"**, el sistema calcula el porcentaje exacto de cada especialista y genera un recibo en PDF formal.
3. **Control Total de Puntualidad y Presencia (QR)**:
   - Los doctores no pueden fingir su hora de llegada: cada uno tiene un código QR único en su teléfono que escanean al entrar y salir.
4. **Protección Contra Desabasto y Pérdida de Material**:
   - El inventario descuenta los insumos automáticamente por cada procedimiento, alertando antes de que se termine la anestesia, brackets o resinas.

---

## 📡 4. Verificación de Telemetría (API Endpoint)

Puedes consultar el estado de salud del MVP Full-Stack en cualquier momento en:
* **Local:** `http://localhost:8090/api/mvp/status`
* **Público:** `https://johns-accurately-gen-harris.trycloudflare.com/api/mvp/status`
