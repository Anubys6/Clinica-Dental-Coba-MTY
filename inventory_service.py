# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTO_DIR = os.path.join(BASE_DIR, 'automation')
INV_PATH = os.path.join(AUTO_DIR, 'inventory_supplies.json')
CRM_PATH = os.path.join(AUTO_DIR, 'crm_leads_coba.json')
DOCS_PATH = os.path.join(AUTO_DIR, 'doctors.json')

# 55 Ultra-detailed dental supplies used in Mexican dental clinics
DETAILED_SUPPLIES_CATALOG = [
    # 1. Bioseguridad, Esterilización & Descartables Básicos
    {
        'id': 'ins-01',
        'name': 'Ciclo Esterilización Autoclave (Bolsa Grado Médico c/Testigo Químico Clase 4 + Desgaste)',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Ciclo / Instrumental',
        'cost_unit': 18.50,
        'stock_current': 420,
        'stock_min': 90,
        'supplier': 'Bioseguridad Dental MTY'
    },
    {
        'id': 'ins-02',
        'name': 'Gasa Quirúrgica Estéril 5x5 cm 100% Algodón (Sobre con 5 gasas)',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Sobre 5 pzas',
        'cost_unit': 7.50,
        'stock_current': 510,
        'stock_min': 120,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-03',
        'name': 'Gasa Quirúrgica Estéril 10x10 cm No Tejida (Sobre con 2 gasas)',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Sobre 2 pzas',
        'cost_unit': 9.00,
        'stock_current': 260,
        'stock_min': 60,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-04',
        'name': 'Rollos de Algodón Odontológico Absorbente #2 (Paquete uso 6 rollos)',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Paquete 6 rollos',
        'cost_unit': 3.80,
        'stock_current': 650,
        'stock_min': 150,
        'supplier': 'Dentarix MTY'
    },
    {
        'id': 'ins-05',
        'name': 'Babero Impermeable Plastificado Grado Médico',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Pieza',
        'cost_unit': 3.50,
        'stock_current': 580,
        'stock_min': 140,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-06',
        'name': 'Eyector de Saliva Desechable con Alambre Flexible y Punta Suave',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Pieza',
        'cost_unit': 4.00,
        'stock_current': 550,
        'stock_min': 130,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-07',
        'name': 'Vaso Plástico Descartable 5oz para Enjuague Antiséptico',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Pieza',
        'cost_unit': 1.50,
        'stock_current': 850,
        'stock_min': 200,
        'supplier': 'Depósito Dental Monterrey'
    },
    {
        'id': 'ins-08',
        'name': 'Película de Barrera Plástica Descartable para Cabezal, Mangas y Lámpara (Set 4 pzas)',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Set 4 pzas',
        'cost_unit': 6.00,
        'stock_current': 420,
        'stock_min': 100,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-09',
        'name': 'Guantes de Examen Nitrilo Sin Polvo Micro-Touch (Par)',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Par',
        'cost_unit': 5.50,
        'stock_current': 750,
        'stock_min': 160,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-10',
        'name': 'Guantes Quirúrgicos Estériles de Nitrilo Grado Cirugía (Par)',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Par',
        'cost_unit': 18.00,
        'stock_current': 190,
        'stock_min': 45,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-11',
        'name': 'Mascarilla KN95 Médica Termosellada',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Pieza',
        'cost_unit': 7.00,
        'stock_current': 350,
        'stock_min': 80,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-12',
        'name': 'Cofia Plisada Descartable / Gorro Quirúrgico',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Pieza',
        'cost_unit': 2.50,
        'stock_current': 480,
        'stock_min': 100,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-13',
        'name': 'Campo Quirúrgico Estéril Fenestrado Impermeable',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Pieza',
        'cost_unit': 32.00,
        'stock_current': 125,
        'stock_min': 35,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-14',
        'name': 'Cubrebandeja de Papel Grado Médico Descartable',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Pieza',
        'cost_unit': 2.20,
        'stock_current': 680,
        'stock_min': 150,
        'supplier': 'Depósito Dental Monterrey'
    },
    {
        'id': 'ins-15',
        'name': 'Microbrush Descartable Aplicador Punta Fina (Par)',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Par',
        'cost_unit': 3.00,
        'stock_current': 400,
        'stock_min': 90,
        'supplier': 'Dentarix MTY'
    },
    {
        'id': 'ins-16',
        'name': 'Desinfección de Superficies Virucida Sanilup / CaviWipes (Dosis aplicación)',
        'category': 'Bioseguridad & Esterilización',
        'unit': 'Dosis por Sillón',
        'cost_unit': 6.50,
        'stock_current': 240,
        'stock_min': 50,
        'supplier': 'Bioseguridad Dental MTY'
    },

    # 2. Anestesia, Ampolletas & Agujas
    {
        'id': 'ins-17',
        'name': 'Ampolleta / Cartucho Articaína 4% con Epinefrina 1:100,000 (Septanest Septodont)',
        'category': 'Anestesia & Agujas',
        'unit': 'Cartucho 1.8ml',
        'cost_unit': 38.00,
        'stock_current': 220,
        'stock_min': 50,
        'supplier': 'Depósito Dental Monterrey'
    },
    {
        'id': 'ins-18',
        'name': 'Ampolleta / Cartucho Mepivacaína al 3% sin Vasoconstrictor (Scandonest)',
        'category': 'Anestesia & Agujas',
        'unit': 'Cartucho 1.8ml',
        'cost_unit': 34.00,
        'stock_current': 105,
        'stock_min': 30,
        'supplier': 'Depósito Dental Monterrey'
    },
    {
        'id': 'ins-19',
        'name': 'Ampolleta / Cartucho Lidocaína 2% con Epinefrina 1:100,000 (Zeyco)',
        'category': 'Anestesia & Agujas',
        'unit': 'Cartucho 1.8ml',
        'cost_unit': 26.00,
        'stock_current': 145,
        'stock_min': 40,
        'supplier': 'Depósito Dental Monterrey'
    },
    {
        'id': 'ins-20',
        'name': 'Aguja Dental Descartable Corta 30G (Terumo/BD)',
        'category': 'Anestesia & Agujas',
        'unit': 'Pieza',
        'cost_unit': 4.50,
        'stock_current': 480,
        'stock_min': 100,
        'supplier': 'Dentarix MTY'
    },
    {
        'id': 'ins-21',
        'name': 'Aguja Dental Descartable Larga 27G (Terumo/BD)',
        'category': 'Anestesia & Agujas',
        'unit': 'Pieza',
        'cost_unit': 4.80,
        'stock_current': 230,
        'stock_min': 60,
        'supplier': 'Dentarix MTY'
    },
    {
        'id': 'ins-22',
        'name': 'Gel Anestésico Tópico Benzocaína 20% Denta-Care Sabor Cereza/Menta',
        'category': 'Anestesia & Agujas',
        'unit': 'Dosis Aplicación',
        'cost_unit': 12.00,
        'stock_current': 85,
        'stock_min': 25,
        'supplier': 'Dentarix MTY'
    },

    # 3. Implantología, Periodoncia & Cirugía Oral
    {
        'id': 'ins-23',
        'name': 'Implante Dental Titanio Grado 4 Neodent Helix GM (Straumann Group)',
        'category': 'Implantología & Cirugía',
        'unit': 'Pieza Implante',
        'cost_unit': 2850.00,
        'stock_current': 18,
        'stock_min': 8,
        'supplier': 'Straumann México MTY'
    },
    {
        'id': 'ins-24',
        'name': 'Tornillo de Cierre & Pilar de Cicatrización Titanio Neodent GM',
        'category': 'Implantología & Cirugía',
        'unit': 'Pieza',
        'cost_unit': 420.00,
        'stock_current': 26,
        'stock_min': 8,
        'supplier': 'Straumann México MTY'
    },
    {
        'id': 'ins-25',
        'name': 'Bulto Quirúrgico Estéril Completo Implantología (Batas, Campos, Cubiertas Motor)',
        'category': 'Implantología & Cirugía',
        'unit': 'Paquete',
        'cost_unit': 140.00,
        'stock_current': 24,
        'stock_min': 8,
        'supplier': 'Médica Regiomontana'
    },
    {
        'id': 'ins-26',
        'name': 'Hoja de Bisturí Quirúrgica #15 Acero Inoxidable (Swann-Morton)',
        'category': 'Implantología & Cirugía',
        'unit': 'Pieza',
        'cost_unit': 11.00,
        'stock_current': 115,
        'stock_min': 30,
        'supplier': 'Farmacia Quirúrgica MTY'
    },
    {
        'id': 'ins-27',
        'name': 'Sutura Reabsorbible Vicryl 4-0 con Aguja Atraumática (Ethicon)',
        'category': 'Implantología & Cirugía',
        'unit': 'Sobre',
        'cost_unit': 88.00,
        'stock_current': 68,
        'stock_min': 20,
        'supplier': 'Farmacia Quirúrgica MTY'
    },
    {
        'id': 'ins-28',
        'name': 'Sutura Seda Negra 3-0 Cortante (Atramat)',
        'category': 'Implantología & Cirugía',
        'unit': 'Sobre',
        'cost_unit': 42.00,
        'stock_current': 78,
        'stock_min': 25,
        'supplier': 'Farmacia Quirúrgica MTY'
    },
    {
        'id': 'ins-29',
        'name': 'Esponja Quirúrgica Hemostática Absorbible (Gelfoam)',
        'category': 'Implantología & Cirugía',
        'unit': 'Sobre',
        'cost_unit': 48.00,
        'stock_current': 52,
        'stock_min': 15,
        'supplier': 'Farmacia Quirúrgica MTY'
    },
    {
        'id': 'ins-30',
        'name': 'Fresa Quirúrgica Zekrya Carburo de Tungsteno (Dentsply)',
        'category': 'Implantología & Cirugía',
        'unit': 'Desgaste Uso',
        'cost_unit': 85.00,
        'stock_current': 42,
        'stock_min': 12,
        'supplier': 'Depósito Dental Monterrey'
    },
    {
        'id': 'ins-31',
        'name': 'Solución Fisiológica Estéril 250ml para Irrigación de Fisiocirugía',
        'category': 'Implantología & Cirugía',
        'unit': 'Frasco',
        'cost_unit': 35.00,
        'stock_current': 58,
        'stock_min': 15,
        'supplier': 'Farmacia Quirúrgica MTY'
    },
    {
        'id': 'ins-32',
        'name': 'Cánula de Aspiración Quirúrgica Alta Potencia Desechable',
        'category': 'Implantología & Cirugía',
        'unit': 'Pieza',
        'cost_unit': 8.00,
        'stock_current': 140,
        'stock_min': 30,
        'supplier': 'Dentarix MTY'
    },

    # 4. Endodoncia Microscópica
    {
        'id': 'ins-33',
        'name': 'Limas Rotatorias NiTi WaveOne Gold Primary 25mm (Dentsply)',
        'category': 'Endodoncia',
        'unit': 'Lima Uso',
        'cost_unit': 185.00,
        'stock_current': 46,
        'stock_min': 15,
        'supplier': 'Dentsply Sirona México'
    },
    {
        'id': 'ins-34',
        'name': 'Dique de Goma Sanctuary + Arco de Young + Clamp/Grapa (Aislamiento Absoluto)',
        'category': 'Endodoncia',
        'unit': 'Juego Sesión',
        'cost_unit': 38.00,
        'stock_current': 95,
        'stock_min': 25,
        'supplier': 'Depósito Dental Monterrey'
    },
    {
        'id': 'ins-35',
        'name': 'Cemento Biocerámico Sellador Radicular AH Plus Bioceramic Sealer',
        'category': 'Endodoncia',
        'unit': 'Dosis Tratamiento',
        'cost_unit': 115.00,
        'stock_current': 36,
        'stock_min': 10,
        'supplier': 'Dentsply Sirona México'
    },
    {
        'id': 'ins-36',
        'name': 'Gutapercha Conicidad WaveOne + Puntas de Papel Estériles',
        'category': 'Endodoncia',
        'unit': 'Juego Obturación',
        'cost_unit': 45.00,
        'stock_current': 120,
        'stock_min': 30,
        'supplier': 'Dentsply Sirona México'
    },
    {
        'id': 'ins-37',
        'name': 'Irrigantes Endodónticos (NaOCl 5.25% + EDTA 17% + Cánulas Endo-Eze)',
        'category': 'Endodoncia',
        'unit': 'Tratamiento',
        'cost_unit': 38.00,
        'stock_current': 72,
        'stock_min': 20,
        'supplier': 'Dentarix MTY'
    },

    # 5. Ortodoncia & Alineadores
    {
        'id': 'ins-38',
        'name': 'Arco Ortodóntico Cu-NiTi Termoactivo Superelástico (Ormco)',
        'category': 'Ortodoncia',
        'unit': 'Juego Arcos',
        'cost_unit': 160.00,
        'stock_current': 140,
        'stock_min': 40,
        'supplier': 'Ormco México'
    },
    {
        'id': 'ins-39',
        'name': 'Resina para Cementado de Brackets Transbond XT (3M Unitek)',
        'category': 'Ortodoncia',
        'unit': 'Aplicación Dosis',
        'cost_unit': 95.00,
        'stock_current': 48,
        'stock_min': 15,
        'supplier': '3M Oral Care México'
    },
    {
        'id': 'ins-40',
        'name': 'Tubos Molares + Módulos Elastoméricos & Cadenas Alastik',
        'category': 'Ortodoncia',
        'unit': 'Juego Paciente',
        'cost_unit': 65.00,
        'stock_current': 210,
        'stock_min': 50,
        'supplier': 'Ormco México'
    },
    {
        'id': 'ins-41',
        'name': 'Kit de Ataches de Resina Microhíbrida para Alineadores Invisibles',
        'category': 'Ortodoncia',
        'unit': 'Juego Caso',
        'cost_unit': 190.00,
        'stock_current': 32,
        'stock_min': 10,
        'supplier': '3M Oral Care México'
    },

    # 6. Prótesis, Operatoria & Estética
    {
        'id': 'ins-42',
        'name': 'Resina Nanohíbrida Fotocurable Filtek Z350 XT (3M ESPE)',
        'category': 'Operatoria & Estética',
        'unit': 'Dosis Restauración',
        'cost_unit': 95.00,
        'stock_current': 64,
        'stock_min': 20,
        'supplier': '3M Oral Care México'
    },
    {
        'id': 'ins-43',
        'name': 'Ácido Fosfórico al 37% + Adhesivo Single Bond Universal (3M)',
        'category': 'Operatoria & Estética',
        'unit': 'Aplicación',
        'cost_unit': 42.00,
        'stock_current': 88,
        'stock_min': 25,
        'supplier': '3M Oral Care México'
    },
    {
        'id': 'ins-44',
        'name': 'Silicona por Adición Masilla Putty + Liviana Light Express XT (3M)',
        'category': 'Prótesis & Toma Impresión',
        'unit': 'Juego Impresión',
        'cost_unit': 260.00,
        'stock_current': 38,
        'stock_min': 10,
        'supplier': '3M Oral Care México'
    },
    {
        'id': 'ins-45',
        'name': 'Cemento Resinoso Dual Autoadhesivo RelyX Ultimate (3M)',
        'category': 'Prótesis & Toma Impresión',
        'unit': 'Dosis Cementado',
        'cost_unit': 185.00,
        'stock_current': 42,
        'stock_min': 12,
        'supplier': '3M Oral Care México'
    },
    {
        'id': 'ins-46',
        'name': 'Cemento Resinoso Fotocurable RelyX Veneer para Carillas (3M)',
        'category': 'Prótesis & Toma Impresión',
        'unit': 'Dosis Cementado',
        'cost_unit': 210.00,
        'stock_current': 29,
        'stock_min': 8,
        'supplier': '3M Oral Care México'
    },
    {
        'id': 'ins-47',
        'name': 'Hilo Retractor Gingival Tejido Ultrapak + Hemodent',
        'category': 'Prótesis & Toma Impresión',
        'unit': 'Aplicación',
        'cost_unit': 48.00,
        'stock_current': 56,
        'stock_min': 15,
        'supplier': 'Ultradent México'
    },
    {
        'id': 'ins-48',
        'name': 'Kit Gel Blanqueador Peróxido Hidrógeno 38% Opalescence Boost',
        'category': 'Operatoria & Estética',
        'unit': 'Kit Jeringa',
        'cost_unit': 480.00,
        'stock_current': 30,
        'stock_min': 8,
        'supplier': 'Ultradent México'
    },
    {
        'id': 'ins-49',
        'name': 'Barrera Gingival Fotopolimerizable OpalDam + Retractor Labial',
        'category': 'Operatoria & Estética',
        'unit': 'Aplicación',
        'cost_unit': 120.00,
        'stock_current': 36,
        'stock_min': 10,
        'supplier': 'Ultradent México'
    },
    {
        'id': 'ins-50',
        'name': 'Fresas de Diamante Micro-Grano para Tallado Protésico (JOTA Swiss)',
        'category': 'Prótesis & Toma Impresión',
        'unit': 'Desgaste Uso',
        'cost_unit': 65.00,
        'stock_current': 78,
        'stock_min': 20,
        'supplier': 'Depósito Dental Monterrey'
    },

    # 7. Periodoncia, Preventiva & Odontopediatría
    {
        'id': 'ins-51',
        'name': 'Pasta Profiláctica Zirconia + Cepillo y Copa de Goma Montada',
        'category': 'Periodoncia & Preventiva',
        'unit': 'Aplicación',
        'cost_unit': 38.00,
        'stock_current': 165,
        'stock_min': 40,
        'supplier': 'Dentarix MTY'
    },
    {
        'id': 'ins-52',
        'name': 'Punta Desechable Ultrasonido Piezoeléctrico / Profilaxis',
        'category': 'Periodoncia & Preventiva',
        'unit': 'Sesión',
        'cost_unit': 25.00,
        'stock_current': 92,
        'stock_min': 30,
        'supplier': 'Dentarix MTY'
    },
    {
        'id': 'ins-53',
        'name': 'Barniz de Flúor Saborizado Monodosis Duraphat / Enamel Pro',
        'category': 'Periodoncia & Preventiva',
        'unit': 'Sobre Monodosis',
        'cost_unit': 35.00,
        'stock_current': 135,
        'stock_min': 35,
        'supplier': 'Dentarix MTY'
    },
    {
        'id': 'ins-54',
        'name': 'Sellador de Fosetas y Fisuras Fotopolimerizable Clinpro (3M)',
        'category': 'Periodoncia & Preventiva',
        'unit': 'Cuadrante',
        'cost_unit': 72.00,
        'stock_current': 48,
        'stock_min': 15,
        'supplier': '3M Oral Care México'
    },
    {
        'id': 'ins-55',
        'name': 'Kit Exploración Desechable (Espejo, Sonda OMS, Pinza) + Funda RVG Rayos X',
        'category': 'Periodoncia & Preventiva',
        'unit': 'Kit Consulta',
        'cost_unit': 30.00,
        'stock_current': 215,
        'stock_min': 60,
        'supplier': 'Depósito Dental Monterrey'
    }
]

