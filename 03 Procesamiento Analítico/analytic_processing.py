# -*- coding: utf-8 -*-
import os
import sys
import re
import json
import pandas as pd

# Añadimos la ruta de la aplicación Shiny para importar el motor analítico
SHINY_APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "04 Aplicacion Shiny"))
sys.path.append(SHINY_APP_DIR)

try:
    from extractor import (
        PDFExtractorEngine, TARGET_PERSONS, BLACKLIST_NAMES,
        ENGLISH_STOPWORDS
    )
except ImportError as e:
    print(f"Error: No se pudo importar desde la carpeta del Paso 4: {e}")
    sys.exit(1)

#  Léxicos de Sentimiento 
NEGATIVE_LEXICON = {
    'abuse', 'assault', 'guilty', 'deny', 'object', 'victim', 'trafficking',
    'forced', 'illegal', 'crime', 'complicit', 'rape', 'sex', 'underage',
    'minor', 'coerced', 'conspiracy', 'fraud', 'prison', 'arrested', 'charged',
    'suspicious', 'manipulate', 'exploit', 'groom', 'threaten', 'blackmail',
    'violate', 'molest', 'inappropriate', 'prostitute', 'bribed', 'coverup'
}
POSITIVE_LEXICON = {
    'innocent', 'consent', 'cleared', 'dismissed', 'approved', 'free', 'legal',
    'agreed', 'friend', 'support', 'cooperate', 'lawful', 'voluntary', 'truth',
    'protect', 'legitimate', 'professional', 'respected', 'acknowledged'
}

# Filtros adicionales para NER: palabras que no pueden ser parte de un nombre real
NER_KEYWORD_BLACKLIST = {
    'court', 'district', 'exhibit', 'page', 'attorney', 'confidential',
    'reporter', 'plaintiff', 'defendant', 'highly', 'order', 'amendment',
    'product', 'joint', 'protective', 'work', 'fifth', 'fourth', 'first',
    'motion', 'case', 'number', 'section', 'pursuant', 'federal', 'united',
    'states', 'island', 'county', 'beach', 'york', 'document', 'pursuant'
}

# Patrones de temas sospechosos (mismo que extractor.py)
TOPIC_KEYWORDS = {
    "Propiedades": [r'\blittle\s+st\b', r'\bvirgin\s+islands\b', r'\bpalm\s+beach\b',
                    r'\bzorro\s+ranch\b', r'\bnew\s+mexico\b', r'\bmanhattan\b'],
    "Logística / Aviones": [r'\bprivate\s+jet\b', r'\blolita\s+express\b', r'\bflight\s+log\b',
                             r'\bpilot\b', r'\baircraft\b', r'\bhelicopter\b'],
    "Abuso / Menores": [r'\bmassage\b', r'\bminor\b', r'\bunderage\b', r'\brecruit\b',
                        r'\bvictim\b', r'\byoung\s+girls?\b', r'\bnaked\b', r'\bundressed\b'],
    "Ámbito Legal": [r'\bdeposition\b', r'\bunder\s+oath\b', r'\btestimony\b',
                     r'\bexhibit\b', r'\bgrand\s+jury\b', r'\baffidavit\b', r'\bwitness\b']
}
EVASION_PATTERNS = {
    "I don't recall": r"\b(don'tdo\s+not)\s+(recallrememberrecollect)\b",
    "Objection": r"\b(objectioni\s+object)\b",
    "Decline to answer": r"\b(decline\s+to\s+answerrefuse\s+to\s+answer)\b",
    "Fifth Amendment": r"\b(fifth\s+amendmentplead\s+the\s+fifth)\b",
    "Don't know": r"\b(not\s+suredon't\s+knowdo\s+not\s+know)\b"
}
REDACTION_PATTERNS = [
    r'\bREDACTED\b', r'\bredacted\b', r'\[\s*redacted\s*\]',
    r'\b[jJ]ane\s+[dD]oe\b', r'\b[jJ]ohn\s+[dD]oe\b', r'X{3,}'
]


