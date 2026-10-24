/* ==========================================================================
   AUTOMATIC — MOTOR DEL COMERCIAL CINEMATOGRÁFICO, CALCULADORA & VALERIA IA
   Con Voz Femenina Neural HD en Tiempo Real (/api/tts)
   ========================================================================== */

const COMMERCIAL_SCENES = [
    {
        tag: 'ACTO I // LA REALIDAD CRUDA EN MONTERREY',
        title: 'SON LAS 3:00 PM EN MONTERREY.<br><span class="gold-gradient">ACABAS DE QUEMAR TU PRESUPUESTO.</span>',
        subtitle: '«Son las tres de la tarde aquí en Monterrey... Acabas de invertir miles de pesos en publicidad. Un cliente entra a tus redes, pide informes... y nadie le contesta. Para las cinco de la tarde, ese cliente ya le compró a tu competencia.»',
        bg: 'images/scene_monterrey.png',
        audio: 'images/scene_1.mp3?v=female_hd'
    },
    {
        tag: 'ACTO II // EL GOLPE DE AUTORIDAD',
        title: 'NO CONTRATES MÁS MANOS.<br><span class="gold-gradient">INSTALA INFRAESTRUCTURA AUTOMATIC.</span>',
        subtitle: '«Mira, los negocios tradicionales contratan más personal para copiar datos en Excel y perseguir curiosos. Pero las empresas que hoy dominan su mercado no contratan más manos... instalan Automatic.»',
        bg: 'images/scene_command.png',
        audio: 'images/scene_2.mp3?v=female_hd'
    },
    {
        tag: 'ACTO III // VOZ HUMANA EN 8 SEGUNDOS',
        title: 'CAPTURA EN CRM + LLAMADA IA<br><span class="gold-gradient">CON VOZ DE MUJER REAL EN 8 SEGUNDOS.</span>',
        subtitle: '«En solo ocho segundos desde que un cliente deja sus datos en tu página, nuestro sistema lo guarda en tu base de datos y le marca a su celular con una voz tan natural como la mía... resuelve todas sus dudas y deja agendada su cita.»',
        bg: 'images/scene_dental_case.png',
        audio: 'images/scene_3.mp3?v=female_hd'
    },
    {
        tag: 'ACTO IV // DOMINIO TOTAL 24/7/365',
        title: 'AUTOMATIC MONTERREY.<br><span class="gold-gradient">AUTOMATIZA O DESAPARECE.</span>',
        subtitle: '«Sin descansos, sin pretextos, veinticuatro horas, los trescientos sesenta y cinco días del año... Automatic. Inteligencia Artificial que suena humana y vende por ti. Automatiza, o desaparece.»',
        bg: 'images/hero_visual.png',
        audio: 'images/scene_4.mp3?v=female_hd'
    }
];

let isPlayingCommercial = false;
let currentSceneIndex = 0;
let activeAudio = null;
let audioCtx = null;
let droneOsc1 = null;
let droneGain = null;
let wavePhase = 0;
let valeriaVoiceAudio = null;

document.addEventListener('DOMContentLoaded', () => {
    initCommercialCanvas();
    initRoiCalculator();
    initViktorB2BForm();
});

/* ==========================================================================
   1. MOTOR DE CINE Y SONIDO DEL COMERCIAL OFICIAL DE AUTOMATIC
   ========================================================================== */
window.startOfficialCommercial = function() {
    document.getElementById('commercial-theatre')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    playCommercialFromScene(0);
};

window.toggleCommercialPlayback = function() {
    if (isPlayingCommercial) {
        stopCommercial();
    } else {
        playCommercialFromScene(currentSceneIndex >= COMMERCIAL_SCENES.length ? 0 : currentSceneIndex);
    }
};

window.jumpToScene = function(idx) {
    playCommercialFromScene(idx);
};