# Standard BASE BIOSAFETY & STERILIZATION required in every clinical consultation
# 1x Autoclave ($18.50), 1x Gasa ($7.50), 1x Rollos algodon ($3.80), 1x Babero ($3.50),
# 1x Eyector ($4.00), 1x Vaso ($1.50), 1x Barrera sillon ($6.00), 1x Guantes nitrilo ($5.50),
# 1x Cubrebocas KN95 ($7.00), 1x Gorro cofia ($2.50), 1x Cubrebandeja ($2.20), 1x Desinfeccion sillon ($6.50)
BASE_CLINICAL_SUPPLIES = [
    {'id': 'ins-01', 'qty': 1, 'name': 'Ciclo Esterilización Autoclave'},
    {'id': 'ins-02', 'qty': 1, 'name': 'Gasa Quirúrgica Estéril 5x5 cm'},
    {'id': 'ins-04', 'qty': 1, 'name': 'Rollos de Algodón Odontológico #2'},
    {'id': 'ins-05', 'qty': 1, 'name': 'Babero Impermeable Plastificado'},
    {'id': 'ins-06', 'qty': 1, 'name': 'Eyector de Saliva Desechable'},
    {'id': 'ins-07', 'qty': 1, 'name': 'Vaso Plástico Descartable 5oz'},
    {'id': 'ins-08', 'qty': 1, 'name': 'Película de Barrera Plástica'},
    {'id': 'ins-09', 'qty': 1, 'name': 'Guantes de Examen Nitrilo (Par)'},
    {'id': 'ins-11', 'qty': 1, 'name': 'Mascarilla KN95 Médica'},
    {'id': 'ins-12', 'qty': 1, 'name': 'Cofia Plisada Descartable'},
    {'id': 'ins-14', 'qty': 1, 'name': 'Cubrebandeja de Papel Grado Médico'},
    {'id': 'ins-16', 'qty': 1, 'name': 'Desinfección de Superficies Virucida'}
]