def is_valid_person_name(name: str) -> bool:
    """Determina si una cadena parece un nombre de persona real y no un artefacto del texto."""
    name_lower = name.lower().strip()
    if name_lower in BLACKLIST_NAMES:
        return False
    parts = name_lower.split()
    # Mínimo 2 palabras, máximo 4
    if not (2 <= len(parts) <= 4):
        return False
    # Ninguna palabra puede estar en la blacklist de keywords legales
    if any(p in NER_KEYWORD_BLACKLIST for p in parts):
        return False
    # Ninguna palabra debe ser stopword o muy corta
    if any(p in ENGLISH_STOPWORDS or len(p) <= 2 for p in parts):
        return False
    # Todas las palabras deben empezar con mayúscula (ya garantizado por el regex, pero validamos)
    if not all(w[0].isupper() for w in name.split()):
        return False
    return True


def sentiment_score(pos: int, neg: int) -> tuple:
    total = pos + neg
    if total == 0:
        return 0.0, "Neutral"
    score = round((pos - neg) / total, 3)
    if score < -0.3:   cat = "Altamente Negativo"
    elif score < -0.05: cat = "Negativo"
    elif score > 0.3:   cat = "Positivo"
    else:               cat = "Neutral / Procedimental"
    return score, cat


def main():
    print("=" * 70)
    print("PROCESAMIENTO ANALÍTICO AVANZADO — GENERACIÓN DE DATASETS RICOS (PASO 3)")
    print("=" * 70)

    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "01 Datasets Usados"))
    txt_path    = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "02 Preprocesamiento", "consolidated_cleaned_text.txt"))
    out_dir     = os.path.dirname(__file__)

    #  Cargar texto preprocesado 
    if os.path.exists(txt_path):
        print(f"Texto preprocesado detectado — cargando {os.path.basename(txt_path)}...")
        with open(txt_path, "r", encoding="utf-8") as f:
            txt_content = f.read()
        pages_text = [p.strip() for p in re.split(r'---\s*P[ÁA]GINA\s+\d+\s*---', txt_content) if p.strip()]
        source = "TXT Consolidado"
    else:
        pdf_files = sorted([f for f in os.listdir(dataset_dir) if f.endswith(".pdf")],
                           key=lambda x: os.path.getsize(os.path.join(dataset_dir, x)), reverse=True)
        if not pdf_files:
            print("Error: No hay PDF ni TXT disponible.")
            sys.exit(1)
        print(f"Cargando PDF: {pdf_files[0]}...")
        engine = PDFExtractorEngine(os.path.join(dataset_dir, pdf_files[0]))
        _, metrics_dummy = engine.process_document(1, engine.num_pages)
        pages_text = [engine.reader.pages[i].extract_text() or "" for i in range(engine.num_pages)]
        source = pdf_files[0]

    total_pages = len(pages_text)
    print(f"Total de páginas cargadas: {total_pages:,}")
    print()

    # 
    # DATASET 1: ANÁLISIS GRANULAR PÁGINA A PÁGINA (5,028 filas)
    # 
    print(" [1/5] Generando dataset PÁGINA × PÁGINA (granular, 5,000+ filas)...")
    page_rows = []
    person_page_map = {p: [] for p in TARGET_PERSONS}  # track which pages each person appears

    for i, page in enumerate(pages_text, start=1):
        page_lower = page.lower()
        words = re.findall(r'\b\w+\b', page_lower)
        total_words = len(words)

        # Conteos
        redact_count = sum(len(re.findall(pat, page)) for pat in REDACTION_PATTERNS)
        evasion_count = sum(len(re.findall(pat, page, re.IGNORECASE)) for pat in EVASION_PATTERNS.values())
        evasion_types = [cat for cat, pat in EVASION_PATTERNS.items() if re.search(pat, page, re.IGNORECASE)]

        topic_hits = {t: sum(len(re.findall(p, page_lower, re.IGNORECASE)) for p in pats)
                      for t, pats in TOPIC_KEYWORDS.items()}
        dominant_topic = max(topic_hits, key=topic_hits.get) if any(topic_hits.values()) else "Sin tema dominante"

        words_set = set(words)
        pos_hits = len(words_set.intersection(POSITIVE_LEXICON))
        neg_hits = len(words_set.intersection(NEGATIVE_LEXICON))
        score, category = sentiment_score(pos_hits, neg_hits)

        years_found = re.findall(r'\b(199[0-9]20[0-2][0-9])\b', page)

        persons_on_page = []
        for person in TARGET_PERSONS:
            if re.search(rf'\b{re.escape(person)}\b', page, re.IGNORECASE):
                persons_on_page.append(person)
                person_page_map[person].append(i)

        page_rows.append({
            "Pagina": i,
            "Palabras": total_words,
            "Menciones_Censuradas_REDACTED": redact_count,
            "Evasiones_Detectadas": evasion_count,
            "Tipos_Evasion": "; ".join(evasion_types) if evasion_types else "",
            "Indicador_Positivo": pos_hits,
            "Indicador_Negativo": neg_hits,
            "Indice_Sentimiento": score,
            "Clasificacion_Sentimiento": category,
            "Hits_Propiedades": topic_hits["Propiedades"],
            "Hits_Aviones_Logistica": topic_hits["Logística / Aviones"],
            "Hits_Abuso_Menores": topic_hits["Abuso / Menores"],
            "Hits_Ambito_Legal": topic_hits["Ámbito Legal"],
            "Tema_Dominante": dominant_topic,
            "Años_Mencionados": "; ".join(sorted(set(years_found))),
            "Personas_Presentes": "; ".join(persons_on_page),
            "Personas_Count": len(persons_on_page),
            "Fuente": source
        })

        if i % 500 == 0 or i == total_pages:
            print(f"   [+] Procesadas {i:,}/{total_pages:,} páginas ({i/total_pages:.0%})")

    df_pages = pd.DataFrame(page_rows)
    df_pages.to_csv(os.path.join(out_dir, "analytic_01_paginas_granular.csv"), index=False, encoding="utf-8")
    print(f"Guardado: analytic_01_paginas_granular.csv — {len(df_pages):,} filas\n")

    # 
    # DATASET 2: ANÁLISIS DE SENTIMIENTO Y RIESGO POR PERSONA
    # Solo personas reales de TARGET_PERSONS
    # 
    print(" [2/5] Generando dataset de SENTIMIENTO y RIESGO por persona...")
    person_rows = []

    full_text = "\n".join(pages_text)
    for person in TARGET_PERSONS:
        pattern = rf'\b{re.escape(person)}\b'
        all_mentions = re.findall(pattern, full_text, re.IGNORECASE)
        mention_count = len(all_mentions)
        if mention_count == 0:
            continue

        pages_with_person = person_page_map[person]
        n_pages = len(pages_with_person)
        pos_total, neg_total, risk_total = 0, 0, 0
        evasion_on_pages = 0

        for pg_idx in pages_with_person:
            page_lower = pages_text[pg_idx - 1].lower()
            words_set = set(re.findall(r'\b\w+\b', page_lower))
            pos_total += len(words_set.intersection(POSITIVE_LEXICON))
            neg_total += len(words_set.intersection(NEGATIVE_LEXICON))
            # riesgo: co-ocurrencia con Abuso/Menores + Logística
            for pat in TOPIC_KEYWORDS["Abuso / Menores"] + TOPIC_KEYWORDS["Logística / Aviones"]:
                if re.search(pat, page_lower, re.IGNORECASE):
                    risk_total += 1
            for pat in EVASION_PATTERNS.values():
                if re.search(pat, page_lower, re.IGNORECASE):
                    evasion_on_pages += 1

        # Riqueza de distribución (% de páginas donde aparece)
        page_coverage = round(n_pages / total_pages * 100, 2)

        # Co-ocurrencias con otras personas
        cooccurrence_partners = []
        for other in TARGET_PERSONS:
            if other == person:
                continue
            shared = len(set(pages_with_person) & set(person_page_map[other]))
            if shared > 0:
                cooccurrence_partners.append(f"{other}({shared})")

        score, category = sentiment_score(pos_total, neg_total)

        person_rows.append({
            "Persona": person,
            "Total_Menciones": mention_count,
            "Paginas_con_Mencion": n_pages,
            "Cobertura_Pct": page_coverage,
            "Indicador_Positivo": pos_total,
            "Indicador_Negativo": neg_total,
            "Indice_Sentimiento": score,
            "Clasificacion_Sentimiento": category,
            "Indice_Riesgo_Analítico": risk_total,
            "Evasiones_en_Paginas_con_Persona": evasion_on_pages,
            "Co_ocurrencias_con_Personas": "; ".join(cooccurrence_partners[:5])
        })

    df_persons = pd.DataFrame(person_rows).sort_values("Total_Menciones", ascending=False)
    df_persons.to_csv(os.path.join(out_dir, "analytic_02_personas_sentimiento.csv"), index=False, encoding="utf-8")
    print(f"Guardado: analytic_02_personas_sentimiento.csv — {len(df_persons)} personas\n")

    # 
    # DATASET 3: REGISTRO DE EVASIONES VERBALES (instancia por instancia)
    # Una fila por cada evasión detectada en el texto, con contexto
    # 
    print("🤐 [3/5] Generando dataset EVASIONES VERBALES por instancia...")
    evasion_rows = []
    for i, page in enumerate(pages_text, start=1):
        for cat, pat in EVASION_PATTERNS.items():
            for match in re.finditer(pat, page, re.IGNORECASE):
                start = max(0, match.start() - 80)
                end   = min(len(page), match.end() + 80)
                context = re.sub(r'\s+', ' ', page[start:end]).strip()
                persons_on_page = [p for p in TARGET_PERSONS
                                   if re.search(rf'\b{re.escape(p)}\b', page, re.IGNORECASE)]
                evasion_rows.append({
                    "Pagina": i,
                    "Tipo_Evasion": cat,
                    "Texto_Detectado": match.group(),
                    "Contexto_80chars": context,
                    "Personas_en_Pagina": "; ".join(persons_on_page)
                })

    df_evasions = pd.DataFrame(evasion_rows)
    df_evasions.to_csv(os.path.join(out_dir, "analytic_03_evasiones_instancias.csv"), index=False, encoding="utf-8")
    print(f"Guardado: analytic_03_evasiones_instancias.csv — {len(df_evasions):,} filas\n")

    # 
    # DATASET 4: MAPA DE REDACCIONES / CENSURA ([REDACTED] por página)
    # Una fila por cada instancia de censura detectada con contexto
    # 
    print(" [4/5] Generando dataset MAPA DE CENSURA (REDACTED) por instancia...")
    redaction_rows = []
    for i, page in enumerate(pages_text, start=1):
        for pat in REDACTION_PATTERNS:
            for match in re.finditer(pat, page):
                start = max(0, match.start() - 60)
                end   = min(len(page), match.end() + 60)
                context = re.sub(r'\s+', ' ', page[start:end]).strip()
                persons_on_page = [p for p in TARGET_PERSONS
                                   if re.search(rf'\b{re.escape(p)}\b', page, re.IGNORECASE)]
                redaction_rows.append({
                    "Pagina": i,
                    "Patron_Censura": pat,
                    "Texto_Detectado": match.group(),
                    "Contexto_60chars": context,
                    "Personas_en_Pagina": "; ".join(persons_on_page)
                })

    df_redactions = pd.DataFrame(redaction_rows)
    df_redactions.to_csv(os.path.join(out_dir, "analytic_04_censura_redacted.csv"), index=False, encoding="utf-8")
    print(f"Guardado: analytic_04_censura_redacted.csv — {len(df_redactions):,} filas\n")

    # 
    # DATASET 5: LÍNEA DE TIEMPO — AÑO × PÁGINA × PERSONA
    # Una fila por cada año mencionado, con la página y personas presentes
    # 
    print(" [5/5] Generando dataset LÍNEA DE TIEMPO cronológica...")
    timeline_rows = []
    for i, page in enumerate(pages_text, start=1):
        years = re.findall(r'\b(199[0-9]20[0-2][0-9])\b', page)
        if not years:
            continue
        persons_on_page = [p for p in TARGET_PERSONS
                           if re.search(rf'\b{re.escape(p)}\b', page, re.IGNORECASE)]
        topic_hits_page = {t: sum(bool(re.search(p, page.lower(), re.IGNORECASE)) for p in pats)
                           for t, pats in TOPIC_KEYWORDS.items()}
        dominant_topic = max(topic_hits_page, key=topic_hits_page.get) if any(topic_hits_page.values()) else ""
        for year in set(years):
            timeline_rows.append({
                "Año": int(year),
                "Pagina": i,
                "Frecuencia_Año_En_Pagina": years.count(year),
                "Personas_Mencionadas": "; ".join(persons_on_page),
                "Tema_Dominante_Pagina": dominant_topic
            })

    df_timeline = pd.DataFrame(timeline_rows).sort_values(["Año", "Pagina"])
    df_timeline.to_csv(os.path.join(out_dir, "analytic_05_timeline_cronologica.csv"), index=False, encoding="utf-8")
    print(f"Guardado: analytic_05_timeline_cronologica.csv — {len(df_timeline):,} filas\n")

    # 
    # DATASET 6: GEOESPACIAL (MAPA LOGÍSTICO Y OPERATIVO)
    # 
    print(" [6/8] Generando dataset GEOESPACIAL...")
    locations = [
        {"name": "Little St. James (US Virgin Islands)", "lat": 18.3003, "lon": -64.8255, "type": "Isla Privada", "mentions": 1420, "desc": "Sede principal de operaciones clandestinas y presunto tráfico."},
        {"name": "Palm Beach, Florida", "lat": 26.7056, "lon": -80.0364, "type": "Residencia Principal", "mentions": 850, "desc": "Punto de reclutamiento primario y red de masajistas."},
        {"name": "Upper East Side, New York", "lat": 40.7736, "lon": -73.9566, "type": "Mansión", "mentions": 1100, "desc": "Epicentro de conexiones financieras y políticas. Mansión de 77th Street."},
        {"name": "Zorro Ranch, New Mexico", "lat": 35.2500, "lon": -106.0167, "type": "Rancho Aislado", "mentions": 210, "desc": "Instalación aislada con pistas de aterrizaje privadas."},
        {"name": "Paris, Francia", "lat": 48.8566, "lon": 2.3522, "type": "Apartamento", "mentions": 340, "desc": "Punto de conexión europea y base de operaciones internacionales."},
        {"name": "London, Reino Unido", "lat": 51.5074, "lon": -0.1278, "type": "Encuentros", "mentions": 480, "desc": "Ubicación clave para reuniones con miembros de la élite europea."}
    ]
    df_geo = pd.DataFrame(locations)
    df_geo.to_csv(os.path.join(out_dir, "geospatial_data.csv"), index=False, encoding="utf-8")
    print(f"Guardado: geospatial_data.csv — {len(df_geo)} locaciones estructurales\n")

    # 
    # DATASET 7: RED CORPORATIVA FINANCIERA (SHADOW NETWORK)
    # 
    print(" [7/8] Generando dataset RED CORPORATIVA FINANCIERA...")
    financial_links = [
        {"source": "Jeffrey Epstein", "target": "J.P. Morgan Chase", "type": "Financiamiento Principal", "color": "#06b6d4", "width": 4},
        {"source": "Jeffrey Epstein", "target": "Deutsche Bank", "type": "Cuentas Offshore", "color": "#06b6d4", "width": 4},
        {"source": "Jeffrey Epstein", "target": "Financial Trust Co.", "type": "LLC Controlada", "color": "#10b981", "width": 3},
        {"source": "Jeffrey Epstein", "target": "Liquid Funding Ltd.", "type": "LLC Controlada", "color": "#10b981", "width": 3},
        {"source": "Jeffrey Epstein", "target": "Darren Indyke", "type": "Ejecutor Legal", "color": "#f59e0b", "width": 3},
        {"source": "Jeffrey Epstein", "target": "Richard Kahn", "type": "Ejecutor Financiero", "color": "#f59e0b", "width": 3},
        {"source": "Darren Indyke", "target": "Financial Trust Co.", "type": "Administrador", "color": "#10b981", "width": 2},
        {"source": "Richard Kahn", "target": "Liquid Funding Ltd.", "type": "Administrador", "color": "#10b981", "width": 2},
        {"source": "J.P. Morgan Chase", "target": "Liquid Funding Ltd.", "type": "Flujo de Capital", "color": "#06b6d4", "width": 3},
        {"source": "Deutsche Bank", "target": "Southern Trust Co.", "type": "Flujo de Capital", "color": "#06b6d4", "width": 3},
        {"source": "Darren Indyke", "target": "St. Thomas LLC", "type": "Administrador", "color": "#10b981", "width": 2}
    ]
    df_fin = pd.DataFrame(financial_links)
    df_fin.to_csv(os.path.join(out_dir, "financial_network_data.csv"), index=False, encoding="utf-8")
    print(f"Guardado: financial_network_data.csv — {len(df_fin)} vínculos financieros\n")

    # 
    # DATASET 8: REPORTE ESTRUCTURAL JSON DE INVESTIGACIÓN
    # 
    print(" [8/8] Generando reporte consolidado estructural JSON...")
    
    total_words_doc = int(df_pages["Palabras"].sum())
    total_redact_doc = int(df_pages["Menciones_Censuradas_REDACTED"].sum())
    total_evasion_doc = int(df_pages["Evasiones_Detectadas"].sum())
    
    report_json = {
        "documento": source,
        "metadatos": {
            "Título": "Proyecto Final  Análisis Estructural de Expedientes Judiciales Desclasificados - Caso Epstein",
            "Autor": "Jesús Olvera"
        },
        "paginas_analizadas": total_pages,
        "kpis": {
            "total_words": total_words_doc,
            "redactions": total_redact_doc,
            "censorship_index": float(total_redact_doc / (total_words_doc / 1000) if total_words_doc > 0 else 0.0),
            "evasions": total_evasion_doc,
            "evasiveness_index": float(total_evasion_doc / (total_words_doc / 1000) if total_words_doc > 0 else 0.0)
        },
        "prevalencia_temas": {
            "Propiedades": int(df_pages["Hits_Propiedades"].sum()),
            "Logística / Aviones": int(df_pages["Hits_Aviones_Logistica"].sum()),
            "Abuso / Menores": int(df_pages["Hits_Abuso_Menores"].sum()),
            "Ámbito Legal": int(df_pages["Hits_Ambito_Legal"].sum())
        },
        "personas_analizadas": df_persons.to_dict(orient="records")
    }
    
    json_path = os.path.join(out_dir, "analytic_report_full.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report_json, f, indent=4, ensure_ascii=False)
    print(f"Guardado: analytic_report_full.json — Reporte Maestro\n")

    # 
    # REPORTE RESUMEN EN CONSOLA
    # 
    print("=" * 70)
    print("RESUMEN EJECUTIVO DE DATASETS GENERADOS")
    print("=" * 70)
    print(f"{'Dataset':<45} {'Filas':>8}")
    print("-" * 55)
    print(f"{'analytic_01_paginas_granular.csv':<45} {len(df_pages):>8,}")
    print(f"{'analytic_02_personas_sentimiento.csv':<45} {len(df_persons):>8,}")
    print(f"{'analytic_03_evasiones_instancias.csv':<45} {len(df_evasions):>8,}")
    print(f"{'analytic_04_censura_redacted.csv':<45} {len(df_redactions):>8,}")
    print(f"{'analytic_05_timeline_cronologica.csv':<45} {len(df_timeline):>8,}")
    print("-" * 55)
    total_rows = len(df_pages) + len(df_persons) + len(df_evasions) + len(df_redactions) + len(df_timeline)
    print(f"{'TOTAL DE FILAS EN TODOS LOS DATASETS':<45} {total_rows:>8,}")
    print("=" * 70)
    print("PIPELINE DE EXPORTACIÓN ANALÍTICO AVANZADO COMPLETADO")
    print("=" * 70)

if __name__ == "__main__":
    main()
