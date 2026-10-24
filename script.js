/* ==========================================================================
   CLÍNICA DENTAL COBÁ MONTERREY — SISTEMA DIGITAL DE CITAS & CONFIRMACIÓN EN TIEMPO REAL
   Motor de Voz Natural en Tiempo Real (/api/tts)
   ========================================================================== */

let currentLeadContext = null;
let currentVoiceAudio = null;
let callPhoneAudioCtx = null;

document.addEventListener('DOMContentLoaded', () => {
    initParticles();
    initNavbar();
    initFlipCards();
    initCounters();
    initPromoQuoter();
    initBookingCalendar();
    initLeadFormWebhook();
    loadExistingLeadsFromBackend();
});

/* 1. Sistema de 50 Partículas Flotantes (Prompt Maestro) */
function initParticles() {
    const container = document.getElementById('particles-container');
    if (!container) return;
    const particleCount = 50;
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = (Math.random() * 18).toFixed(2) + 's';
        particle.style.animationDuration = (14 + Math.random() * 12).toFixed(2) + 's';
        container.appendChild(particle);
    }
}

/* 2. Navbar Sticky & Menú Móvil */
function initNavbar() {
    const navbar = document.getElementById('navbar');
    const toggle = document.getElementById('mobile-menu-toggle');
    const navLinks = document.getElementById('nav-links');

    window.addEventListener('scroll', () => {
        if (window.scrollY > 30) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }, { passive: true });

    if (toggle && navLinks) {
        toggle.addEventListener('click', () => {
            navLinks.classList.toggle('open');
        });
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => navLinks.classList.remove('open'));
        });
    }
}

/* 3. Flip Cards 3D: Pasa el cursor y se voltea UNA SOLA VEZ para leer, y solo con clic se regresa a la imagen original */
function initFlipCards() {
    const cards = document.querySelectorAll('.service-card-flip');
    cards.forEach(card => {
        // 1. Al pasar el cursor, se voltea una sola vez y se queda fija para poder leer cómodamente
        card.addEventListener('mouseenter', () => {
            if (!card.classList.contains('flipped')) {
                card.classList.add('flipped');
            }
        });

        // 2. Al hacer clic (o en el botón de volver), regresa a la foto original
        card.addEventListener('click', (e) => {
            if (e.target.closest('a') || e.target.closest('button')) return;
            card.classList.toggle('flipped');
        });
    });
}

window.selectTreatmentFromCard = function(treatmentName) {
    const select = document.getElementById('tratamiento');
    if (!select) return;
    for (let i = 0; i < select.options.length; i++) {
        if (select.options[i].value === treatmentName || select.options[i].text.includes(treatmentName)) {
            select.selectedIndex = i;
            break;
        }
    }
    const nombreInput = document.getElementById('nombre');
    if (nombreInput) {
        setTimeout(() => nombreInput.focus(), 500);
    }
};

/* 4. Contadores Animados con IntersectionObserver */
function initCounters() {
    const counters = document.querySelectorAll('.counter');
    if (!counters.length) return;

    const animateCounter = (el, target, duration = 1800) => {
        const increment = target / (duration / 16);
        let current = 0;
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                el.textContent = target.toLocaleString('es-MX');
                clearInterval(timer);
            } else {
                el.textContent = Math.round(current).toLocaleString('es-MX');
            }
        }, 16);
    };

    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const el = entry.target;
                const target = parseInt(el.getAttribute('data-target') || '0', 10);
                animateCounter(el, target);
                obs.unobserve(el);
            }
        });
    }, { threshold: 0.25 });

    counters.forEach(c => observer.observe(c));
}