# Hyper-meticulous recipes: Base sterilization/gasas + procedure-specific materials
TREATMENT_RECIPES = {
    'implante': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-23', 'qty': 1, 'name': 'Implante Titanio Neodent Helix GM'},
        {'id': 'ins-24', 'qty': 1, 'name': 'Tornillo Cierre & Pilar Cicatrización'},
        {'id': 'ins-25', 'qty': 1, 'name': 'Bulto Quirúrgico Completo Implantología'},
        {'id': 'ins-17', 'qty': 2, 'name': 'Ampolleta Articaína 4% c/Epinefrina'},
        {'id': 'ins-20', 'qty': 2, 'name': 'Agujas Dentales Descartables 30G'},
        {'id': 'ins-26', 'qty': 1, 'name': 'Hoja de Bisturí Quirúrgica #15'},
        {'id': 'ins-27', 'qty': 1, 'name': 'Sutura Reabsorbible Vicryl 4-0'},
        {'id': 'ins-29', 'qty': 1, 'name': 'Esponja Quirúrgica Hemostática Gelfoam'},
        {'id': 'ins-10', 'qty': 1, 'name': 'Guantes Quirúrgicos Estériles (Par)'},
        {'id': 'ins-31', 'qty': 1, 'name': 'Solución Fisiológica Irrigación Fisiocirugía'},
        {'id': 'ins-32', 'qty': 1, 'name': 'Cánula Aspiración Quirúrgica Alta Potencia'}
    ],
    'cirugia': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-17', 'qty': 3, 'name': 'Ampolleta Articaína 4% c/Epinefrina'},
        {'id': 'ins-20', 'qty': 2, 'name': 'Agujas Dentales Descartables 30G'},
        {'id': 'ins-26', 'qty': 1, 'name': 'Hoja de Bisturí Quirúrgica #15'},
        {'id': 'ins-30', 'qty': 1, 'name': 'Fresa Quirúrgica Zekrya Carburo'},
        {'id': 'ins-28', 'qty': 1, 'name': 'Sutura Seda Negra 3-0'},
        {'id': 'ins-29', 'qty': 1, 'name': 'Esponja Hemostática Gelfoam'},
        {'id': 'ins-13', 'qty': 1, 'name': 'Campo Quirúrgico Fenestrado'},
        {'id': 'ins-10', 'qty': 1, 'name': 'Guantes Quirúrgicos Estériles (Par)'},
        {'id': 'ins-32', 'qty': 1, 'name': 'Cánula Aspiración Quirúrgica'}
    ],
    'endodoncia': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-33', 'qty': 1, 'name': 'Lima Rotatoria WaveOne Gold Primary'},
        {'id': 'ins-34', 'qty': 1, 'name': 'Dique de Goma + Arco + Clamp/Grapa'},
        {'id': 'ins-35', 'qty': 1, 'name': 'Cemento Biocerámico AH Plus Sealer'},
        {'id': 'ins-36', 'qty': 1, 'name': 'Gutapercha + Puntas Papel Conicidad'},
        {'id': 'ins-37', 'qty': 1, 'name': 'Irrigantes NaOCl 5.25% + EDTA 17%'},
        {'id': 'ins-17', 'qty': 2, 'name': 'Ampolleta Articaína 4% c/Epinefrina'},
        {'id': 'ins-20', 'qty': 2, 'name': 'Agujas Dentales Descartables 30G'}
    ],
    'alineadores': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-41', 'qty': 1, 'name': 'Kit Ataches Resina Microhíbrida'},
        {'id': 'ins-44', 'qty': 1, 'name': 'Silicona Adición Express XT'},
        {'id': 'ins-43', 'qty': 1, 'name': 'Ácido Fosfórico 37% + Adhesivo Universal'},
        {'id': 'ins-15', 'qty': 1, 'name': 'Microbrush Aplicador (Par)'}
    ],
    'brackets': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-38', 'qty': 1, 'name': 'Arco Cu-NiTi Termoactivo Superelástico'},
        {'id': 'ins-39', 'qty': 1, 'name': 'Resina Cementado Transbond XT'},
        {'id': 'ins-40', 'qty': 1, 'name': 'Tubos Molares + Módulos Alastik'},
        {'id': 'ins-43', 'qty': 1, 'name': 'Ácido Fosfórico al 37%'},
        {'id': 'ins-51', 'qty': 1, 'name': 'Profilaxis Previa con Pasta Zirconia'}
    ],
    'carillas': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-46', 'qty': 1, 'name': 'Cemento RelyX Veneer para Carillas'},
        {'id': 'ins-44', 'qty': 1, 'name': 'Silicona Adición Express XT'},
        {'id': 'ins-47', 'qty': 1, 'name': 'Hilo Retractor Ultrapak + Hemodent'},
        {'id': 'ins-50', 'qty': 1, 'name': 'Fresa Diamante Tallado JOTA Swiss'},
        {'id': 'ins-43', 'qty': 1, 'name': 'Ácido Fosfórico + Adhesivo Universal'},
        {'id': 'ins-17', 'qty': 1, 'name': 'Ampolleta Articaína 4% c/Epinefrina'},
        {'id': 'ins-20', 'qty': 1, 'name': 'Aguja Dental Descartable 30G'}
    ],
    'zirconia': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-45', 'qty': 1, 'name': 'Cemento RelyX Ultimate Dual'},
        {'id': 'ins-44', 'qty': 1, 'name': 'Silicona Adición Express XT'},
        {'id': 'ins-47', 'qty': 1, 'name': 'Hilo Retractor Ultrapak'},
        {'id': 'ins-50', 'qty': 1, 'name': 'Fresa Desgaste Tallado JOTA'},
        {'id': 'ins-17', 'qty': 1, 'name': 'Ampolleta Articaína 4% c/Epinefrina'},
        {'id': 'ins-20', 'qty': 1, 'name': 'Aguja Dental Descartable 30G'}
    ],
    'blanqueamiento': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-48', 'qty': 1, 'name': 'Kit Gel Opalescence Boost 38%'},
        {'id': 'ins-49', 'qty': 1, 'name': 'Barrera OpalDam + Retractor Labial'},
        {'id': 'ins-51', 'qty': 1, 'name': 'Pasta Profiláctica Zirconia Previa'}
    ],
    'limpieza': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-51', 'qty': 1, 'name': 'Pasta Profiláctica Zirconia + Cepillo'},
        {'id': 'ins-52', 'qty': 1, 'name': 'Punta Ultrasonido Piezoeléctrico'},
        {'id': 'ins-53', 'qty': 1, 'name': 'Barniz Flúor Saborizado Duraphat'}
    ],
    'odontopediatria': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-54', 'qty': 2, 'name': 'Sellador Fosetas Clinpro (2 cuadrantes)'},
        {'id': 'ins-53', 'qty': 1, 'name': 'Barniz Flúor Saborizado Fresa'},
        {'id': 'ins-22', 'qty': 1, 'name': 'Gel Anestésico Tópico Saborizado'},
        {'id': 'ins-51', 'qty': 1, 'name': 'Pasta Profiláctica Infantil'}
    ],
    'valoracion': BASE_CLINICAL_SUPPLIES + [
        {'id': 'ins-55', 'qty': 1, 'name': 'Kit Exploración Desechable + Funda RVG'}
    ]
}

