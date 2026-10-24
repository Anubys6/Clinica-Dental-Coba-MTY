import os

html_path = r'C:\Users\SAmue\.gemini\antigravity\scratch\clinica-dental-coba-mty\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Hero section
text = text.replace(
    'agenda tu cita en línea y recibe confirmación inmediata por llamada de nuestra IA y WhatsApp.',
    'agenda tu cita y recibe cotización instantánea con Menú Interactivo directo por WhatsApp con nuestro Bot Clínico.'
)

text = text.replace(
    '''                    <a href="#booking-section" class="btn btn-primary">
                        🚀 Agendar Cita y Recibir Llamada IA
                    </a>''',
    '''                    <a href="#booking-section" class="btn btn-primary">
                        💬 Cotizar por WhatsApp (Menú Interactivo)
                    </a>'''
)

# 2. Update Section 6: replace entire Section 6 block
old_sec_start = '<!-- 6. SISTEMA DE BOOKING + CONFIRMACIÓN INMEDIATA EN TIEMPO REAL -->'
old_sec_end = '<!-- 8. TESTIMONIOS DE PACIENTES EN MONTERREY -->'

start_idx = text.find(old_sec_start)
end_idx = text.find(old_sec_end)

if start_idx == -1 or end_idx == -1:
    print('ERROR: Could not find section 6 markers')
    exit(1)