/* 5. Cotizador Interactivo de Promociones Reales de Clínica Dental Cobá */
function initPromoQuoter() {
    const promoData = {
        brackets: {
            badge: '🔥 Promoción Más Solicitada en Monterrey y Guadalupe',
            title: 'Paquete Completo de Brackets Metálicos',
            price: '$1,999 MXN',
            oldPrice: '$4,500 MXN',
            treatmentOption: 'Promo Brackets Metálicos ($1,999 MXN + Limpieza Gratis)',
            items: [
                '✅ Instalación completa de Brackets Metálicos (Arcada Superior e Inferior)',
                '✅ Limpieza dental ultrasónica incluida GRATIS en tu colocación',
                '✅ Consultas de ajuste mensual accesibles ($250 MXN)',
                '✅ Disponible en Sucursal Monterrey Centro y Guadalupe Centro'
            ]
        },
        zirconia: {
            badge: '💎 Rehabilitación Protésica de Alta Estética',
            title: 'Coronas y Puentes Fijos en Zirconia / Porcelana',
            price: 'Desde $3,800 MXN',
            oldPrice: '$5,200 MXN',
            treatmentOption: 'Coronas y Puentes Fijos de Zirconia',
            items: [
                '✅ Escaneo y ajuste protésico de alta precisión libre de metal',
                '✅ Translucidez y color natural idéntico a tus dientes',
                '✅ Esquema de pagos parciales durante tu rehabilitación',
                '✅ Garantía funcional y estética en ambas sucursales'
            ]
        },
        endodoncia: {
            badge: '🛡️ Atención Inmediata de Dolor Dental',
            title: 'Endodoncia Especializada Sin Dolor',
            price: 'Desde $2,400 MXN',
            oldPrice: '$3,500 MXN',
            treatmentOption: 'Endodoncia Especializada / Urgencia Dental',
            items: [
                '✅ Eliminación total del dolor e infección desde la primera sesión',
                '✅ Realizada por especialistas en endodoncia con equipo rotatorio',
                '✅ Conserva tu pieza dental natural evitando extracciones',
                '✅ Prioridad de agenda para pacientes con molestia aguda'
            ]
        },
        limpieza: {
            badge: '✨ Paquete Preventivo y Estético Familiar',
            title: 'Valoración + Limpieza Ultrasónica + 2 Resinas',
            price: '$950 MXN',
            oldPrice: '$1,600 MXN',
            treatmentOption: 'Limpieza Ultrasónica y Paquete de Resinas',
            items: [
                '✅ Eliminación de sarro con ultrasonido y pulido profiláctico',
                '✅ 2 resinas estéticas de alta durabilidad del tono de tu diente',
                '✅ Diagnóstico integral con cámara intraoral',
                '✅ Ideal para iniciar tu cuidado dental sin dolor'
            ]
        }
    };

    const buttons = document.querySelectorAll('.promo-option-btn');
    const badgeEl = document.getElementById('promo-badge');
    const titleEl = document.getElementById('promo-title');
    const priceEl = document.getElementById('promo-price');
    const oldPriceEl = document.getElementById('promo-old-price');
    const listEl = document.getElementById('promo-checklist');
    const ctaBtn = document.getElementById('promo-cta-btn');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            buttons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const key = btn.getAttribute('data-promo');
            const info = promoData[key];
            if (!info) return;

            badgeEl.textContent = info.badge;
            titleEl.textContent = info.title;
            priceEl.textContent = info.price;
            oldPriceEl.textContent = info.oldPrice;
            listEl.innerHTML = info.items.map(item => `<li>${item}</li>`).join('');
            ctaBtn.setAttribute('onclick', `selectTreatmentFromCard('${info.treatmentOption}')`);
        });
    });
}

