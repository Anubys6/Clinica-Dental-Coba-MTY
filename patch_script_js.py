import os

js_path = r'C:\Users\SAmue\.gemini\antigravity\scratch\clinica-dental-coba-mty\script.js'

with open(js_path, 'r', encoding='utf-8') as f:
    text = f.read()

# Locate section 7 start
sec7_marker = '/* 7. Envío del Formulario'
if sec7_marker not in text:
    sec7_marker = '/* 7. Env'

sec7_idx = text.find(sec7_marker)
if sec7_idx == -1:
    print('ERROR: Could not find section 7 marker')
    exit(1)

# Locate sleep function before which section 7/8/9 ends
sleep_marker = 'function sleep(ms)'
sleep_idx = text.find(sleep_marker)
if sleep_idx == -1:
    print('ERROR: Could not find sleep function marker')
    exit(1)

new_code = '''/* 7. Envío de Cotización por WhatsApp con Menú Interactivo */
let currentWhatsAppPayload = {
    nombre: '',
    telefono: '',
    email: '',
    sucursal: 'Monterrey Centro (Jerónimo Treviño #1111 Pte.)',
    tratamiento: 'Promo Brackets Metálicos ($1,999 MXN + Limpieza Gratis)',
    urgencia: '🟢 Sin dolor (Valoración estética, revisión o limpieza)',
    fecha_cita: '',
    hora_cita: '11:00 AM',
    mensaje: ''
};

function initLeadFormWebhook() {
    const form = document.getElementById('lead-booking-form');
    if (!form) return;

    // Listeners para actualizar en tiempo real el ticket del simulador de WhatsApp
    const inputs = ['nombre', 'telefono', 'email', 'sucursal', 'tratamiento', 'urgencia', 'fecha_cita', 'mensaje'];
    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', updateLiveWhatsAppPreview);
            el.addEventListener('change', updateLiveWhatsAppPreview);
        }
    });

    // Time slot click listeners
    const slotBtns = document.querySelectorAll('.time-slot-btn');
    slotBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            slotBtns.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            const hiddenTime = document.getElementById('hora_cita');
            if (hiddenTime) hiddenTime.value = btn.dataset.time || btn.textContent.trim();
            updateLiveWhatsAppPreview();
        });
    });

    // Inicializar la vista previa con valores actuales
    updateLiveWhatsAppPreview();

    // Evento de Envío del Formulario
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById('submit-lead-btn');
        const originalHtml = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span>⏳ Compilando tu Menú de WhatsApp...</span>';

        const payload = gatherBookingFormData();
        currentWhatsAppPayload = payload;

        // Ejecutar animación de pipeline de fast-track
        const webhookUrl = document.getElementById('webhook_url_input')?.value?.trim() || '/webhook/clinica-coba-leads';
        await runWhatsAppFastTrackPipeline(payload, webhookUrl);

        // Generar el mensaje estructurado de WhatsApp con el menú interactivo
        const waText = generateWhatsAppStructuredMessage(payload);
        const waUrl = `https://wa.me/528118483941?text=${encodeURIComponent(waText)}`;

        // Actualizar enlaces del simulador
        updateSimulatorWhatsAppLinks(waUrl);

        // Actualizar visual del chat en el simulador
        renderSubmissionInSimulator(payload);

        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span>✅ ¡Abriendo tu WhatsApp con Menú! 📲</span>';

        // Abrir WhatsApp en pestaña nueva
        window.open(waUrl, '_blank');

        setTimeout(() => {
            submitBtn.innerHTML = originalHtml;
        }, 5000);
    });
}

function gatherBookingFormData() {
    const nombre = document.getElementById('nombre')?.value.trim() || 'Paciente';
    const telefono = document.getElementById('telefono')?.value.trim() || '';
    const email = document.getElementById('email')?.value.trim() || '';
    const sucursal = document.getElementById('sucursal')?.value || 'Monterrey Centro (Jerónimo Treviño #1111 Pte.)';
    const tratamiento = document.getElementById('tratamiento')?.value || 'Valoración General';
    const urgencia = document.getElementById('urgencia')?.value || '🟢 Sin dolor';
    const fecha_cita = document.getElementById('fecha_cita')?.value || '';
    const hora_cita = document.getElementById('hora_cita')?.value || '11:00 AM';
    const mensaje = document.getElementById('mensaje')?.value.trim() || '';

    return {
        nombre,
        telefono,
        email,
        sucursal,
        tratamiento,
        urgencia,
        fecha_cita,
        hora_cita,
        mensaje,
        source: 'Cotizador Web Cobá MTY',
        timestamp: new Date().toISOString()
    };
}

function updateLiveWhatsAppPreview() {
    const payload = gatherBookingFormData();
    currentWhatsAppPayload = payload;

    const previewBox = document.getElementById('wa-ticket-preview-text');
    if (previewBox) {
        previewBox.innerHTML = `
            • <strong>Paciente:</strong> ${escapeHtml(payload.nombre || 'Escribe tu nombre...')}<br>
            • <strong>WhatsApp:</strong> ${escapeHtml(payload.telefono || 'Ingresa tu celular...')}<br>
            • <strong>Tratamiento:</strong> ${escapeHtml(payload.tratamiento)}<br>
            • <strong>Sucursal:</strong> ${escapeHtml(payload.sucursal.includes('Guadalupe') ? 'Guadalupe Centro' : 'Monterrey Centro')}<br>
            • <strong>Fecha y Horario:</strong> ${escapeHtml(payload.fecha_cita || 'Por definir')} a las ${escapeHtml(payload.hora_cita)}<br>
            • <strong>Molestia / Urgencia:</strong> ${escapeHtml(payload.urgencia.split('(')[0].trim())}
        `;
    }

    // Actualizar URL predeterminada de WhatsApp
    const waText = generateWhatsAppStructuredMessage(payload);
    const waUrl = `https://wa.me/528118483941?text=${encodeURIComponent(waText)}`;
    updateSimulatorWhatsAppLinks(waUrl);
}

function updateSimulatorWhatsAppLinks(url) {
    const primaryBtn = document.getElementById('wa-primary-chat-link');
    if (primaryBtn) primaryBtn.href = url;
    const headerBtn = document.getElementById('wa-header-link');
    if (headerBtn) headerBtn.href = url;
}

function generateWhatsAppStructuredMessage(payload, chosenOption = null) {
    const sucursalNombre = payload.sucursal?.includes('Guadalupe')
        ? 'Sucursal Guadalupe Centro (Benito Juárez #825, Local D)'
        : 'Sucursal Monterrey Centro (Jerónimo Treviño #1111 Pte.)';

    let msg = `🦷 *CLÍNICA DENTAL COBÁ — COTIZACIÓN Y CITA DIGITAL* 🦷\n\n`;
    msg += `¡Hola Dr. Cobá! Deseo cotizar mi tratamiento y agendar una valoración con su Bot Especializado:\n\n`;
    msg += `📋 *DATOS DE MI SOLICITUD:*\n`;
    msg += `• *Paciente:* ${payload.nombre || 'Paciente'}\n`;
    msg += `• *Teléfono:* ${payload.telefono || 'Sin especificar'}\n`;
    if (payload.email) msg += `• *Correo:* ${payload.email}\n`;
    msg += `• *Sucursal:* ${sucursalNombre}\n`;
    msg += `• *Tratamiento de Interés:* ${payload.tratamiento || 'Valoración General'}\n`;
    msg += `• *Nivel de Urgencia / Dolor:* ${payload.urgencia || 'Sin dolor'}\n`;
    msg += `• *Fecha Deseada:* ${payload.fecha_cita || 'Próxima disponible'}\n`;
    msg += `• *Horario Preferido:* ${payload.hora_cita || '11:00 AM'}\n`;
    if (payload.mensaje) msg += `• *Notas / Síntomas:* ${payload.mensaje}\n`;

    msg += `\n━━━━━━━━━━━━━━━━━━━━\n`;
    msg += `📱 *MENÚ INTERACTIVO DE ATENCIÓN DIRECTA:*\n`;
    msg += `_Por favor responde con el número de tu opción:_\n\n`;
    msg += `1️⃣ *Confirmar y Bloquear Cita en Sillón* (Apartar horario y especialista)\n`;
    msg += `2️⃣ *Recibir Cotización Desglosada con Precios y MSI* (Opciones de pago a 3, 6 o 12 meses)\n`;
    msg += `3️⃣ *🚨 Urgencia Dental por Dolor Agudo* (Pase prioritario inmediato sin cita previa)\n`;
    msg += `4️⃣ *📍 Ubicación GPS y Cómo Llegar* (Monterrey Centro o Guadalupe + Estacionamiento)\n`;
    msg += `5️⃣ *👨‍⚕️ Hablar con Odontólogo Especialista en Vivo*\n`;
    msg += `━━━━━━━━━━━━━━━━━━━━\n`;

    if (chosenOption) {
        msg += `\n👉 *Opción inicial seleccionada:* ${chosenOption}\n`;
    }

    msg += `\n_Quedo a la espera de su respuesta inmediata para confirmar. ¡Muchas gracias!_`;
    return msg;
}

async function runWhatsAppFastTrackPipeline(payload, webhookUrl) {
    const setStepState = (stepNum, state, descText) => {
        const stepEl = document.getElementById(`step-${stepNum}`);
        const descEl = document.getElementById(`step-${stepNum}-desc`);
        if (!stepEl) return;
        stepEl.classList.remove('active', 'done');
        if (state) stepEl.classList.add(state);
        if (descText && descEl) descEl.textContent = descText;
    };

    for (let i = 1; i <= 4; i++) setStepState(i, '');

    setStepState(1, 'active', 'Validando cuestionario clínico...');
    let webhookResult = null;
    try {
        const res = await fetch(webhookUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (res.ok) {
            webhookResult = await res.json();
        }
    } catch (err) {
        console.log('Registro local de solicitud:', err.message);
    }

    await sleep(250);
    setStepState(1, 'done', `Solicitud recibida (${payload.nombre} • ${payload.telefono})`);

    const sucursalCorta = payload.sucursal.includes('Guadalupe') ? 'Guadalupe Centro' : 'Monterrey Centro';
    setStepState(2, 'active', `Asignando turno en ${sucursalCorta}...`);
    await sleep(280);
    setStepState(2, 'done', `Sede confirmada: ${sucursalCorta} • ${payload.fecha_cita || 'Próxima'} ${payload.hora_cita}`);

    setStepState(3, 'active', 'Calculando presupuesto y pase digital...');
    await sleep(280);
    prependLeadToCrmTable(payload);
    setStepState(3, 'done', `Cotización y folio listos para ${payload.email}`);

    setStepState(4, 'active', 'Conectando con Bot Oficial de WhatsApp...');
    await sleep(300);
    setStepState(4, 'done', `Menú interactivo entregado a WhatsApp (+52 81 1848 3941)`);
}

function renderSubmissionInSimulator(payload) {
    const timeEl = document.getElementById('wa-ticket-time');
    if (timeEl) {
        const now = new Date();
        timeEl.textContent = `${now.getHours()}:${String(now.getMinutes()).padStart(2, '0')} • Enviado`;
    }

    const replyBox = document.getElementById('wa-dynamic-reply-box');
    const replyContent = document.getElementById('wa-dynamic-reply-content');
    if (replyBox && replyContent) {
        replyBox.style.display = 'flex';
        replyContent.innerHTML = `
            <p>🎉 <strong>¡Solicitud de Cotización Recibida, ${escapeHtml(payload.nombre)}!</strong></p>
            <p style="margin-top:4px;">Tu información para <strong>${escapeHtml(payload.tratamiento)}</strong> ha sido procesada con éxito. Ya puedes responder directamente en WhatsApp con el número del menú que deseas para atenderte al instante.</p>
        `;
        const chat = document.getElementById('wa-sim-chat');
        if (chat) chat.scrollTop = chat.scrollHeight;
    }
}

// Interacción con los botones del menú de WhatsApp en el simulador
window.selectWhatsAppInteractiveOption = function(optionNum) {
    const payload = gatherBookingFormData();
    const replyBox = document.getElementById('wa-dynamic-reply-box');
    const replyContent = document.getElementById('wa-dynamic-reply-content');
    if (!replyBox || !replyContent) return;

    let responseHtml = '';
    let optionTitle = '';

    switch(optionNum) {
        case 1:
            optionTitle = '1️⃣ Confirmar y Bloquear Cita en Sillón';
            responseHtml = `
                <p>🦷 <strong>Confirmación Inmediata de Sillón Dental:</strong></p>
                <p style="margin-top:4px;">Hemos reservado preventivamente tu turno en <strong>${payload.sucursal.includes('Guadalupe') ? 'Guadalupe Centro' : 'Monterrey Centro'}</strong> para <em>${payload.fecha_cita || 'la fecha que indiques'}</em> a las <em>${payload.hora_cita}</em>.</p>
                <p style="margin-top:4px; font-size:0.78rem; color:#6EE7B7;">👉 Al presionar el botón verde abajo, recepción confirmará tu doctor especialista en turno sin costo de apartado.</p>
            `;
            break;
        case 2:
            optionTitle = '2️⃣ Cotización Detallada y Meses Sin Intereses';
            responseHtml = `
                <p>💎 <strong>Cotización y Formas de Pago:</strong></p>
                <p style="margin-top:4px;">Tu tratamiento <strong>${escapeHtml(payload.tratamiento)}</strong> cuenta con nuestra promoción activa del mes. Aceptamos efectivo, transferencias SPEI y tarjetas a <strong>3, 6 y 12 Meses Sin Intereses</strong>.</p>
                <p style="margin-top:4px; font-size:0.78rem; color:#6EE7B7;">👉 Toca el botón verde abajo para recibir el PDF de tu presupuesto oficial por WhatsApp.</p>
            `;
            break;
        case 3:
            optionTitle = '3️⃣ 🚨 Urgencia Dental por Dolor Agudo';
            responseHtml = `
                <p>🚨 <strong>Atención Prioritaria de Urgencia:</strong></p>
                <p style="margin-top:4px;">Si sufres de dolor intenso, fractura o inflamación, contamos con <strong>sillón de urgencias disponible</strong> en Monterrey Centro (81 8374 6726) y Guadalupe Centro (81 8070 1778).</p>
                <p style="margin-top:4px; font-size:0.78rem; color:#F87171;">⚡ Atención prioritaria sin tiempo de espera. Toca el botón para canalizarte de inmediato.</p>
            `;
            break;
        case 4:
            optionTitle = '4️⃣ 📍 Ubicación GPS y Cómo Llegar';
            responseHtml = `
                <p>📍 <strong>Sucursales Oficiales de Clínica Cobá:</strong></p>
                <p style="margin-top:4px;">• <strong>Monterrey Centro:</strong> Jerónimo Treviño #1111 Pte. (entre Juan Álvarez y Serafín Peña). Contamos con estacionamiento exclusivo.<br>• <strong>Guadalupe Centro:</strong> Benito Juárez #825, Local D, 2do Piso.</p>
                <p style="margin-top:4px; font-size:0.78rem; color:#6EE7B7;">👉 Toca el botón abajo para recibir el link de Google Maps y Waze directo a tu WhatsApp.</p>
            `;
            break;
        case 5:
            optionTitle = '5️⃣ 👨‍⚕️ Hablar con Odontólogo Especialista';
            responseHtml = `
                <p>👨‍⚕️ <strong>Conexión con Doctor en Vivo:</strong></p>
                <p style="margin-top:4px;">Te canalizamos directamente con el Dr. Cobá o el especialista de turno (Ortodoncia, Endodoncia o Rehabilitación Oral).</p>
                <p style="margin-top:4px; font-size:0.78rem; color:#6EE7B7;">💬 Toca el botón verde para iniciar la conversación en WhatsApp ahora mismo.</p>
            `;
            break;
    }

    replyBox.style.display = 'flex';
    replyContent.innerHTML = responseHtml;

    // Actualizar enlace con la opción específica preseleccionada
    const waText = generateWhatsAppStructuredMessage(payload, optionTitle);
    const waUrl = `https://wa.me/528118483941?text=${encodeURIComponent(waText)}`;
    updateSimulatorWhatsAppLinks(waUrl);

    const chat = document.getElementById('wa-sim-chat');
    if (chat) chat.scrollTop = chat.scrollHeight;
};

// Acceso rápido para seleccionar tratamiento desde las tarjetas de servicios
window.selectTreatmentFromCard = function(treatmentName) {
    const sel = document.getElementById('tratamiento');
    if (sel) {
        for (let i = 0; i < sel.options.length; i++) {
            if (sel.options[i].value.includes(treatmentName) || sel.options[i].text.includes(treatmentName)) {
                sel.selectedIndex = i;
                break;
            }
        }
    }
    updateLiveWhatsAppPreview();
    const bookingSec = document.getElementById('booking-section');
    if (bookingSec) bookingSec.scrollIntoView({ behavior: 'smooth' });
};

'''

text = text[:sec7_idx] + new_code + text[sleep_idx:]

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(text)

print('SUCCESS: script.js updated with interactive WhatsApp intake and menu!')
