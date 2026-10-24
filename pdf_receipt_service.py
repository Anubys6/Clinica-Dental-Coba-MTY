# -*- coding: utf-8 -*-
"""
pdf_receipt_service.py
Generador oficial de documentos PDF para la Clínica Dental Cobá Monterrey.
- Estado de Cuenta, Liquidación Quincenal & Rendimiento por Médico Especialista
- Recibo Oficial de Honorarios y Tratamiento Odontológico para Paciente
Cumplimiento NOM-004-SSA3 y estándares fiscales de servicios médicos en México.
"""

import os
import io
import json
import hashlib
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
import qrcode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTO_DIR = os.path.join(BASE_DIR, 'automation')
CRM_PATH = os.path.join(AUTO_DIR, 'crm_leads_coba.json')
DOCS_PATH = os.path.join(AUTO_DIR, 'doctors.json')
PAYROLL_STATUS_PATH = os.path.join(AUTO_DIR, 'payroll_status.json')
LOGO_PATH = os.path.join(BASE_DIR, 'images', 'logo.png')

import inventory_service

def load_payroll_status():
    if os.path.exists(PAYROLL_STATUS_PATH):
        try:
            with open(PAYROLL_STATUS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_payroll_status(status_dict):
    os.makedirs(AUTO_DIR, exist_ok=True)
    with open(PAYROLL_STATUS_PATH, 'w', encoding='utf-8') as f:
        json.dump(status_dict, f, indent=2, ensure_ascii=False)

def record_liquidation(doc_id, payment_method="Transferencia SPEI", notes=""):
    status_dict = load_payroll_status()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    folio = f"LIQ-COBA-{datetime.now().strftime('%Y%m')}-{doc_id.replace('doc-', '').zfill(3)}"
    
    status_dict[doc_id] = {
        "status": "LIQUIDADO",
        "liquidated_at": now_str,
        "payment_method": payment_method,
        "notes": notes,
        "folio": folio
    }
    save_payroll_status(status_dict)
    return status_dict[doc_id]

def get_liquidation_info(doc_id):
    status_dict = load_payroll_status()
    return status_dict.get(doc_id, {
        "status": "PENDIENTE",
        "liquidated_at": None,
        "payment_method": "Transferencia SPEI",
        "folio": f"LIQ-COBA-{datetime.now().strftime('%Y%m')}-{doc_id.replace('doc-', '').zfill(3)}"
    })

def make_qr_code(data_str, width=65, height=65):
    qr = qrcode.QRCode(version=1, box_size=3, border=1)
    qr.add_data(data_str)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0F172A", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return RLImage(buf, width=width, height=height)

def generate_doctor_payroll_pdf(doc_id_or_name, period="2ª Quincena Octubre 2026"):
    """
    Genera un PDF formal, ultra-detallado y corporativo de la Liquidación Quincenal
    y Rendimiento de Honorarios de un doctor específico en Clínica Dental Cobá.
    """
    inv_data = inventory_service.calculate_inventory_metrics()
    doc_balances = inv_data.get('doctor_balances', [])
    
    # Buscar doctor por ID o por nombre
    matched_doc = None
    for d in doc_balances:
        if d['id'] == doc_id_or_name or d['name'].lower() == doc_id_or_name.lower():
            matched_doc = d
            break
        if doc_id_or_name.lower() in d['name'].lower() or d['name'].lower() in doc_id_or_name.lower():
            matched_doc = d
            break
            
    if not matched_doc and doc_balances:
        matched_doc = doc_balances[0]

    d = matched_doc
    liq_info = get_liquidation_info(d['id'])
    folio = liq_info.get('folio', f"LIQ-COBA-2026-{d['id'].replace('doc-', '').zfill(3)}")
    status_text = liq_info.get('status', 'PENDIENTE')
    fecha_emision = datetime.now().strftime("%d de Octubre de 2026")
    
    # Configuración de estilos
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()
    
    c_primary = colors.HexColor('#0F172A')
    c_cyan = colors.HexColor('#06B6D4')
    c_slate = colors.HexColor('#475569')
    c_light = colors.HexColor('#F8FAFC')
    c_border = colors.HexColor('#E2E8F0')
    c_emerald = colors.HexColor('#059669')
    c_rose = colors.HexColor('#E11D48')

    title_main = ParagraphStyle(
        'DocTitleMain',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=c_primary
    )

    title_sub = ParagraphStyle(
        'DocTitleSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=c_slate
    )

    folio_style = ParagraphStyle(
        'FolioStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=c_cyan,
        alignment=2
    )

    badge_status = ParagraphStyle(
        'BadgeStatus',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10,
        textColor=colors.HexColor('#10B981') if status_text == 'LIQUIDADO' else colors.HexColor('#F59E0B'),
        alignment=2
    )

    body_regular = ParagraphStyle(
        'BodyRegular',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=c_primary
    )

    body_bold = ParagraphStyle(
        'BodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=c_primary
    )

    body_money = ParagraphStyle(
        'BodyMoney',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        alignment=2,
        textColor=c_primary
    )

    table_header_style = ParagraphStyle(
        'TableHeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=colors.white,
        alignment=0
    )

    table_header_money = ParagraphStyle(
        'TableHeaderMoney',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9,
        textColor=colors.white,
        alignment=2
    )

    elements = []

    # 1. ENCABEZADO CORPORATIVO DE LA CLÍNICA
    header_data = []
    logo_flowable = ""
    if os.path.exists(LOGO_PATH):
        try:
            logo_flowable = RLImage(LOGO_PATH, width=46, height=46)
        except Exception:
            logo_flowable = Paragraph("<b>COBÁ</b>", title_main)
    else:
        logo_flowable = Paragraph("<b>COBÁ</b>", title_main)

    clinic_info = [
        Paragraph("<b>CLÍNICA DENTAL COBÁ MONTERREY</b>", title_main),
        Paragraph("Odontología Digital Avanzada, Cirugía & Implantes Dentales • NOM-004-SSA3", title_sub),
        Paragraph("Av. Constitución 2050, Obispado / San Jerónimo • Tel: (81) 1848 3941 • contacto@coba.mx", title_sub),
        Paragraph("RFC: CDC-180415-MTY • Registro Sanitario SSA: 19-COBA-NL-00829", title_sub)
    ]

    doc_meta = [
        Paragraph(f"<b>FOLIO: {folio}</b>", folio_style),
        Paragraph(f"<b>ESTADO: ● {status_text}</b>", badge_status),
        Paragraph(f"Fecha Emisión: {fecha_emision}", ParagraphStyle('R1', parent=title_sub, alignment=2)),
        Paragraph(f"Periodo: <b>{period}</b>", ParagraphStyle('R2', parent=title_sub, alignment=2))
    ]

    top_table = Table(
        [[logo_flowable, clinic_info, doc_meta]],
        colWidths=[54, 320, 166]
    )
    top_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(top_table)
    elements.append(Spacer(1, 8))

    # Línea divisoria decorativa
    elements.append(HRFlowable(width="100%", thickness=2, color=c_cyan, spaceBefore=2, spaceAfter=8))

    # TÍTULO DEL DOCUMENTO
    doc_banner = Table(
        [[Paragraph("<b>ESTADO DE CUENTA, RENDIMIENTO CLÍNICO & LIQUIDACIÓN DE HONORARIOS MÉDICOS</b>", 
                    ParagraphStyle('Banner', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0F172A'), alignment=1))]],
        colWidths=[540]
    )
    doc_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E0F2FE')),
        ('BOX', (0,0), (-1,-1), 0.5, c_cyan),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(doc_banner)
    elements.append(Spacer(1, 8))

    # 2. FICHA DEL MÉDICO ESPECIALISTA
    doc_info_data = [
        [
            Paragraph("<b>MÉDICO ESPECIALISTA:</b>", body_regular),
            Paragraph(f"<b>{d['name']}</b>", body_bold),
            Paragraph("<b>CÉDULA PROFESIONAL:</b>", body_regular),
            Paragraph(f"{d.get('cedula', '8294711')} (DGP México)", body_bold)
        ],
        [
            Paragraph("<b>ESPECIALIDAD CLÍNICA:</b>", body_regular),
            Paragraph(f"{d['specialty']}", body_bold),
            Paragraph("<b>RÉGIMEN DE COMISIÓN:</b>", body_regular),
            Paragraph(f"<b>{d['comision_pct']}%</b> libre de lab/insumos", body_bold)
        ],
        [
            Paragraph("<b>SUCURSAL ASIGNADA:</b>", body_regular),
            Paragraph("Monterrey Centro / San Pedro", body_bold),
            Paragraph("<b>MÉTODO DE LIQUIDACIÓN:</b>", body_regular),
            Paragraph(f"{liq_info.get('payment_method', 'Transferencia Bancaria SPEI')}", body_bold)
        ]
    ]

    doc_info_table = Table(doc_info_data, colWidths=[120, 160, 130, 130])
    doc_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(doc_info_table)
    elements.append(Spacer(1, 8))

    # 3. RESUMEN FINANCIERO Y CÁLCULO DE LIQUIDACIÓN QUINCENAL
    gross = d.get('ingresos_brutos_mxn', 0.0)
    lab = d.get('costo_lab_mxn', 0.0)
    insumos = d.get('costo_insumos_mxn', 0.0)
    base_neta = max(0.0, gross - lab - insumos)
    doc_net_total = d.get('pago_neto_doctor_mxn', 0.0)
    doc_quincena = d.get('liquidacion_quincenal_mxn', round(doc_net_total / 4.0))
    clinic_profit = d.get('utilidad_neta_clinica_mxn', 0.0)
    citas_count = d.get('citas_total', 0)

    fin_summary_data = [
        [
            Paragraph("<b>CONCEPTO FINANCIERO AUDITADO</b>", table_header_style),
            Paragraph("<b>BASE DE CÁLCULO / FÓRMULA</b>", table_header_style),
            Paragraph("<b>SUBTOTAL (MXN)</b>", table_header_money),
            Paragraph("<b>IMPORTE FINAL (MXN)</b>", table_header_money)
        ],
        [
            Paragraph("Rendimiento Bruto Facturado", body_regular),
            Paragraph(f"{citas_count} consultas concluidas en el periodo", body_regular),
            Paragraph(f"${gross:,.2f}", body_money),
            Paragraph(f"${gross:,.2f}", body_money)
        ],
        [
            Paragraph("(-) Deducción Laboratorio CAD/CAM", body_regular),
            Paragraph("Prótesis, Zirconia, Modelos CAD/CAM y Guías Quirúrgicas", body_regular),
            Paragraph(f"-${lab:,.2f}", ParagraphStyle('M1', parent=body_money, textColor=c_rose)),
            Paragraph(f"-${lab:,.2f}", ParagraphStyle('M1', parent=body_money, textColor=c_rose))
        ],
        [
            Paragraph("(-) Deducción Insumos Clínicos Reales", body_regular),
            Paragraph("Bioseguridad, Anestesia, Ciclos Autoclave y Materiales", body_regular),
            Paragraph(f"-${insumos:,.2f}", ParagraphStyle('M2', parent=body_money, textColor=c_rose)),
            Paragraph(f"-${insumos:,.2f}", ParagraphStyle('M2', parent=body_money, textColor=c_rose))
        ],
        [
            Paragraph("<b>Base Neta Sujeta a Comisión</b>", body_bold),
            Paragraph("Ingreso Facturado - Lab - Insumos Médicos", body_regular),
            Paragraph(f"<b>${base_neta:,.2f}</b>", body_money),
            Paragraph(f"<b>${base_neta:,.2f}</b>", body_money)
        ],
        [
            Paragraph("<b>Tasa Pactada de Comisión del Especialista</b>", body_bold),
            Paragraph(f"Porcentaje contractual asignado a {d['specialty']}", body_regular),
            Paragraph(f"<b>{d['comision_pct']}%</b>", body_money),
            Paragraph(f"<b>${doc_net_total:,.2f}</b>", body_money)
        ],
        [
            Paragraph("<b>PAGO QUINCENAL A LIQUIDAR AL ESPECIALISTA</b>", ParagraphStyle('W1', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor('#065F46'))),
            Paragraph("<b>Liquidación 2ª Quincena (Base Neta × Comisión / 4)</b>", ParagraphStyle('W2', fontName='Helvetica-Bold', fontSize=8, textColor=colors.HexColor('#065F46'))),
            Paragraph(f"<b>${doc_quincena:,.2f}</b>", ParagraphStyle('W3', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#065F46'), alignment=2)),
            Paragraph(f"<b>${doc_quincena:,.2f} MXN</b>", ParagraphStyle('W4', fontName='Helvetica-Bold', fontSize=9.5, textColor=colors.HexColor('#065F46'), alignment=2))
        ],
        [
            Paragraph("Utilidad Neta Remanente Clínica Cobá", body_regular),
            Paragraph("Margen operativo final para reinversión e infraestructura", body_regular),
            Paragraph(f"${clinic_profit:,.2f}", ParagraphStyle('M4', parent=body_money, textColor=colors.HexColor('#0284C7'))),
            Paragraph(f"${clinic_profit:,.2f} MXN", ParagraphStyle('M5', parent=body_money, textColor=colors.HexColor('#0284C7')))
        ]
    ]

    fin_table = Table(fin_summary_data, colWidths=[150, 170, 110, 110])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('BACKGROUND', (0,1), (-1,1), colors.white),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor('#FFF1F2')),
        ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#FFF1F2')),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#F8FAFC')),
        ('BACKGROUND', (0,5), (-1,5), colors.white),
        ('BACKGROUND', (0,6), (-1,6), colors.HexColor('#D1FAE5')), # Highlight Liquidación
        ('BACKGROUND', (0,7), (-1,7), colors.HexColor('#F0F9FF')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(fin_table)
    elements.append(Spacer(1, 10))

    # 4. HISTORIAL METICULOSO DE CONSULTAS Y PACIENTES ATENDIDOS POR ESTE DOCTOR
    elements.append(Paragraph("<b>DESGLOSE DE PACIENTES ATENDIDOS Y COSTEO CLÍNICO EN EL PERIODO</b>", 
                              ParagraphStyle('SubT', fontName='Helvetica-Bold', fontSize=9, leading=11, textColor=c_primary)))
    elements.append(Spacer(1, 4))

    patients_history = d.get('patients_history', [])
    # Limit to top 14 if many to ensure clean document or show full list
    display_patients = patients_history[:12] if len(patients_history) > 14 else patients_history

    pt_rows = [
        [
            Paragraph("<b>#</b>", table_header_style),
            Paragraph("<b>FECHA</b>", table_header_style),
            Paragraph("<b>PACIENTE</b>", table_header_style),
            Paragraph("<b>TRATAMIENTO CLÍNICO</b>", table_header_style),
            Paragraph("<b>COBRO ($)</b>", table_header_money),
            Paragraph("<b>INSUMOS ($)</b>", table_header_money),
            Paragraph("<b>NETO DOC ($)</b>", table_header_money)
        ]
    ]

    for idx, p in enumerate(display_patients, 1):
        ticket = p.get('ticket_price_mxn', 0.0)
        ins = p.get('supplies_cost_mxn', 0.0)
        lab_p = p.get('lab_cost_mxn', 0.0)
        doc_com = max(0.0, (ticket - lab_p) * (d['comision_pct'] / 100.0))
        
        pt_rows.append([
            Paragraph(f"{idx}", body_regular),
            Paragraph(f"{p.get('appointment_date', '')[5:]}", body_regular),
            Paragraph(f"<b>{p.get('patient_name', 'Paciente')[:22]}</b>", body_regular),
            Paragraph(f"{p.get('treatment_name', 'Tratamiento')[:24]}", body_regular),
            Paragraph(f"${ticket:,.0f}", body_money),
            Paragraph(f"-${ins:,.0f}", ParagraphStyle('PIns', parent=body_money, textColor=c_rose)),
            Paragraph(f"<b>${doc_com:,.0f}</b>", ParagraphStyle('PDoc', parent=body_money, textColor=c_emerald))
        ])

    if len(patients_history) > len(display_patients):
        remaining = len(patients_history) - len(display_patients)
        pt_rows.append([
            Paragraph("...", body_regular),
            Paragraph("...", body_regular),
            Paragraph(f"<b>(+ {remaining} consultas adicionales en sistema Cobá)</b>", body_regular),
            Paragraph("Auditoría en base de datos CRM", body_regular),
            Paragraph("...", body_money),
            Paragraph("...", body_money),
            Paragraph("...", body_money)
        ])

    pt_table = Table(pt_rows, colWidths=[18, 52, 130, 140, 65, 65, 70])
    pt_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_slate),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(pt_table)
    elements.append(Spacer(1, 10))

    # 5. BLOQUE DE SEGURIDAD, QR & FIRMAS OFICIALES
    qr_data = f"CLINICA-COBA-LIQ|DOC={d['name']}|PERIODO={period}|NETO={doc_quincena}|FOLIO={folio}|AUTENTICADO-SSA-NOM004"
    qr_img = make_qr_code(qr_data, width=54, height=54)

    # Hash criptográfico para simular sello digital fiscal/médico
    seal_hash = hashlib.sha256(qr_data.encode('utf-8')).hexdigest()[:48]
    seal_text = f"SELLO DIGITAL COBÁ: {seal_hash[:24]}...{seal_hash[-12:]}"

    sig_data = [
        [
            qr_img,
            [
                Paragraph("<b>CERTIFICACIÓN & DISPERSIÓN DE FONDOS:</b>", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=7.5, textColor=c_primary)),
                Paragraph(seal_text, ParagraphStyle('H2', fontName='Helvetica', fontSize=6.5, textColor=c_slate)),
                Paragraph("Dispersión autorizada conforme al Contrato de Prestación de Servicios Odontológicos y la NOM-004-SSA3.", ParagraphStyle('H3', fontName='Helvetica', fontSize=6.5, textColor=c_slate))
            ],
            [
                Spacer(1, 24),
                HRFlowable(width="90%", thickness=1, color=c_primary, spaceBefore=0, spaceAfter=2),
                Paragraph("<b>DR. MAURICIO COBÁ</b>", ParagraphStyle('F1', fontName='Helvetica-Bold', fontSize=7.5, alignment=1)),
                Paragraph("Director Médico y Administrativo", ParagraphStyle('F2', fontName='Helvetica', fontSize=6.5, alignment=1, textColor=c_slate))
            ],
            [
                Spacer(1, 24),
                HRFlowable(width="90%", thickness=1, color=c_primary, spaceBefore=0, spaceAfter=2),
                Paragraph(f"<b>{d['name'].upper()}</b>", ParagraphStyle('F3', fontName='Helvetica-Bold', fontSize=7.5, alignment=1)),
                Paragraph("Firma de Conformidad del Médico", ParagraphStyle('F4', fontName='Helvetica', fontSize=6.5, alignment=1, textColor=c_slate))
            ]
        ]
    ]

    sig_table = Table(sig_data, colWidths=[60, 200, 140, 140])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 2),
        ('RIGHTPADDING', (0,0), (-1,-1), 2),
    ]))

    footer_legal = Paragraph(
        "Documento confidencial emitido por Clínica Dental Cobá S.A. de C.V. • Obispado / San Jerónimo, Monterrey, N.L. • Válido como comprobante administrativo y fiscal de liquidación quincenal.",
        ParagraphStyle('Foot', fontName='Helvetica', fontSize=6.5, leading=8, textColor=c_slate, alignment=1)
    )

    elements.append(KeepTogether([sig_table, Spacer(1, 6), footer_legal]))

    doc.build(elements)
    buf.seek(0)
    return buf.getvalue()


def generate_patient_receipt_pdf(appointment_id):
    """
    Genera un Comprobante Oficial de Pago / Recibo Dental para el paciente
    con desglose de tratamiento, doctor tratante, fecha, IVA exento y código QR.
    """
    appts = []
    if os.path.exists(CRM_PATH):
        try:
            with open(CRM_PATH, 'r', encoding='utf-8') as f:
                appts = json.load(f)
        except Exception:
            pass

    appt = None
    for a in appts:
        if str(a.get('id', '')) == str(appointment_id):
            appt = a
            break
            
    if not appt and appts:
        appt = appts[0]

    if not appt:
        appt = {
            'id': appointment_id,
            'nombre': 'Fernanda Salinas Elizondo',
            'telefono': '+52 81 1928 3491',
            'email': 'fernanda.salinas@gmail.com',
            'tratamiento': 'Corona Monolítica de Zirconia Prettau CAD/CAM',
            'fecha_cita': '2026-10-24',
            'hora_cita': '11:00 AM',
            'doctor_asignado': 'Dr. Mauricio Cobá',
            'sucursal': 'Monterrey Centro (Obispado)'
        }

    val = inventory_service.get_treatment_val(appt.get('tratamiento', ''))
    folio = f"REC-COBA-{datetime.now().strftime('%Y%m')}-{str(appt.get('id', '1')).replace('coba-', '').zfill(4)}"
    fecha_emision = datetime.now().strftime("%d de Octubre de 2026")

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    c_primary = colors.HexColor('#0F172A')
    c_cyan = colors.HexColor('#06B6D4')
    c_slate = colors.HexColor('#475569')
    c_light = colors.HexColor('#F8FAFC')
    c_border = colors.HexColor('#E2E8F0')

    title_main = ParagraphStyle('RTitleMain', fontName='Helvetica-Bold', fontSize=15, leading=18, textColor=c_primary)
    title_sub = ParagraphStyle('RTitleSub', fontName='Helvetica', fontSize=8.5, leading=11, textColor=c_slate)

    elements = []

    # Encabezado
    logo_flowable = ""
    if os.path.exists(LOGO_PATH):
        try:
            logo_flowable = RLImage(LOGO_PATH, width=46, height=46)
        except Exception:
            logo_flowable = Paragraph("<b>COBÁ</b>", title_main)
    else:
        logo_flowable = Paragraph("<b>COBÁ</b>", title_main)

    clinic_info = [
        Paragraph("<b>CLÍNICA DENTAL COBÁ MONTERREY</b>", title_main),
        Paragraph("Odontología Digital Avanzada, Cirugía & Implantes Dentales • NOM-004-SSA3", title_sub),
        Paragraph("Av. Constitución 2050, Obispado / San Jerónimo • Tel: (81) 1848 3941 • contacto@coba.mx", title_sub),
        Paragraph("RFC: CDC-180415-MTY • Registro Sanitario SSA: 19-COBA-NL-00829", title_sub)
    ]

    rec_meta = [
        Paragraph(f"<b>FOLIO: {folio}</b>", ParagraphStyle('RFol', fontName='Helvetica-Bold', fontSize=9, textColor=c_cyan, alignment=2)),
        Paragraph("<b>ESTADO: ● PAGADO / COBRADO</b>", ParagraphStyle('RSt', fontName='Helvetica-Bold', fontSize=8.5, textColor=colors.HexColor('#10B981'), alignment=2)),
        Paragraph(f"Fecha: {fecha_emision}", ParagraphStyle('RDt', fontName='Helvetica', fontSize=8.5, textColor=c_slate, alignment=2)),
        Paragraph(f"Sucursal: <b>{appt.get('sucursal', 'Monterrey Centro')}</b>", ParagraphStyle('RSc', fontName='Helvetica', fontSize=8.5, textColor=c_slate, alignment=2))
    ]

    top_table = Table([[logo_flowable, clinic_info, rec_meta]], colWidths=[54, 320, 166])
    top_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(top_table)
    elements.append(Spacer(1, 10))

    elements.append(HRFlowable(width="100%", thickness=2, color=c_cyan, spaceBefore=0, spaceAfter=10))

    doc_banner = Table(
        [[Paragraph("<b>COMPROBANTE OFICIAL DE HONORARIOS & TRATAMIENTO ODONTOLÓGICO</b>", 
                    ParagraphStyle('Banner2', fontName='Helvetica-Bold', fontSize=10.5, textColor=c_primary, alignment=1))]],
        colWidths=[540]
    )
    doc_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#E0F2FE')),
        ('BOX', (0,0), (-1,-1), 0.5, c_cyan),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(doc_banner)
    elements.append(Spacer(1, 12))

    # Datos del paciente y médico
    client_box = [
        [
            Paragraph("<b>PACIENTE:</b>", ParagraphStyle('B1', fontName='Helvetica', fontSize=8.5)),
            Paragraph(f"<b>{appt.get('nombre', 'Paciente')}</b>", ParagraphStyle('B2', fontName='Helvetica-Bold', fontSize=9)),
            Paragraph("<b>DOCTOR TRATANTE:</b>", ParagraphStyle('B3', fontName='Helvetica', fontSize=8.5)),
            Paragraph(f"<b>{appt.get('doctor_asignado', 'Dr. Mauricio Cobá')}</b>", ParagraphStyle('B4', fontName='Helvetica-Bold', fontSize=9))
        ],
        [
            Paragraph("<b>TELÉFONO:</b>", ParagraphStyle('B5', fontName='Helvetica', fontSize=8.5)),
            Paragraph(f"{appt.get('telefono', '+52 81 0000 0000')}", ParagraphStyle('B6', fontName='Helvetica', fontSize=8.5)),
            Paragraph("<b>FECHA ATENCIÓN:</b>", ParagraphStyle('B7', fontName='Helvetica', fontSize=8.5)),
            Paragraph(f"{appt.get('fecha_cita', '')} a las {appt.get('hora_cita', '10:00 AM')}", ParagraphStyle('B8', fontName='Helvetica', fontSize=8.5))
        ],
        [
            Paragraph("<b>CORREO:</b>", ParagraphStyle('B9', fontName='Helvetica', fontSize=8.5)),
            Paragraph(f"{appt.get('email', 'paciente@gmail.com')}", ParagraphStyle('B10', fontName='Helvetica', fontSize=8.5)),
            Paragraph("<b>MÉTODO DE PAGO:</b>", ParagraphStyle('B11', fontName='Helvetica', fontSize=8.5)),
            Paragraph("Tarjeta de Crédito / Terminal Cobá", ParagraphStyle('B12', fontName='Helvetica-Bold', fontSize=8.5))
        ]
    ]

    client_table = Table(client_box, colWidths=[100, 170, 120, 150])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(client_table)
    elements.append(Spacer(1, 14))

    # Desglose de servicios odontológicos
    items_table_data = [
        [
            Paragraph("<b>CANT.</b>", ParagraphStyle('TH1', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
            Paragraph("<b>DESCRIPCIÓN DEL PROCEDIMIENTO ODONTOLÓGICO</b>", ParagraphStyle('TH2', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white)),
            Paragraph("<b>PRECIO UNITARIO</b>", ParagraphStyle('TH3', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=2)),
            Paragraph("<b>TOTAL (MXN)</b>", ParagraphStyle('TH4', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, alignment=2))
        ],
        [
            Paragraph("1", ParagraphStyle('TD1', fontName='Helvetica', fontSize=8.5)),
            Paragraph(f"<b>{appt.get('tratamiento', 'Procedimiento Clínico Dental')}</b><br/><font color='#64748B' size='7.5'>Incluye valoración digital 3D, asepsia hospitalaria y garantía de calidad Cobá Monterrey.</font>", ParagraphStyle('TD2', fontName='Helvetica', fontSize=8.5, leading=11)),
            Paragraph(f"${val:,.2f}", ParagraphStyle('TD3', fontName='Helvetica', fontSize=8.5, alignment=2)),
            Paragraph(f"${val:,.2f}", ParagraphStyle('TD4', fontName='Helvetica-Bold', fontSize=8.5, alignment=2))
        ],
        [
            Paragraph("", ParagraphStyle('E1', fontName='Helvetica')),
            Paragraph("<b>SUBTOTAL:</b>", ParagraphStyle('S1', fontName='Helvetica-Bold', fontSize=8.5, alignment=2)),
            Paragraph(f"${val:,.2f}", ParagraphStyle('S2', fontName='Helvetica-Bold', fontSize=8.5, alignment=2)),
            Paragraph(f"${val:,.2f} MXN", ParagraphStyle('S3', fontName='Helvetica-Bold', fontSize=8.5, alignment=2))
        ],
        [
            Paragraph("", ParagraphStyle('E2', fontName='Helvetica')),
            Paragraph("<b>I.V.A. (0% EXENTO MÉDICO):</b><br/><font size='6.5' color='#64748B'>Exento según Art. 15 Fracc. XIV de la Ley del IVA</font>", ParagraphStyle('I1', fontName='Helvetica', fontSize=8, alignment=2, leading=9)),
            Paragraph("$0.00", ParagraphStyle('I2', fontName='Helvetica', fontSize=8.5, alignment=2)),
            Paragraph("$0.00 MXN", ParagraphStyle('I3', fontName='Helvetica', fontSize=8.5, alignment=2))
        ],
        [
            Paragraph("", ParagraphStyle('E3', fontName='Helvetica')),
            Paragraph("<b>TOTAL PAGADO:</b>", ParagraphStyle('T1', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#065F46'), alignment=2)),
            Paragraph(f"<b>${val:,.2f}</b>", ParagraphStyle('T2', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#065F46'), alignment=2)),
            Paragraph(f"<b>${val:,.2f} MXN</b>", ParagraphStyle('T3', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#065F46'), alignment=2))
        ]
    ]

    items_table = Table(items_table_data, colWidths=[35, 295, 105, 105])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 0.5, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('BACKGROUND', (0,1), (-1,1), colors.white),
        ('BACKGROUND', (0,2), (-1,2), c_light),
        ('BACKGROUND', (0,3), (-1,3), colors.white),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor('#D1FAE5')), # Highlight total
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 16))

    # QR y firmas
    qr_data = f"CLINICA-COBA-RECIBO|FOLIO={folio}|PACIENTE={appt.get('nombre')}|TOTAL={val}|SSA-NOM004"
    qr_img = make_qr_code(qr_data, width=54, height=54)

    seal_hash = hashlib.sha256(qr_data.encode('utf-8')).hexdigest()[:44]
    seal_text = f"SELLO DIGITAL COBÁ: {seal_hash[:22]}...{seal_hash[-12:]}"

    sig_data = [
        [
            qr_img,
            [
                Paragraph("<b>AUTENTICACIÓN FISCAL & SANITARIA:</b>", ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=8, textColor=c_primary)),
                Paragraph(seal_text, ParagraphStyle('H2', fontName='Helvetica', fontSize=6.5, textColor=c_slate)),
                Paragraph("Este comprobante certifica la recepción íntegra del pago por servicios odontológicos.", ParagraphStyle('H3', fontName='Helvetica', fontSize=6.5, textColor=c_slate))
            ],
            [
                Spacer(1, 28),
                HRFlowable(width="90%", thickness=1, color=c_primary, spaceBefore=0, spaceAfter=2),
                Paragraph(f"<b>{appt.get('doctor_asignado', 'Dr. Mauricio Cobá').upper()}</b>", ParagraphStyle('F1', fontName='Helvetica-Bold', fontSize=8, alignment=1)),
                Paragraph("Médico Especialista Tratante", ParagraphStyle('F2', fontName='Helvetica', fontSize=7, alignment=1, textColor=c_slate))
            ]
        ]
    ]

    sig_table = Table(sig_data, colWidths=[60, 280, 200])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(sig_table)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        "Agradecemos tu preferencia en Clínica Dental Cobá Monterrey. Para dudas, facturación CFDI o citas de seguimiento, comunícate al 81 1848 3941.",
        ParagraphStyle('Foot2', fontName='Helvetica', fontSize=7, leading=9, textColor=c_slate, alignment=1)
    ))

    doc.build(elements)
    buf.seek(0)
    return buf.getvalue()