RECIPE_LABELS = {
    'implante': 'Colocación de Implante Dental de Titanio',
    'cirugia': 'Cirugía Oral & Terceros Molares',
    'endodoncia': 'Endodoncia Microscópica Rotatoria',
    'alineadores': 'Ortodoncia Invisible con Alineadores',
    'brackets': 'Colocación & Control de Brackets Metálicos',
    'carillas': 'Carillas de Porcelana Estratificada',
    'zirconia': 'Coronas y Puentes Fijos de Zirconia',
    'blanqueamiento': 'Diseño de Sonrisa & Blanqueamiento Opalescence',
    'limpieza': 'Limpieza Ultrasónica & Profilaxis Preventiva',
    'odontopediatria': 'Odontopediatría Integral & Selladores',
    'valoracion': 'Valoración Inicial & Diagnóstico Digital'
}

TREATMENT_VALUES = {
    'alineador': 28000, 'invisible': 28000,
    'implante': 12500, 'carilla': 7200,
    'zirconia': 4500, 'corona': 4500, 'puente': 4500,
    'diseño': 3800, 'blanqueamiento': 3800,
    'cirug': 3200, 'tercer': 3200, 'endodoncia': 2400,
    'bracket': 1999, 'ortodoncia': 1999,
    'pediatr': 1650, 'sellador': 1650,
    'limpieza': 950, 'profilaxis': 950,
    'resina': 950, 'valoración': 250
}