new_section_html = '''<!-- 6. SISTEMA DE COTIZACIÓN Y BOOKING INTERACTIVO POR WHATSAPP -->
    <section class="section" id="booking-section">
        <div class="container">
            <div class="section-header">
                <span class="section-label" style="background: rgba(37,211,102,0.15); color: #25D366; border-color: rgba(37,211,102,0.35);">💬 Cotizador Odontológico y Menú Interactivo WhatsApp</span>
                <h2 class="section-title">Cotiza tu Tratamiento en <span class="text-gradient">30 Segundos por WhatsApp</span></h2>
                <p class="section-subtitle">
                    Completa tus datos clínicos para generar tu cotización personalizada. Al hacer clic, recibirás en tu WhatsApp un <strong>Menú Interactivo con opciones de confirmación, precios desglosados, promociones del mes y atención directa</strong> con nuestros especialistas.
                </p>
            </div>

            <div class="booking-layout">
                <!-- Formulario de Captación y Preguntas Clínicas Necesarias -->
                <div class="glass-card">
                    <form id="lead-booking-form">
                        <div class="form-grid-2">
                            <div class="form-group">
                                <label class="form-label" for="nombre">Nombre Completo *</label>
                                <input type="text" id="nombre" name="nombre" class="form-input" placeholder="Ej. Carlos Garza Treviño" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="telefono">WhatsApp / Celular (10 dígitos) *</label>
                                <input type="tel" id="telefono" name="telefono" class="form-input" placeholder="Ej. 81 1234 5678" required>
                            </div>
                        </div>

                        <div class="form-grid-2">
                            <div class="form-group">
                                <label class="form-label" for="email">Correo Electrónico (Para envío de cotización en PDF) *</label>
                                <input type="email" id="email" name="email" class="form-input" placeholder="carlos.garza@ejemplo.com" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="sucursal">Sucursal Cobá Preferida *</label>
                                <select id="sucursal" name="sucursal" class="form-select" required>
                                    <option value="Monterrey Centro (Jerónimo Treviño #1111 Pte.)">📍 Monterrey Centro (Jerónimo Treviño #1111 Pte.)</option>
                                    <option value="Guadalupe Centro (Benito Juárez #825, Local D)">📍 Guadalupe Centro (Benito Juárez #825, Local D)</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-grid-2">
                            <div class="form-group">
                                <label class="form-label" for="tratamiento">Tratamiento o Procedimiento a Cotizar *</label>
                                <select id="tratamiento" name="tratamiento" class="form-select" required>
                                    <option value="Promo Brackets Metálicos ($1,999 MXN + Limpieza Gratis)">🔥 Promo Brackets Metálicos ($1,999 MXN + Limpieza Gratis)</option>
                                    <option value="Coronas y Puentes Fijos de Zirconia Monolítica">👑 Coronas y Puentes Fijos de Zirconia Monolítica</option>
                                    <option value="Diseño de Sonrisa Digital y Blanqueamiento Láser">✨ Diseño de Sonrisa Digital y Blanqueamiento Láser</option>
                                    <option value="Endodoncia Microscópica y Manejo de Dolor">🛡️ Endodoncia Microscópica y Manejo de Dolor</option>
                                    <option value="Implantes Dentales de Titanio y Cirugía de Juicio">🔩 Implantes Dentales de Titanio y Cirugía de Juicio</option>
                                    <option value="Limpieza Ultrasónica y Paquete de Resinas ($950 MXN)">💧 Limpieza Ultrasónica y Paquete de Resinas ($950 MXN)</option>
                                    <option value="Valoración Odontológica Integral y Diagnóstico General">🦷 Valoración Odontológica Integral y Diagnóstico General</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label" for="urgencia">¿Tienes Dolor o Urgencia Dental? *</label>
                                <select id="urgencia" name="urgencia" class="form-select" required>
                                    <option value="🟢 Sin dolor (Valoración estética, revisión o limpieza)">🟢 Sin dolor (Valoración estética, revisión o limpieza)</option>
                                    <option value="🟡 Molestia moderada (Sensibilidad al frío, calor o masticar)">🟡 Molestia moderada (Sensibilidad al frío, calor o masticar)</option>
                                    <option value="🔴 Dolor agudo constante (Urgencia prioritaria)">🔴 Dolor agudo constante (Urgencia prioritaria)</option>
                                    <option value="⚠️ Pieza fracturada, resina caída o prótesis floja">⚠️ Pieza fracturada, resina caída o prótesis floja</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-grid-2">
                            <div class="form-group">
                                <label class="form-label" for="fecha_cita" style="cursor: pointer;">📅 Fecha Preferida de Cita (Toca para elegir) *</label>
                                <input type="date" id="fecha_cita" name="fecha_cita" class="form-input" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Turno / Horario Preferido *</label>
                                <input type="hidden" id="hora_cita" name="hora_cita" value="11:00 AM">
                                <div class="time-slots-grid" id="time-slots-grid">
                                    <button type="button" class="time-slot-btn" data-time="09:30 AM">09:30 AM</button>
                                    <button type="button" class="time-slot-btn selected" data-time="11:00 AM">11:00 AM</button>
                                    <button type="button" class="time-slot-btn" data-time="12:30 PM">12:30 PM</button>
                                    <button type="button" class="time-slot-btn" data-time="02:00 PM">02:00 PM</button>
                                    <button type="button" class="time-slot-btn" data-time="03:30 PM">03:30 PM</button>
                                    <button type="button" class="time-slot-btn" data-time="04:30 PM">04:30 PM</button>
                                    <button type="button" class="time-slot-btn" data-time="05:15 PM">05:15 PM</button>
                                    <button type="button" class="time-slot-btn" data-time="Sábado Matutino">Sáb 10:30 AM</button>
                                </div>
                            </div>
                        </div>

                        <div class="form-group">
                            <label class="form-label" for="mensaje">Dudas Específicas o Síntomas (Opcional)</label>
                            <textarea id="mensaje" name="mensaje" rows="2" class="form-textarea" placeholder="Cuéntanos si tienes alguna duda sobre costos, meses sin intereses, si cuentas con radiografía previa o detalles de tu molestia..."></textarea>
                        </div>

                        <!-- Backend endpoint predeterminado en background -->
                        <input type="hidden" id="webhook_url_input" value="/webhook/clinica-coba-leads">

                        <div class="form-group" style="display:flex; align-items:center; gap:10px;">
                            <input type="checkbox" id="privacidad" required checked style="width:18px; height:18px; accent-color: #25D366;">
                            <label for="privacidad" style="font-size: 0.85rem; color: var(--text-tertiary);">
                                Acepto el aviso de privacidad y autorizo recibir cotización y atención médica personalizada vía WhatsApp.
                            </label>
                        </div>

                        <button type="submit" class="btn btn-whatsapp-full" id="submit-lead-btn" style="width: 100%; font-size: 1.05rem; padding: 14px 20px;">
                            <span>💬 Enviar a WhatsApp y Abrir Menú Interactivo</span>
                            <span style="font-size: 1.2rem;">📲</span>
                        </button>
                    </form>
                </div>

                <!-- Panel de Proceso y Simulador Interactivo de WhatsApp con Menú -->
                <div class="glass-card automation-live-panel">
                    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom: 10px;">
                        <span class="badge-pill" style="background: rgba(37,211,102,0.15); color: #25D366; border-color: rgba(37,211,102,0.35);">🟢 WhatsApp Bot Clínico Activo</span>
                        <span style="font-family: var(--font-mono); font-size: 0.75rem; color: #25D366;">● EN LÍNEA 24/7</span>
                    </div>
                    <h3 style="font-family: var(--font-display); font-size: 1.3rem; margin-bottom: 6px;">
                        Cotización Cobá Fast-Track™
                    </h3>
                    <p style="font-size: 0.88rem; color: var(--text-tertiary); margin-bottom: 14px;">
                        Al enviar tu solicitud o pulsar una opción, el sistema compilará tu cotización oficial y te entregará este menú interactivo en tu chat:
                    </p>

                    <div class="pipeline-steps" id="pipeline-steps">
                        <div class="pipeline-step" id="step-1">
                            <div class="step-badge">01</div>
                            <div>
                                <strong style="display:block; font-size:0.92rem;">1. Cuestionario Clínico Completo</strong>
                                <span style="font-size:0.78rem; color:var(--text-tertiary);" id="step-1-desc">Registra tus preferencias y síntomas</span>
                            </div>
                        </div>
                        <div class="pipeline-step" id="step-2">
                            <div class="step-badge">02</div>
                            <div>
                                <strong style="display:block; font-size:0.92rem;">2. Asignación de Sede y Especialista</strong>
                                <span style="font-size:0.78rem; color:var(--text-tertiary);" id="step-2-desc">Monterrey Centro o Guadalupe Centro</span>
                            </div>
                        </div>
                        <div class="pipeline-step" id="step-3">
                            <div class="step-badge">03</div>
                            <div>
                                <strong style="display:block; font-size:0.92rem;">3. Generación de Cotización y Promoción</strong>
                                <span style="font-size:0.78rem; color:var(--text-tertiary);" id="step-3-desc">Apartado en agenda clínica y precio especial</span>
                            </div>
                        </div>
                        <div class="pipeline-step" id="step-4">
                            <div class="step-badge">04</div>
                            <div>
                                <strong style="display:block; font-size:0.92rem;">4. Menú Interactivo en WhatsApp Listo</strong>
                                <span style="font-size:0.78rem; color:var(--text-tertiary);" id="step-4-desc">Mensaje compilado listo para enviar al bot</span>
                            </div>
                        </div>
                    </div>

                    <!-- Simulador Interactivo de WhatsApp en Tiempo Real -->
                    <div class="wa-interactive-simulator" id="wa-interactive-simulator">
                        <!-- Cabecera estilo WhatsApp -->
                        <div class="wa-sim-header">
                            <div class="wa-sim-user">
                                <div class="wa-sim-avatar">🦷</div>
                                <div>
                                    <div style="display:flex; align-items:center; gap:6px;">
                                        <strong style="font-size:0.94rem; color:#FFFFFF;">Dr. Cobá | Bot WhatsApp Clínico</strong>
                                        <span style="color:#25D366; font-size:0.9rem;" title="Cuenta Verificada">✓</span>
                                    </div>
                                    <span style="font-size:0.74rem; color:#6EE7B7;" id="wa-sim-status">🟢 En línea • Responde en &lt; 5 seg</span>
                                </div>
                            </div>
                            <a href="https://wa.me/528118483941" target="_blank" rel="noopener" class="wa-sim-app-badge" id="wa-header-link" title="Abrir en WhatsApp">
                                📲 Abrir App
                            </a>
                        </div>

                        <!-- Ventana de Chat Interactiva -->
                        <div class="wa-sim-chat" id="wa-sim-chat">
                            <!-- Mensaje 1: Bienvenida del Bot -->
                            <div class="wa-msg wa-msg-bot">
                                <div class="wa-msg-bubble">
                                    <p>¡Hola! 👋 Bienvenido a <strong>Clínica Dental Cobá</strong> (Sucursales Monterrey Centro y Guadalupe Centro).</p>
                                    <p style="margin-top:5px;">Completa tus datos o toca cualquier opción para recibir tu cotización oficial y menú interactivo directo en WhatsApp.</p>
                                    <span class="wa-msg-time">Ahora • Cobá Bot</span>
                                </div>
                            </div>

                            <!-- Mensaje 2: Ficha del Paciente (Se actualiza dinámicamente) -->
                            <div class="wa-msg wa-msg-patient" id="wa-patient-ticket-msg">
                                <div class="wa-msg-bubble">
                                    <p><strong>📋 Mi Solicitud de Cotización y Consulta:</strong></p>
                                    <div id="wa-ticket-preview-text" style="font-size:0.83rem; line-height:1.45; margin-top:5px;">
                                        • <strong>Paciente:</strong> (Escribe tu nombre...)<br>
                                        • <strong>WhatsApp:</strong> (Ingresa tu celular...)<br>
                                        • <strong>Tratamiento:</strong> Promo Brackets Metálicos<br>
                                        • <strong>Sucursal:</strong> Monterrey Centro<br>
                                        • <strong>Fecha y Turno:</strong> Próxima disponible (11:00 AM)<br>
                                        • <strong>Estado:</strong> Valoración general
                                    </div>
                                    <span class="wa-msg-time" id="wa-ticket-time">En espera</span>
                                </div>
                            </div>

                            <!-- Mensaje 3: Menú Interactivo de Opciones -->
                            <div class="wa-msg wa-msg-bot">
                                <div class="wa-msg-bubble">
                                    <p>📱 <strong>MENÚ INTERACTIVO DR. COBÁ:</strong></p>
                                    <p style="font-size:0.78rem; color:#D1D5DB; margin-top:2px;">_Toca cualquier botón para interactuar o enviar por WhatsApp:_</p>
                                    
                                    <div class="wa-menu-options" id="wa-menu-options">
                                        <button type="button" class="wa-menu-btn" onclick="selectWhatsAppInteractiveOption(1)">
                                            <span class="wa-btn-num">1️⃣</span>
                                            <span class="wa-btn-txt">
                                                <strong>Confirmar y Bloquear Cita en Sillón</strong>
                                                <small>Apartar horario y especialista sin filas</small>
                                            </span>
                                        </button>
                                        <button type="button" class="wa-menu-btn" onclick="selectWhatsAppInteractiveOption(2)">
                                            <span class="wa-btn-num">2️⃣</span>
                                            <span class="wa-btn-txt">
                                                <strong>Cotización Detallada y Planes a Meses</strong>
                                                <small>Precios, promociones y 3, 6, 12 MSI</small>
                                            </span>
                                        </button>
                                        <button type="button" class="wa-menu-btn" onclick="selectWhatsAppInteractiveOption(3)">
                                            <span class="wa-btn-num">3️⃣</span>
                                            <span class="wa-btn-txt">
                                                <strong>🚨 Urgencia Dental por Dolor Agudo</strong>
                                                <small>Pase de prioridad inmediata con especialista</small>
                                            </span>
                                        </button>
                                        <button type="button" class="wa-menu-btn" onclick="selectWhatsAppInteractiveOption(4)">
                                            <span class="wa-btn-num">4️⃣</span>
                                            <span class="wa-btn-txt">
                                                <strong>📍 Ubicación GPS y Cómo Llegar</strong>
                                                <small>Ruta Waze/Maps y estacionamiento privado</small>
                                            </span>
                                        </button>
                                        <button type="button" class="wa-menu-btn" onclick="selectWhatsAppInteractiveOption(5)">
                                            <span class="wa-btn-num">5️⃣</span>
                                            <span class="wa-btn-txt">
                                                <strong>👨‍⚕️ Hablar con un Doctor en Vivo</strong>
                                                <small>Atención personalizada por chat</small>
                                            </span>
                                        </button>
                                    </div>
                                    <span class="wa-msg-time">Opciones 24/7</span>
                                </div>
                            </div>

                            <!-- Mensaje 4: Respuesta del Bot ante selección de opción -->
                            <div class="wa-msg wa-msg-bot" id="wa-dynamic-reply-box" style="display:none;">
                                <div class="wa-msg-bubble" id="wa-dynamic-reply-bubble">
                                    <div id="wa-dynamic-reply-content"></div>
                                    <span class="wa-msg-time">Respuesta Automática</span>
                                </div>
                            </div>
                        </div>

                        <!-- Barra Inferior de Acción Inmediata en WhatsApp -->
                        <div class="wa-sim-footer">
                            <a id="wa-primary-chat-link" href="https://wa.me/528118483941" target="_blank" rel="noopener" class="btn-whatsapp-full">
                                <span>💬 Abrir WhatsApp con Menú Interactivo Activo</span>
                                <span style="font-size:1.15rem;">📲</span>
                            </a>
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px; font-size:0.75rem; color:var(--text-tertiary);">
                                <span>🔒 Encriptación de extremo a extremo</span>
                                <span>⚡ Tiempo de respuesta: Inmediato</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    '''

text = text[:start_idx] + new_section_html + text[end_idx:]

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('SUCCESS: index.html updated successfully!')
