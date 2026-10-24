import os

css_path = r'C:\Users\SAmue\.gemini\antigravity\scratch\clinica-dental-coba-mty\styles.css'

wa_css = """

/* ==========================================================================
   SIMULADOR DE WHATSAPP INTERACTIVO Y MENÚ AUTOMATIZADO FAST-TRACK
   ========================================================================== */
.wa-interactive-simulator {
    margin-top: 18px;
    border-radius: 18px;
    background: #0B141A;
    border: 1px solid rgba(37, 211, 102, 0.35);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 25px rgba(37, 211, 102, 0.15);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.wa-sim-header {
    background: #1F2C34;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.wa-sim-user {
    display: flex;
    align-items: center;
    gap: 12px;
}

.wa-sim-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 0 12px rgba(37, 211, 102, 0.5);
}

.wa-sim-app-badge {
    background: rgba(37, 211, 102, 0.18);
    border: 1px solid rgba(37, 211, 102, 0.5);
    color: #25D366;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 20px;
    text-decoration: none;
    transition: all 0.2s ease;
}

.wa-sim-app-badge:hover {
    background: #25D366;
    color: #000;
    transform: translateY(-1px);
}

.wa-sim-chat {
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    background-color: #0B141A;
    background-image: radial-gradient(rgba(37, 211, 102, 0.04) 1px, transparent 1px);
    background-size: 16px 16px;
    max-height: 420px;
    overflow-y: auto;
}

.wa-msg {
    display: flex;
    width: 100%;
}

.wa-msg-bot {
    justify-content: flex-start;
}

.wa-msg-patient {
    justify-content: flex-end;
}

.wa-msg-bubble {
    max-width: 90%;
    padding: 11px 15px;
    border-radius: 14px;
    font-size: 0.86rem;
    line-height: 1.48;
    position: relative;
    box-shadow: 0 3px 8px rgba(0,0,0,0.35);
}

.wa-msg-bot .wa-msg-bubble {
    background: #202C33;
    color: #E9EDEF;
    border-top-left-radius: 3px;
    border: 1px solid rgba(255,255,255,0.07);
}

.wa-msg-patient .wa-msg-bubble {
    background: #005C4B;
    color: #E9EDEF;
    border-top-right-radius: 3px;
    border: 1px solid rgba(37, 211, 102, 0.3);
}

.wa-msg-time {
    display: block;
    font-size: 0.68rem;
    color: #8696A0;
    text-align: right;
    margin-top: 5px;
}

.wa-menu-options {
    display: flex;
    flex-direction: column;
    gap: 7px;
    margin-top: 10px;
}

.wa-menu-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(37, 211, 102, 0.3);
    border-radius: 10px;
    color: #F3F4F6;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s ease;
    width: 100%;
    font-family: inherit;
}

.wa-menu-btn:hover {
    background: rgba(37, 211, 102, 0.2);
    border-color: #25D366;
    transform: translateX(3px);
}

.wa-btn-num {
    font-size: 1.15rem;
    flex-shrink: 0;
}

.wa-btn-txt {
    display: flex;
    flex-direction: column;
}

.wa-btn-txt strong {
    font-size: 0.84rem;
    color: #FFFFFF;
}

.wa-btn-txt small {
    font-size: 0.72rem;
    color: #9CA3AF;
}

.wa-sim-footer {
    background: #1F2C34;
    padding: 14px 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.btn-whatsapp-full {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    padding: 13px 20px;
    background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
    color: #FFFFFF;
    font-weight: 800;
    font-size: 0.98rem;
    border-radius: 12px;
    text-decoration: none;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4);
    transition: all 0.25s ease;
}

.btn-whatsapp-full:hover {
    background: linear-gradient(135deg, #20BA5A 0%, #0F7569 100%);
    box-shadow: 0 6px 22px rgba(37, 211, 102, 0.65);
    transform: translateY(-2px);
    color: #FFFFFF;
}
"""

with open(css_path, 'a', encoding='utf-8') as f:
    f.write(wa_css)

print('SUCCESS: Appended wa_css to styles.css')