/* 6. Calendario de Booking y Selección de Horario */
function initBookingCalendar() {
    const dateInput = document.getElementById('fecha_cita');
    if (dateInput) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        if (tomorrow.getDay() === 0) {
            tomorrow.setDate(tomorrow.getDate() + 1);
        }
        const yyyy = tomorrow.getFullYear();
        const mm = String(tomorrow.getMonth() + 1).padStart(2, '0');
        const dd = String(tomorrow.getDate()).padStart(2, '0');
        dateInput.value = `${yyyy}-${mm}-${dd}`;
        dateInput.min = `${yyyy}-${mm}-${dd}`;

        const openCalendarPicker = () => {
            try {
                if (typeof dateInput.showPicker === 'function') {
                    dateInput.showPicker();
                }
            } catch (err) {
                // Silently handle if already open
            }
        };

        // Al tocar o dar click en cualquier parte de la casilla, se abre el calendario inmediatamente
        dateInput.addEventListener('click', openCalendarPicker);
        dateInput.addEventListener('focus', openCalendarPicker);
        dateInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ' || e.key === 'ArrowDown') {
                e.preventDefault();
                openCalendarPicker();
            }
        });
    }

    const slotBtns = document.querySelectorAll('.time-slot-btn');
    const hiddenTime = document.getElementById('hora_cita');
    slotBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            slotBtns.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            if (hiddenTime) hiddenTime.value = btn.getAttribute('data-time');
        });
    });
}

/* 7. Envío de Cotización por WhatsApp con Menú Interactivo */
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

    let msg = `🦷 *CLÍNICA DENTAL COBÁ — COTIZACIÓN Y CITA DIGITAL* 🦷

`;
    msg += `¡Hola Dr. Cobá! Deseo cotizar mi tratamiento y agendar una valoración con su Bot Especializado:

`;
    msg += `📋 *DATOS DE MI SOLICITUD:*
`;
    msg += `• *Paciente:* ${payload.nombre || 'Paciente'}
`;
    msg += `• *Teléfono:* ${payload.telefono || 'Sin especificar'}
`;
    if (payload.email) msg += `• *Correo:* ${payload.email}
`;
    msg += `• *Sucursal:* ${sucursalNombre}
`;
    msg += `• *Tratamiento de Interés:* ${payload.tratamiento || 'Valoración General'}
`;
    msg += `• *Nivel de Urgencia / Dolor:* ${payload.urgencia || 'Sin dolor'}
`;
    msg += `• *Fecha Deseada:* ${payload.fecha_cita || 'Próxima disponible'}
`;
    msg += `• *Horario Preferido:* ${payload.hora_cita || '11:00 AM'}
`;
    if (payload.mensaje) msg += `• *Notas / Síntomas:* ${payload.mensaje}
`;

    msg += `
━━━━━━━━━━━━━━━━━━━━
`;
    msg += `📱 *MENÚ INTERACTIVO DE ATENCIÓN DIRECTA:*
`;
    msg += `_Por favor responde con el número de tu opción:_

`;
    msg += `1️⃣ *Confirmar y Bloquear Cita en Sillón* (Apartar horario y especialista)
`;
    msg += `2️⃣ *Recibir Cotización Desglosada con Precios y MSI* (Opciones de pago a 3, 6 o 12 meses)
`;
    msg += `3️⃣ *🚨 Urgencia Dental por Dolor Agudo* (Pase prioritario inmediato sin cita previa)
`;
    msg += `4️⃣ *📍 Ubicación GPS y Cómo Llegar* (Monterrey Centro o Guadalupe + Estacionamiento)
`;
    msg += `5️⃣ *👨‍⚕️ Hablar con Odontólogo Especialista en Vivo*
`;
    msg += `━━━━━━━━━━━━━━━━━━━━
`;

    if (chosenOption) {
        msg += `
👉 *Opción inicial seleccionada:* ${chosenOption}
`;
    }

    msg += `
_Quedo a la espera de su respuesta inmediata para confirmar. ¡Muchas gracias!_`;
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

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function escapeHtml(str) {
    return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}


// Toggle del Widget de WhatsApp Bot Especializado
function toggleWaBotCard(forceState) {
    const card = document.getElementById('waBotCard');
    if (!card) return;
    if (typeof forceState === 'boolean') {
        if (forceState) card.classList.add('open');
        else card.classList.remove('open');
    } else {
        card.classList.toggle('open');
    }
}