TREATMENT_LAB_COSTS = {
    'alineador': 6200, 'invisible': 6200,
    'implante': 2400, 'carilla': 1450,
    'zirconia': 950, 'corona': 950, 'puente': 950,
    'blanqueamiento': 420, 'diseño': 420,
    'cirug': 350, 'tercer': 350, 'endodoncia': 320,
    'bracket': 380, 'ortodoncia': 380,
    'pediatr': 210, 'sellador': 210,
    'limpieza': 120, 'profilaxis': 120,
    'resina': 150, 'valoración': 40
}

def load_inventory_data():
    if os.path.exists(INV_PATH):
        try:
            with open(INV_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('supplies') and len(data['supplies']) >= len(DETAILED_SUPPLIES_CATALOG):
                    return data
        except Exception:
            pass
    # Initialize default
    data = {
        'supplies': DETAILED_SUPPLIES_CATALOG,
        'recipes': TREATMENT_RECIPES
    }
    save_inventory_data(data)
    return data

def save_inventory_data(data):
    with open(INV_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_treatment_val(t_str):
    t = (t_str or '').lower()
    for k, v in TREATMENT_VALUES.items():
        if k in t: return v
    return 950

def get_treatment_lab(t_str):
    t = (t_str or '').lower()
    for k, v in TREATMENT_LAB_COSTS.items():
        if k in t: return v
    return 150

def get_recipe_key(t_str):
    t = (t_str or '').lower()
    if 'implante' in t: return 'implante'
    if 'cirug' in t or 'tercer' in t: return 'cirugia'
    if 'endo' in t: return 'endodoncia'
    if 'alineador' in t or 'invisible' in t: return 'alineadores'
    if 'bracket' in t or 'orto' in t: return 'brackets'
    if 'carilla' in t: return 'carillas'
    if 'zirconia' in t or 'corona' in t or 'puente' in t: return 'zirconia'
    if 'diseño' in t or 'blanqueamiento' in t: return 'blanqueamiento'
    if 'limpieza' in t or 'profilaxis' in t: return 'limpieza'
    if 'pediatr' in t or 'sellador' in t: return 'odontopediatria'
    return 'valoracion'

def calculate_inventory_metrics():
    inv_data = load_inventory_data()
    supplies = inv_data.get('supplies', [])
    recipes = inv_data.get('recipes', TREATMENT_RECIPES)
    supplies_dict = {s['id']: s for s in supplies}

    # Dynamic cost per recipe based on current unit prices
    recipe_costs = {}
    for r_key, items in recipes.items():
        rc_total = 0.0
        detailed_items = []
        for it in items:
            s = supplies_dict.get(it['id'])
            unit_cost = s['cost_unit'] if s else 0.0
            total_it_cost = it['qty'] * unit_cost
            rc_total += total_it_cost
            detailed_items.append({
                'id': it['id'],
                'name': s['name'] if s else it.get('name', ''),
                'category': s['category'] if s else 'General',
                'unit': s['unit'] if s else 'Pieza',
                'qty': it['qty'],
                'cost_unit': unit_cost,
                'total_cost': round(total_it_cost, 2)
            })
        recipe_costs[r_key] = {
            'recipe_key': r_key,
            'label': RECIPE_LABELS.get(r_key, r_key.capitalize()),
            'total_cost': round(rc_total, 2),
            'items': detailed_items
        }

    # Read appointments and doctors
    appts = []
    if os.path.exists(CRM_PATH):
        with open(CRM_PATH, 'r', encoding='utf-8') as f:
            appts = json.load(f)

    docs = []
    if os.path.exists(DOCS_PATH):
        with open(DOCS_PATH, 'r', encoding='utf-8') as f:
            docs = json.load(f)

    doc_stats_map = {}
    for d in docs:
        comm = d.get('comision_porcentaje')
        if not comm:
            spec = d.get('specialty', '').lower()
            comm = 50 if 'endo' in spec else (45 if ('implan' in spec or 'cirug' in spec or 'protes' in spec or 'zirconia' in spec) else 40)
        doc_stats_map[d['name']] = {
            'id': d['id'],
            'name': d['name'],
            'specialty': d['specialty'],
            'cedula': d.get('cedula', '8294711'),
            'photo': d.get('photo', ''),
            'color': d.get('color', '#06B6D4'),
            'comision_pct': comm,
            'citas_total': 0,
            'ingresos_brutos_mxn': 0.0,
            'costo_insumos_mxn': 0.0,
            'costo_lab_mxn': 0.0,
            'consumed_items': {}, # supply_id -> qty
            'treatments_breakdown': {},
            'patients_history': [] # List of individual patient consumption sheets
        }

    global_item_usage = {} # supply_id -> total qty used
    supplies_monthly_timeline = {} # supply_id -> { 'Agosto 2026': qty, 'Septiembre 2026': qty, 'Octubre 2026': qty }

    for a in appts:
        st = str(a.get('status', '')).lower()
        if 'cancel' in st:
            continue
        doc_name = a.get('doctor_asignado', '')
        treat = a.get('tratamiento', '')
        f_cita = str(a.get('fecha_cita', ''))
        
        # Determine month
        month_label = 'Agosto 2026' if f_cita.startswith('2026-08') else ('Septiembre 2026' if f_cita.startswith('2026-09') else 'Octubre 2026')

        matched_doc = None
        for k in doc_stats_map.keys():
            if k in doc_name or doc_name in k:
                matched_doc = k
                break
        if not matched_doc:
            matched_doc = list(doc_stats_map.keys())[0]

        d_stat = doc_stats_map[matched_doc]
        val = get_treatment_val(treat)
        lab = get_treatment_lab(treat)
        r_key = get_recipe_key(treat)
        r_info = recipe_costs.get(r_key, {'total_cost': 0.0, 'items': []})

        d_stat['citas_total'] += 1
        d_stat['ingresos_brutos_mxn'] += val
        d_stat['costo_lab_mxn'] += lab
        d_stat['costo_insumos_mxn'] += r_info['total_cost']

        # Patient individual consumption sheet
        patient_supplies_detail = []
        for it in r_info['items']:
            sid = it['id']
            qty = it['qty']
            d_stat['consumed_items'][sid] = d_stat['consumed_items'].get(sid, 0) + qty
            global_item_usage[sid] = global_item_usage.get(sid, 0) + qty

            # Monthly timeline tracking
            if sid not in supplies_monthly_timeline:
                supplies_monthly_timeline[sid] = {'Agosto 2026': 0, 'Septiembre 2026': 0, 'Octubre 2026': 0}
            supplies_monthly_timeline[sid][month_label] += qty

            patient_supplies_detail.append({
                'id': sid,
                'name': it['name'],
                'category': it.get('category', 'General'),
                'unit': it['unit'],
                'qty': qty,
                'cost_unit': it['cost_unit'],
                'total_cost': it['total_cost']
            })

        patient_sheet = {
            'appointment_id': a.get('id', f'coba-{d_stat["citas_total"]}'),
            'patient_name': a.get('nombre', 'Paciente'),
            'patient_phone': a.get('telefono', '+52 81 0000 0000'),
            'patient_email': a.get('email', 'paciente@gmail.com'),
            'appointment_date': f_cita or '2026-09-15',
            'appointment_time': a.get('hora_cita', '10:00 AM'),
            'sucursal': a.get('sucursal', 'Monterrey Centro'),
            'treatment_name': treat,
            'treatment_label': RECIPE_LABELS.get(r_key, treat),
            'ticket_price_mxn': val,
            'supplies_cost_mxn': r_info['total_cost'],
            'lab_cost_mxn': lab,
            'margin_mxn': round(val - r_info['total_cost'] - lab, 2),
            'margin_pct': round(((val - r_info['total_cost'] - lab) / val * 100), 1) if val > 0 else 0.0,
            'supplies_consumed': patient_supplies_detail
        }
        d_stat['patients_history'].append(patient_sheet)

        # Breakdown per procedure in doctor
        tb = d_stat['treatments_breakdown'].setdefault(r_key, {
            'recipe_key': r_key,
            'label': RECIPE_LABELS.get(r_key, r_key.capitalize()),
            'citas': 0,
            'ingresos_total': 0.0,
            'costo_insumos_total': 0.0,
            'costo_insumos_unitario': r_info['total_cost'],
            'costo_lab_total': 0.0
        })
        tb['citas'] += 1
        tb['ingresos_total'] += val
        tb['costo_insumos_total'] += r_info['total_cost']
        tb['costo_lab_total'] += lab

    # Finalize doctor balances and margins
    doctor_balances = []
    total_clinic_income = 0.0
    total_clinic_supplies = 0.0
    total_clinic_lab = 0.0

    for d_name, d_stat in doc_stats_map.items():
        gross = d_stat['ingresos_brutos_mxn']
        insumos = round(d_stat['costo_insumos_mxn'], 2)
        lab = d_stat['costo_lab_mxn']
        total_clinic_income += gross
        total_clinic_supplies += insumos
        total_clinic_lab += lab

        ratio_insumos = round((insumos / gross * 100), 1) if gross > 0 else 0.0
        margen_bruto = max(0.0, gross - insumos - lab)
        net_base_doc = max(0.0, gross - lab)
        doc_net = round(net_base_doc * (d_stat['comision_pct'] / 100.0))
        quincena = round(doc_net / 4.0)
        clinic_net = max(0.0, gross - insumos - lab - doc_net)

        if ratio_insumos <= 15:
            eficiencia = 'Excelente'
            eficiencia_color = '#10B981'
        elif ratio_insumos <= 25:
            eficiencia = 'Moderado'
            eficiencia_color = '#06B6D4'
        else:
            eficiencia = 'Alto Consumo'
            eficiencia_color = '#F59E0B'

        consumed_list = []
        for sid, qty in d_stat['consumed_items'].items():
            s = supplies_dict.get(sid)
            if s:
                consumed_list.append({
                    'id': sid,
                    'name': s['name'],
                    'category': s['category'],
                    'unit': s['unit'],
                    'cost_unit': s['cost_unit'],
                    'qty': qty,
                    'total_cost': round(qty * s['cost_unit'], 2)
                })
        consumed_list.sort(key=lambda x: x['total_cost'], reverse=True)

        tb_list = list(d_stat['treatments_breakdown'].values())
        tb_list.sort(key=lambda x: x['ingresos_total'], reverse=True)

        # Sort patient history by date descending
        d_stat['patients_history'].sort(key=lambda x: x['appointment_date'], reverse=True)

        doctor_balances.append({
            'id': d_stat['id'],
            'name': d_stat['name'],
            'specialty': d_stat['specialty'],
            'cedula': d_stat['cedula'],
            'photo': d_stat['photo'],
            'color': d_stat['color'],
            'comision_pct': d_stat['comision_pct'],
            'citas_total': d_stat['citas_total'],
            'ingresos_brutos_mxn': gross,
            'costo_insumos_mxn': insumos,
            'costo_lab_mxn': lab,
            'margen_bruto_operativo_mxn': round(margen_bruto, 2),
            'ratio_insumos_pct': ratio_insumos,
            'pago_neto_doctor_mxn': doc_net,
            'liquidacion_quincenal_mxn': quincena,
            'utilidad_neta_clinica_mxn': round(clinic_net, 2),
            'eficiencia': eficiencia,
            'eficiencia_color': eficiencia_color,
            'consumed_supplies': consumed_list,
            'treatments_breakdown': tb_list,
            'patients_history': d_stat['patients_history']
        })

    doctor_balances.sort(key=lambda x: x['ingresos_brutos_mxn'], reverse=True)

    # Attach total consumed and timeline to each supply in catalog
    supplies_with_metrics = []
    total_stock_value = 0.0
    low_stock_alerts = []

    for s in supplies:
        sid = s['id']
        total_used = global_item_usage.get(sid, 0)
        total_spent = round(total_used * s['cost_unit'], 2)
        stock_val = round(s.get('stock_current', 0) * s['cost_unit'], 2)
        total_stock_value += stock_val
        is_low = (s.get('stock_current', 0) <= s.get('stock_min', 0))
        if is_low:
            low_stock_alerts.append(s)

        timeline = supplies_monthly_timeline.get(sid, {'Agosto 2026': 0, 'Septiembre 2026': 0, 'Octubre 2026': 0})
        s_copy = dict(s)
        s_copy['stock_value_mxn'] = stock_val
        s_copy['total_used_units'] = total_used
        s_copy['total_spent_mxn'] = total_spent
        s_copy['is_low_stock'] = is_low
        s_copy['monthly_timeline'] = {
            'Agosto 2026': {'units': timeline['Agosto 2026'], 'spent': round(timeline['Agosto 2026'] * s['cost_unit'], 2)},
            'Septiembre 2026': {'units': timeline['Septiembre 2026'], 'spent': round(timeline['Septiembre 2026'] * s['cost_unit'], 2)},
            'Octubre 2026': {'units': timeline['Octubre 2026'], 'spent': round(timeline['Octubre 2026'] * s['cost_unit'], 2)}
        }
        supplies_with_metrics.append(s_copy)

    # Sort supplies by total spent descending for analytics
    top_spent_supplies = sorted(supplies_with_metrics, key=lambda x: x['total_spent_mxn'], reverse=True)
    top_volume_supplies = sorted(supplies_with_metrics, key=lambda x: x['total_used_units'], reverse=True)

    global_ratio = round((total_clinic_supplies / total_clinic_income * 100), 1) if total_clinic_income > 0 else 0.0

    return {
        'status': 'ok',
        'supplies': supplies_with_metrics,
        'top_spent_supplies': top_spent_supplies[:10],
        'top_volume_supplies': top_volume_supplies[:10],
        'recipe_costs': recipe_costs,
        'doctor_balances': doctor_balances,
        'clinic_summary': {
            'total_items_catalog': len(supplies),
            'valor_inventario_bodega_mxn': round(total_stock_value, 2),
            'total_insumos_consumidos_mxn': round(total_clinic_supplies, 2),
            'total_facturacion_mxn': round(total_clinic_income, 2),
            'total_lab_mxn': round(total_clinic_lab, 2),
            'margen_post_insumos_mxn': round(total_clinic_income - total_clinic_supplies - total_clinic_lab, 2),
            'ratio_global_insumos_pct': global_ratio,
            'total_alertas_stock_bajo': len(low_stock_alerts),
            'low_stock_items': low_stock_alerts
        }
    }

def update_supply_price(item_id, new_price):
    data = load_inventory_data()
    found = False
    new_price = max(0.01, float(new_price))
    for s in data.get('supplies', []):
        if s['id'] == item_id:
            s['cost_unit'] = new_price
            found = True
            break
    if found:
        save_inventory_data(data)
    return found

def update_supply_stock(item_id, new_stock):
    data = load_inventory_data()
    found = False
    new_stock = max(0, int(new_stock))
    for s in data.get('supplies', []):
        if s['id'] == item_id:
            s['stock_current'] = new_stock
            found = True
            break
    if found:
        save_inventory_data(data)
    return found

def save_or_create_supply(item_data):
    data = load_inventory_data()
    supplies = data.get('supplies', [])
    item_id = item_data.get('id', '').strip()
    
    if item_id:
        for idx, s in enumerate(supplies):
            if s['id'] == item_id:
                supplies[idx].update({
                    'name': item_data.get('name', s['name']).strip(),
                    'category': item_data.get('category', s['category']),
                    'unit': item_data.get('unit', s['unit']),
                    'cost_unit': float(item_data.get('cost_unit', s['cost_unit'])),
                    'stock_current': int(item_data.get('stock_current', s['stock_current'])),
                    'stock_min': int(item_data.get('stock_min', s['stock_min'])),
                    'supplier': item_data.get('supplier', s.get('supplier', '')).strip()
                })
                save_inventory_data(data)
                return supplies[idx]
                
    max_num = 0
    for s in supplies:
        sid = s.get('id', '')
        if sid.startswith('ins-'):
            try:
                num = int(sid.split('-')[1])
                if num > max_num: max_num = num
            except Exception:
                pass
    new_id = f"ins-{max_num + 1:02d}"
    new_item = {
        'id': new_id,
        'name': item_data.get('name', 'Nuevo Insumo Clínico').strip(),
        'category': item_data.get('category', 'Materiales Generales'),
        'unit': item_data.get('unit', 'Pieza'),
        'cost_unit': max(0.01, float(item_data.get('cost_unit', 10.0))),
        'stock_current': max(0, int(item_data.get('stock_current', 50))),
        'stock_min': max(0, int(item_data.get('stock_min', 10))),
        'supplier': item_data.get('supplier', 'Depósito Dental Monterrey').strip()
    }
    supplies.append(new_item)
    data['supplies'] = supplies
    save_inventory_data(data)
    return new_item

def delete_supply(item_id):
    data = load_inventory_data()
    supplies = data.get('supplies', [])
    orig_len = len(supplies)
    supplies = [s for s in supplies if s['id'] != item_id]
    if len(supplies) < orig_len:
        data['supplies'] = supplies
        for rk, items in data.get('recipes', {}).items():
            data['recipes'][rk] = [it for it in items if it['id'] != item_id]
        save_inventory_data(data)
        return True
    return False

if __name__ == '__main__':
    res = calculate_inventory_metrics()
    print('Status:', res['status'])
    print('Supplies Count:', len(res['supplies']))
    print('Doctor balances count:', len(res['doctor_balances']))
    print('Top spent supply:', res['top_spent_supplies'][0]['name'], res['top_spent_supplies'][0]['total_spent_mxn'])
    doc = res['doctor_balances'][0]
    print('Doc 1:', doc['name'], 'Patients with supply history:', len(doc['patients_history']))
    p = doc['patients_history'][0]
    print('Patient sample:', p['patient_name'], '-', p['treatment_name'], '- Costo insumos:', p['supplies_cost_mxn'], '- Insumos usados:', len(p['supplies_consumed']))