function startCinematicDrone() {
    try {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        if (!AudioContextClass) return;
        if (!audioCtx) audioCtx = new AudioContextClass();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        stopCinematicDrone();

        droneOsc1 = audioCtx.createOscillator();
        const droneOsc2 = audioCtx.createOscillator();
        const filter = audioCtx.createBiquadFilter();
        droneGain = audioCtx.createGain();

        droneOsc1.type = 'sawtooth';
        droneOsc1.frequency.setValueAtTime(55, audioCtx.currentTime);
        droneOsc2.type = 'triangle';
        droneOsc2.frequency.setValueAtTime(110, audioCtx.currentTime);

        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(150, audioCtx.currentTime);

        droneGain.gain.setValueAtTime(0.01, audioCtx.currentTime);
        droneGain.gain.exponentialRampToValueAtTime(0.075, audioCtx.currentTime + 1.2);

        droneOsc1.connect(filter);
        droneOsc2.connect(filter);
        filter.connect(droneGain);
        droneGain.connect(audioCtx.destination);

        droneOsc1.start();
        droneOsc2.start();
        droneOsc1._partner = droneOsc2;
    } catch (e) {
        console.log('WebAudio drone:', e);
    }
}

function playImpactBoom() {
    try {
        if (!audioCtx) return;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(125, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(28, audioCtx.currentTime + 0.65);
        gain.gain.setValueAtTime(0.24, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.7);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + 0.72);
    } catch (_) {}
}

function stopCinematicDrone() {
    try {
        if (droneOsc1) {
            droneOsc1.stop();
            if (droneOsc1._partner) droneOsc1._partner.stop();
            droneOsc1.disconnect();
            droneOsc1 = null;
        }
    } catch (_) {}
}

function stopCommercial() {
    isPlayingCommercial = false;
    if (activeAudio) {
        activeAudio.pause();
        activeAudio.currentTime = 0;
        activeAudio = null;
    }
    stopCinematicDrone();
    const btn = document.getElementById('play-toggle-btn');
    if (btn) btn.innerHTML = '▶ REANUDAR COMERCIAL';
}

function playCommercialFromScene(idx) {
    if (activeAudio) {
        activeAudio.pause();
        activeAudio = null;
    }
    if (valeriaVoiceAudio) {
        valeriaVoiceAudio.pause();
        valeriaVoiceAudio = null;
    }
    isPlayingCommercial = true;
    currentSceneIndex = idx;

    const btn = document.getElementById('play-toggle-btn');
    if (btn) btn.innerHTML = '⏸ DETENER COMERCIAL';

    startCinematicDrone();
    playImpactBoom();
    renderSceneVisuals(idx);

    const scene = COMMERCIAL_SCENES[idx];
    const audio = new Audio(scene.audio);
    activeAudio = audio;

    audio.addEventListener('timeupdate', () => {
        if (!audio.duration) return;
        const sceneShare = 100 / COMMERCIAL_SCENES.length;
        const totalPct = (idx * sceneShare) + ((audio.currentTime / audio.duration) * sceneShare);
        const fill = document.getElementById('commercial-progress-fill');
        if (fill) fill.style.width = `${Math.min(100, totalPct)}%`;

        const elapsed = Math.floor(idx * 9.5 + audio.currentTime);
        const tc = document.getElementById('theatre-timecode');
        if (tc) tc.textContent = `00:${String(Math.min(38, elapsed)).padStart(2, '0')} / 00:38`;
    });

    audio.addEventListener('ended', () => {
        if (!isPlayingCommercial) return;
        if (idx + 1 < COMMERCIAL_SCENES.length) {
            playCommercialFromScene(idx + 1);
        } else {
            playImpactBoom();
            stopCommercial();
            const fill = document.getElementById('commercial-progress-fill');
            if (fill) fill.style.width = '100%';
            if (btn) btn.innerHTML = '↻ REPETIR COMERCIAL OFICIAL';
        }
    });

    audio.play().catch(err => console.error('Audio play error:', err));
}

function renderSceneVisuals(idx) {
    const scene = COMMERCIAL_SCENES[idx];
    if (!scene) return;
    const tagEl = document.getElementById('commercial-scene-tag');
    const titleEl = document.getElementById('commercial-kinetic-title');
    const subEl = document.getElementById('commercial-subtitle-box');
    const bgEl = document.getElementById('commercial-bg-slide');

    if (tagEl) tagEl.textContent = scene.tag;
    if (titleEl) titleEl.innerHTML = scene.title;
    if (subEl) subEl.textContent = scene.subtitle;
    if (bgEl) {
        bgEl.classList.remove('zooming');
        bgEl.src = scene.bg;
        void bgEl.offsetWidth;
        bgEl.classList.add('zooming');
    }
}

function initCommercialCanvas() {
    const canvas = document.getElementById('commercial-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const resize = () => {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        wavePhase += isPlayingCommercial ? 0.09 : 0.02;
        const amp = isPlayingCommercial ? 38 : 8;
        const midY = canvas.height - 55;

        ctx.beginPath();
        ctx.strokeStyle = isPlayingCommercial ? 'rgba(251, 191, 36, 0.78)' : 'rgba(245, 158, 11, 0.25)';
        ctx.lineWidth = 2.5;
        for (let x = 0; x < canvas.width; x += 6) {
            const y = midY + Math.sin(x * 0.018 + wavePhase) * amp * Math.sin(x * 0.004 + wavePhase * 0.5);
            if (x === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.stroke();

        requestAnimationFrame(draw);
    }
    draw();
}

/* ==========================================================================
   2. CALCULADORA DE FUGA DE CAPITAL EN MONTERREY
   ========================================================================== */
function initRoiCalculator() {
    const sLeads = document.getElementById('slider-leads');
    const sTicket = document.getElementById('slider-ticket');
    const sDelay = document.getElementById('slider-delay');
    if (!sLeads || !sTicket || !sDelay) return;

    const update = () => {
        const leads = parseInt(sLeads.value, 10);
        const ticket = parseInt(sTicket.value, 10);
        const delay = parseInt(sDelay.value, 10);

        document.getElementById('val-leads').textContent = `${leads} prospectos`;
        document.getElementById('val-ticket').textContent = `$${ticket.toLocaleString('es-MX')} MXN`;
        document.getElementById('val-delay').textContent = delay === 1 ? '1 Hora' : `${delay} Horas`;

        const lostLeads = Math.round(leads * Math.min(0.42, 0.14 + delay * 0.025));
        const monthlyLeak = lostLeads * ticket;
        const yearlyLeak = monthlyLeak * 12;
        const recovered = Math.round(monthlyLeak * 0.75);

        document.getElementById('leak-monthly').textContent = `-$${monthlyLeak.toLocaleString('es-MX')} MXN / mes`;
        document.getElementById('leak-yearly').textContent = `$${yearlyLeak.toLocaleString('es-MX')} MXN al año`;
        document.getElementById('recovered-monthly').textContent = `+$${recovered.toLocaleString('es-MX')} MXN / mes`;
    };

    [sLeads, sTicket, sDelay].forEach(el => el.addEventListener('input', update));
    update();
}

/* ==========================================================================
   3. TERMINAL DE VALERIA (DIRECTORA COMERCIAL IA CON VOZ FEMENINA NATURAL)
   ========================================================================== */
let currentB2BLead = null;

function initViktorB2BForm() {
    const form = document.getElementById('automatic-b2b-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            nombre: document.getElementById('b2b-nombre').value.trim(),
            telefono: document.getElementById('b2b-telefono').value.trim(),
            email: 'directivo@empresa-mty.mx',
            sucursal: document.getElementById('b2b-empresa').value.trim(),
            tratamiento: 'Intervención B2B AUTOMATIC: ' + document.getElementById('b2b-dolor').value,
            fecha_cita: 'Diagnóstico Ejecutivo Prioritario',
            hora_cita: 'Inmediato',
            mensaje: document.getElementById('b2b-dolor').value,
            source: 'Agencia Oficial AUTOMATIC B2B Monterrey'
        };
        currentB2BLead = payload;

        try {
            await fetch('/webhook/clinica-coba-leads', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } catch (_) {}

        await launchValeriaCall(payload);
    });
}

window.simulateViktorDemo = function() {
    document.getElementById('b2b-nombre').value = 'Mauricio Elizondo';
    document.getElementById('b2b-empresa').value = 'Clínica Dental Cobá';
    document.getElementById('b2b-telefono').value = '+52 81 1848 3941';
    document.getElementById('b2b-dolor').selectedIndex = 0;
    document.getElementById('automatic-b2b-form').requestSubmit();
};

function playPhoneRingback() {
    return new Promise(resolve => {
        try {
            const AudioCtx = window.AudioContext || window.webkitAudioContext;
            if (!AudioCtx) {
                resolve();
                return;
            }
            if (!audioCtx) audioCtx = new AudioCtx();
            if (audioCtx.state === 'suspended') audioCtx.resume();

            const osc1 = audioCtx.createOscillator();
            const osc2 = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc1.frequency.setValueAtTime(440, audioCtx.currentTime);
            osc2.frequency.setValueAtTime(480, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.06, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.72);
            osc1.connect(gain);
            osc2.connect(gain);
            gain.connect(audioCtx.destination);
            osc1.start();
            osc2.start();
            osc1.stop(audioCtx.currentTime + 0.75);
            osc2.stop(audioCtx.currentTime + 0.75);
            setTimeout(resolve, 780);
        } catch (_) {
            resolve();
        }
    });
}

async function launchValeriaCall(lead) {
    stopCommercial();
    const status = document.getElementById('viktor-status');
    const log = document.getElementById('viktor-log');
    if (status) status.textContent = `📞 MARCANDO A ${lead.nombre.toUpperCase()}...`;
    if (log) log.innerHTML = '';

    await playPhoneRingback();

    const primerNombre = (lead.nombre || 'Hola').replace(/^(Dr\.|Dra\.|Lic\.|Ing\.)\s*/i, '').split(' ')[0];
    const opening = `¡Hola ${primerNombre}! ¿Qué tal, cómo estás?... Oye, te habla Valeria, Directora Comercial de Automatic aquí en Monterrey. Vi que acabas de registrar a ${lead.sucursal} en nuestra página porque ${lead.mensaje}. De hecho, ya estuvimos revisando su caso y les armamos un prototipo completo funcionando en vivo. Cuéntame rápido, ¿hoy como cuántos mensajes o llamadas reciben al día cuando lanzan alguna promoción?`;

    appendViktorLog('VALERIA (DIRECTORA IA AUTOMATIC)', opening, 'ai');
    speakValeriaFemale(opening);
}

window.viktorUserReply = function(text) {
    if (!currentB2BLead) {
        currentB2BLead = {
            nombre: 'Mauricio',
            sucursal: 'Clínica Dental Cobá'
        };
    }
    const primerNombre = (currentB2BLead.nombre || 'Mauricio').replace(/^(Dr\.|Dra\.|Lic\.|Ing\.)\s*/i, '').split(' ')[0];
    appendViktorLog(primerNombre, text, 'user');

    let reply = '';
    if (text.toLowerCase().includes('recepción') || text.toLowerCase().includes('mensajes')) {
        reply = `Uy sí, te entiendo perfecto ${primerNombre}, ahí es donde se enfría la mayoría de los clientes en Monterrey. Fíjate que con el sistema que ya les construimos para ${currentB2BLead.sucursal}, en cuanto el paciente pide informes, nuestra inteligencia artificial lo guarda en su base de datos y le marca en ocho segundos con mi voz para confirmarle su cita sin que tu recepción pierda nada de tiempo. ¿Te parece bien si lo conectamos a su WhatsApp oficial esta misma semana?`;
    } else {
        reply = `¡Me encanta la idea, ${primerNombre}! Ahorita mismo te acabo de mandar por WhatsApp el enlace directo a su prototipo y ya te agendé una sesión rápida de quince minutos para dejarlo conectado en tus dos sucursales. ¡Muchísimas gracias y nos vemos muy pronto!`;
    }

    setTimeout(() => {
        appendViktorLog('VALERIA (DIRECTORA IA AUTOMATIC)', reply, 'ai');
        speakValeriaFemale(reply);
    }, 280);
};

function appendViktorLog(sender, text, role) {
    const log = document.getElementById('viktor-log');
    if (!log) return;
    const div = document.createElement('div');
    div.className = `viktor-msg ${role}`;
    div.innerHTML = `<strong>[${sender}]:</strong> ${text}`;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}

async function speakValeriaFemale(text) {
    if (valeriaVoiceAudio) {
        valeriaVoiceAudio.pause();
        valeriaVoiceAudio = null;
    }
    const status = document.getElementById('viktor-status');
    if (status) status.textContent = '🔊 VALERIA ESTÁ HABLANDO CONTIGO (VOZ MUJER NEURAL HD)...';

    const voiceSelect = document.getElementById('b2b-voice-select')?.value || 'dalia';
    const url = `/api/tts?voice=${encodeURIComponent(voiceSelect)}&text=${encodeURIComponent(text)}`;

    try {
        const audio = new Audio(url);
        valeriaVoiceAudio = audio;
        audio.onended = () => {
            if (status) status.textContent = '🟢 VALERIA TE ESTÁ ESCUCHANDO (ELIGE UNA RESPUESTA ABAJO)...';
        };
        await audio.play();
    } catch (err) {
        console.error('Error reproduciendo voz de Valeria:', err);
    }
}
