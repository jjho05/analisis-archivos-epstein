import matplotlib
matplotlib.use('Agg')

from shiny import App, render, ui, reactive
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os
from extractor import PDFExtractorEngine, TARGET_PERSONS
import logic
import providers
from report_generator import (
    generate_report,
    generate_audit_report,
    generate_dashboard_report,
    generate_network_report,
    generate_geo_report,
)
from datetime import datetime

# --- ESTILADO CSS PREMIUM (Cyber-Noir & High-Fidelity Style) ---
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;700&display=swap');

/* --- Estilos Globales --- */
:root, body, html {
    --bs-table-bg: #120e20 !important;
    --bs-table-striped-bg: #0e0a17 !important;
    --bs-table-hover-bg: #1a152e !important;
    --bs-table-color: #ebdff5 !important;
    --bs-table-border-color: rgba(255, 255, 255, 0.1) !important;
    --bs-pre-bg: #0e0a17 !important;
    --bs-pre-color: #ebdff5 !important;
}

body {
    background-color: #0b090f !important;
    color: #e5e0eb !important;
    font-family: 'Outfit', sans-serif;
    font-size: 1rem;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Space Grotesk', sans-serif;
    color: #ffffff;
    font-weight: 700;
}

/* Sidebar Custom Styling */
.sidebar {
    background-color: #0e0a17 !important;
    border-right: 1px solid rgba(168, 85, 247, 0.25) !important;
}

.control-label, 
label, 
.form-label, 
.form-check-label, 
.shiny-input-container label {
    color: #c084fc !important;
    font-weight: 700;
    margin-bottom: 0.4rem;
    font-size: 0.82rem;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

.form-control, 
select,
input[type="number"], 
input[type="text"], 
textarea {
    background-color: #161224 !important;
    color: #ffffff !important;
    border: 1px solid rgba(168, 85, 247, 0.3) !important;
    border-radius: 8px !important;
    padding: 0.45rem 0.6rem !important;
    font-size: 0.9rem;
}

.form-control:focus, 
select:focus,
input[type="number"]:focus,
textarea:focus {
    border-color: #d8b4fe !important;
    box-shadow: 0 0 8px rgba(216, 180, 254, 0.25) !important;
    outline: none !important;
}

.control-card {
    background: linear-gradient(135deg, rgba(26, 19, 44, 0.6) 0%, rgba(15, 10, 27, 0.85) 100%);
    border: 1px solid rgba(168, 85, 247, 0.35);
    border-radius: 14px;
    padding: 1.2rem 1.8rem;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
    margin-bottom: 1.8rem;
}

.kpi-row {
    margin-bottom: 1.5rem;
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.kpi-wrapper {
    flex: 1 1 15%;
    min-width: 145px;
}

.kpi-card {
    background: linear-gradient(135deg, rgba(30, 22, 53, 0.5) 0%, rgba(15, 11, 27, 0.75) 100%);
    border: 1px solid rgba(168, 85, 247, 0.28);
    border-radius: 12px;
    padding: 0.9rem;
    text-align: center;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    transition: all 0.3s ease;
    height: 100%;
}

.kpi-card:hover {
    border-color: #a855f7;
    background: rgba(168, 85, 247, 0.05);
}

.kpi-title {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #c084fc;
    margin-bottom: 0.2rem;
    font-weight: 600;
}

.kpi-value {
    font-size: 1.35rem;
    font-weight: 700;
    color: #ffffff;
}

/* Sephora Explanation Box Styling but Adapted to Analytic dark theme */
.explanation-box {
    background: rgba(15, 11, 27, 0.85);
    border-top: 1px solid rgba(168, 85, 247, 0.22);
    padding: 15px 20px;
    border-radius: 0 0 12px 12px;
    font-size: 0.86rem;
    color: #ebdff5;
    line-height: 1.6;
}

.explanation-title {
    font-weight: 700;
    color: #a855f7;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.88rem;
    letter-spacing: 0.5px;
}

/* Cards Premium */
.card {
    background-color: #120e1d !important;
    border: 1px solid rgba(168, 85, 247, 0.22) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
    margin-bottom: 20px;
}

.card-header {
    background-color: rgba(168, 85, 247, 0.07) !important;
    border-bottom: 1px solid rgba(168, 85, 247, 0.22) !important;
    color: #ffffff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 12px 20px !important;
}

.btn-primary {
    background: linear-gradient(135deg, #a855f7 0%, #701a75 100%) !important;
    border: 1px solid rgba(216, 180, 254, 0.4) !important;
    padding: 0.6rem 1.2rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3) !important;
    transition: all 0.2s ease !important;
}

.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(168, 85, 247, 0.45) !important;
    border-color: #d8b4fe !important;
}

.btn-download {
    background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
    border: 1px solid rgba(6, 182, 212, 0.3) !important;
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.25) !important;
}

.btn-download:hover {
    box-shadow: 0 6px 16px rgba(6, 182, 212, 0.35) !important;
    border-color: #22d3ee !important;
}

textarea.form-control {
    background-color: #0b0812 !important;
    color: #e2daf0 !important;
    font-family: 'Courier New', Courier, monospace !important;
    font-size: 0.88rem !important;
    line-height: 1.45 !important;
    border: 1px solid rgba(168, 85, 247, 0.22) !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    resize: none !important;
}

.meta-container {
    background: rgba(255, 255, 255, 0.012);
    border: 1px solid rgba(168, 85, 247, 0.15);
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    margin-top: 0.8rem;
}

.meta-item-title {
    font-size: 0.75rem;
    color: #c084fc;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.meta-item-value {
    color: #ffffff;
    font-size: 0.85rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Tab Overrides */
.nav-tabs {
    border-bottom: 1px solid rgba(168, 85, 247, 0.25) !important;
    gap: 8px;
    margin-bottom: 20px;
}
.nav-link {
    color: #bfaec2 !important;
    border: 1px solid transparent !important;
    border-radius: 8px 8px 0 0 !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    padding: 8px 16px !important;
    transition: all 0.2s ease !important;
}
.nav-link.active {
    background-color: rgba(168, 85, 247, 0.12) !important;
    border: 1px solid rgba(168, 85, 247, 0.35) !important;
    border-bottom: 1px solid #0b090f !important;
    color: #ffffff !important;
    box-shadow: 0 -4px 12px rgba(168, 85, 247, 0.08) !important;
}
.nav-link:hover:not(.active) {
    color: #ffffff !important;
    background-color: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(168, 85, 247, 0.15) !important;
}

/* Chat Styling */
.shiny-chat {
    flex-grow: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
}

.shiny-chat-messages {
    flex-grow: 1 !important;
    overflow-y: auto !important;
    padding-bottom: 140px !important;
    max-height: calc(100vh - 200px) !important;
}

/* Input del chat fijado al fondo — selector amplio para compatibilidad con Shiny */
.shiny-chat .textarea-container,
.shiny-chat form,
.shiny-chat [class*="input"],
.shiny-chat > div:last-of-type {
    position: sticky !important;
    bottom: 0 !important;
    background: #0b090f !important;
    z-index: 20 !important;
    padding: 8px 0 4px !important;
    border-top: 1px solid rgba(168, 85, 247, 0.18) !important;
    margin-top: 0 !important;
}

.chat-suggestion-box:hover {
    border-color: #a855f7 !important;
    background: rgba(168, 85, 247, 0.05) !important;
    box-shadow: 0 4px 15px rgba(168, 85, 247, 0.15) !important;
    transform: translateY(-1px);
}

/* --- Eliminación Absoluta de la Barra Blanca Superior --- */
html, body, .container-fluid, main, .app-container {
    background-color: #0b090f !important;
    margin-top: 0 !important;
    padding-top: 0 !important;
    border-top: none !important;
}

header, .navbar, .app-header, .bslib-page-header, .bslib-navbar, .bslib-page-navbar {
    display: none !important;
}

.bslib-sidebar-layout {
    border: none !important;
    box-shadow: none !important;
}

/* --- Estilado Premium de Casillas de Selección (Checkboxes) --- */
.shiny-options-group {
    display: flex !important;
    flex-direction: column !important;
    gap: 8px !important;
    max-height: 250px !important;
    overflow-y: auto !important;
    padding-right: 8px !important;
    margin-bottom: 15px !important;
}

/* Scrollbar personalizada con estilo neón cyberpunk */
.shiny-options-group::-webkit-scrollbar {
    width: 6px !important;
}
.shiny-options-group::-webkit-scrollbar-track {
    background: rgba(25, 18, 44, 0.4) !important;
    border-radius: 4px !important;
}
.shiny-options-group::-webkit-scrollbar-thumb {
    background: rgba(168, 85, 247, 0.35) !important;
    border-radius: 4px !important;
    border: 1px solid rgba(168, 85, 247, 0.15) !important;
}
.shiny-options-group::-webkit-scrollbar-thumb:hover {
    background: rgba(168, 85, 247, 0.6) !important;
}

/* Contenedor del item checkbox */
.shiny-options-group .form-check {
    background: rgba(15, 10, 27, 0.85) !important;
    border: 1px solid rgba(168, 85, 247, 0.25) !important;
    border-radius: 8px !important;
    padding: 8px 12px 8px 32px !important;
    margin: 0 !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    position: relative !important;
}

.shiny-options-group .form-check:hover {
    background: rgba(168, 85, 247, 0.08) !important;
    border-color: rgba(168, 85, 247, 0.5) !important;
    box-shadow: 0 0 10px rgba(168, 85, 247, 0.12) !important;
    transform: translateX(2px);
}

/* Checkbox circular/rounded neón */
.shiny-options-group .form-check-input {
    background-color: #161224 !important;
    border: 1px solid rgba(168, 85, 247, 0.45) !important;
    width: 16px !important;
    height: 16px !important;
    border-radius: 4px !important;
    position: absolute !important;
    left: 10px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

.shiny-options-group .form-check-input:checked {
    background-color: #a855f7 !important;
    border-color: #d8b4fe !important;
    box-shadow: 0 0 8px rgba(168, 85, 247, 0.6) !important;
}

.shiny-options-group .form-check-input:focus {
    box-shadow: 0 0 8px rgba(168, 85, 247, 0.4) !important;
    border-color: #a855f7 !important;
}

/* Etiqueta del checkbox */
.shiny-options-group .form-check-label {
    color: #e5e0eb !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-transform: none !important;
    letter-spacing: 0px !important;
    cursor: pointer !important;
    padding-left: 0 !important;
    user-select: none !important;
}

/* --- Estilo de Olvera AI Chat (Visibilidad de Letras) --- */
/* Forzar variables CSS heredables en los componentes web */
.shiny-chat, 
shiny-chat-messages,
.shiny-chat-messages,
.shiny-chat-message,
.message-body,
.message-content,
.markdown-container,
[id="chat"] {
    --chat-message-assistant-color: #e5e0eb !important;
    --chat-message-user-color: #ffffff !important;
    --chat-message-assistant-bg: rgba(168, 85, 247, 0.08) !important;
    --chat-message-user-bg: rgba(6, 182, 212, 0.08) !important;
    --bs-body-color: #e5e0eb !important;
    --bs-heading-color: #ffffff !important;
    color: #e5e0eb !important;
}

/* Reglas universales y de etiquetas específicas para penetrar selectores */
.shiny-chat *,
.shiny-chat p,
.shiny-chat li,
.shiny-chat span,
.shiny-chat div,
.shiny-chat strong,
.shiny-chat em,
.shiny-chat-messages *,
.shiny-chat-messages p,
.shiny-chat-messages li,
.shiny-chat-messages span,
.shiny-chat-messages div,
.shiny-chat-message-body *,
.shiny-chat-message-body p,
.shiny-chat-message-body li,
.shiny-chat-message-body span,
.message-body *,
.message-body p,
.message-body li,
.message-body span,
.message-content *,
.message-content p,
.message-content li,
.message-content span,
.markdown-container *,
.markdown-container p,
.markdown-container li,
.markdown-container span {
    color: #ebdff5 !important; /* Forzar el color lavanda legible en todo el contenido */
}

/* Habilitar colores especiales para resaltar títulos y negritas */
.shiny-chat strong,
.shiny-chat-messages strong,
.markdown-container strong,
.shiny-chat-message strong,
.shiny-chat-message-assistant strong,
.shiny-chat-message-user strong {
    color: #ffffff !important;
    font-weight: 700 !important;
}

.shiny-chat h1, .shiny-chat h2, .shiny-chat h3, .shiny-chat h4,
.shiny-chat-messages h1, .shiny-chat-messages h2, .shiny-chat-messages h3,
.markdown-container h1, .markdown-container h2, .markdown-container h3,
.shiny-chat-message h1, .shiny-chat-message h2, .shiny-chat-message h3 {
    color: #ffffff !important;
    font-weight: 800 !important;
    margin-top: 1rem !important;
    margin-bottom: 0.5rem !important;
}

/* Bordes y fondos de mensajes en el chat */
.shiny-chat-message-assistant,
shiny-chat-message[role="assistant"] {
    background-color: rgba(168, 85, 247, 0.08) !important;
    border: 1px solid rgba(168, 85, 247, 0.22) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

.shiny-chat-message-user,
shiny-chat-message[role="user"] {
    background-color: rgba(6, 182, 212, 0.08) !important;
    border: 1px solid rgba(6, 182, 212, 0.22) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

/*  Estilos de Tablas Globales y de Chat (Modo Oscuro)  */
table, 
.table,
.shiny-chat table,
.shiny-chat-messages table,
.shiny-chat-message-body table {
    width: 100% !important;
    border-collapse: collapse !important;
    margin: 14px 0 !important;
    font-size: 0.84rem !important;
    background-color: #0e0a17 !important;
    background: #0e0a17 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
}

th,
.table th,
.shiny-chat th,
.shiny-chat-messages th {
    background-color: #1a152e !important;
    background: #1a152e !important;
    color: #ffffff !important;
    padding: 10px 14px !important;
    text-align: left !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
}

td,
.table td,
.shiny-chat td,
.shiny-chat-messages td {
    background-color: #120e20 !important;
    background: #120e20 !important;
    color: #ebdff5 !important;
    padding: 8px 14px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    vertical-align: top !important;
}

tr:nth-child(even) td,
.table tr:nth-child(even) td {
    background-color: #0e0a17 !important;
    background: #0e0a17 !important;
}

tr:hover td,
.table tr:hover td {
    background-color: #1a152e !important;
    background: #1a152e !important;
}

/*  Estilos Globales de Código (pre / code)  */
pre, 
code, 
.code-block, 
.markdown-code-block,
pre code {
    background-color: #0e0a17 !important;
    background: #0e0a17 !important;
    color: #ebdff5 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    padding: 12px !important;
    border-radius: 8px !important;
    font-family: 'Courier New', Courier, monospace !important;
}
"""

# Obtener lista de PDFs disponibles en la carpeta de datasets
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "01 Datasets Usados"))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

pdf_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".pdf")]
if not pdf_files:
    pdf_files = ["Ningún archivo en la carpeta de datasets"]

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.div(
            ui.h3("Proyecto Final: Analisis caso epstein", style="color: #ffffff; font-family: 'Space Grotesk', sans-serif; font-weight: 800; font-size: 0.95rem; letter-spacing: 1px; text-align: center; margin-top: 25px; border-bottom: 2px solid rgba(168, 85, 247, 0.35); padding-bottom: 15px; margin-bottom: 25px;"),
        ),
        
        ui.div(
            ui.p("AUDITORÍA ANALÍTICO:", style="font-weight: bold; color: #ffffff; font-size: 0.85em; letter-spacing: 0.5px;"),
            ui.p("Este sistema realiza minería de texto y análisis de co-ocurrencia sobre testimonios judiciales desclasificados. Emplea procesamiento de lenguaje natural y visualizaciones de grado de investigación para mapear redes de interés en el caso Epstein.", style="font-size: 0.82em; color: #ebdff5; line-height: 1.5;"),
            style="background: rgba(168, 85, 247, 0.05); padding: 15px; border-radius: 8px; border: 1px solid rgba(168, 85, 247, 0.2); margin-bottom: 20px;"
        ),
        
        # PANEL DE FILTROS INTERACTIVOS SEPHORA-STYLE
        ui.div(
            ui.div("FILTROS INTERACTIVOS", style="font-weight: 800; color: #a855f7; font-size: 0.8rem; letter-spacing: 1px; margin-bottom: 15px; text-transform: uppercase; border-left: 3px solid #a855f7; padding-left: 8px;"),
            
            # Filtro por Persona de Interés (Checkbox Group Sephora-Style)
            ui.input_checkbox_group(
                "selected_persons", 
                "Personas Clave:", 
                choices=TARGET_PERSONS, 
                selected=TARGET_PERSONS # Activar todas por defecto
            ),
            
            # Slider para Menciones Mínimas
            ui.input_slider(
                "min_mentions", 
                "Menciones Mínimas:", 
                min=1, 
                max=50, 
                value=1,
                step=1
            ),
            
            # Select para Radar de Tópicos
            ui.input_select(
                "dominant_topic", 
                "Resaltar Tópico:", 
                choices=["Todos", "Propiedades / Lugares", "Logística / Aviones", "Abuso / Menores", "Ámbito Legal / Juicio"], 
                selected="Todos"
            ),
            style="background: rgba(22, 18, 36, 0.7); border: 1px solid rgba(168, 85, 247, 0.25); padding: 20px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.45); margin-bottom: 20px;"
        ),
        width=290,
        style="padding: 25px;"
    ),

    ui.div(
        # Rayas de Estilado Neon Purple y Dark (Stripes de Sephora adaptadas)
        ui.div(style="height: 6px; background: repeating-linear-gradient(90deg, #a855f7, #a855f7 15px, #0b090f 15px, #0b090f 30px); width: 100%; border-radius: 4px 4px 0 0; margin-bottom: 20px;"),
    ),

    ui.navset_tab(
        # TAB 1: Dashboard Analítico
        ui.nav_panel(
            "Dashboard Analítico",
            ui.div(
                ui.output_ui("analytic_dashboard_ui")
            )
        ),
        
        # TAB 2: Explorador de Transcripciones y Cronología
        ui.nav_panel(
            "Explorador de Transcripción",
            ui.div(
                ui.output_ui("document_explorer_ui")
            )
        ),
        
        # TAB 3: Buscador Semántico (RAG Local)
        ui.nav_panel(
            "Búsqueda Semántica",
            ui.div(
                ui.h3("Buscador Inteligente (Por Contexto)", style="color:#ffffff; margin-bottom:15px; font-weight:700;"),
                ui.p("A diferencia de un buscador normal que requiere la palabra exacta, este motor utiliza un algoritmo matemático para entender la intención y el significado de tu búsqueda. Esto te permite encontrar evidencia aunque los testigos hayan usado términos distintos para referirse a lo mismo.", style="color:#bfaec2; margin-bottom:25px;"),
                ui.layout_columns(
                    ui.input_text("search_query", " ¿Qué intentas encontrar en el expediente? (Ej. Encuentros en la isla, logística de vuelos secretos):", width="100%"),
                    ui.input_action_button("search_btn", "Buscar", class_="btn-primary", style="margin-top:24px; background:#a855f7; border:none; height:40px;"),
                    ui.panel_conditional(
                        "input.search_btn > 0",
                        ui.download_button("download_report", "Descargar Reporte de Evidencia", class_="btn-primary", style="margin-top:24px; background:#06b6d4; border:none; height:40px; font-weight:bold; width:100%;")
                    ),
                    col_widths=[8, 2, 2]
                ),
                ui.hr(style="border-color: rgba(168, 85, 247, 0.2); margin: 1.5rem 0;"),
                ui.output_ui("search_results_ui"),
                style="padding: 20px;"
            )
        ),
        
        # TAB 4: Auditor de Contradicciones (Agente Lógico)
        ui.nav_panel(
            "Auditor de Contradicciones",
            ui.div(
                ui.h3("Agente Autónomo Detector de Contradicciones", style="color:#ffffff; margin-bottom:15px; font-weight:700;"),
                ui.p("Inicia un proceso lógico donde el LLM escanea los testimonios clave (ej. Maxwell y Giuffre) buscando discrepancias cruzadas o evasiones intencionales detectadas en las transcripciones.", style="color:#bfaec2; margin-bottom:25px;"),
                ui.layout_columns(
                    ui.input_select("audit_focus", "Enfoque de Auditoría:", ["General", "Contradicciones de Abuso", "Rutas y Logística (Aviones)", "Discrepancias Financieras"]),
                    ui.input_select("audit_target", "Persona Objetivo:", ["Todos", "Jeffrey Epstein", "Ghislaine Maxwell", "Virginia Giuffre", "Prince Andrew"]),
                    ui.input_select("audit_strictness", "Nivel de Severidad:", ["Estándar", "Implacable (Crítico)", "Leve (Solo hechos obvios)"]),
                    col_widths=[4, 4, 4]
                ),
                ui.input_action_button("audit_btn", "Iniciar Auditoría Profunda", class_="btn-danger", style="background:#f43f5e; border:none; padding:10px 20px; font-weight:bold; width: 100%; margin-top: 15px;"),
                ui.hr(style="border-color: rgba(168, 85, 247, 0.2); margin: 1.5rem 0;"),
                ui.output_ui("contradictions_results_ui"),
                ui.panel_conditional(
                    "input.audit_btn > 0",
                    ui.download_button("download_audit_report", "Descargar Reporte de Auditoría", class_="btn-primary", style="margin-top:16px; background:#f43f5e; border:none; height:40px; font-weight:bold; width:100%;")
                ),
                style="padding: 20px;"
            )
        ),
        
        # TAB 5: Inteligencia Geoespacial
        ui.nav_panel(
            "Mapa Geoespacial",
            ui.div(
                ui.h3("Red Logística Internacional (Footprint)", style="color:#ffffff; margin-bottom:15px; font-weight:700;"),
                ui.p("Visualización de coordenadas clave extraídas del expediente. Identifica las rutas de vuelo, islas privadas y bases de operaciones utilizadas en la red.", style="color:#bfaec2; margin-bottom:25px;"),
                ui.layout_columns(
                    ui.output_ui("geospatial_map_ui"),
                    ui.div(
                        ui.h4("‍ Análisis de Rutas", style="color:#06b6d4; font-weight:bold; margin-bottom:15px;"),
                        ui.markdown("""
**Little St. James (USVI):** Identificada en los registros de vuelo como el destino principal y punto ciego legal.
                        
**Palm Beach / NY:** Nodos primarios de operación y reclutamiento según las bitácoras del *Lolita Express*.
                        
**Zorro Ranch (NM):** Instalación aislada de alta seguridad con infraestructura de aterrizaje privada.
                        
**Conexiones Transatlánticas:** Los saltos entre NY, París y Londres documentan el alcance internacional de las operaciones de tráfico con miembros de la élite europea.
                        """),
                        ui.download_button("download_geo_report", "Descargar Reporte Geoespacial", class_="btn-primary", style="margin-top:16px; background:#06b6d4; border:none; height:40px; font-weight:bold; width:100%;"),
                        style="background:rgba(15, 11, 27, 0.85); padding:20px; border-radius:12px; border:1px solid rgba(6,182,212,0.3); color:#e5e0eb; height:100%;"
                    ),
                    col_widths=[8, 4]
                ),
                style="padding: 20px;"
            )
        ),
        
        # TAB 6: Mapeo Financiero (Shadow Network)
        ui.nav_panel(
            "Red Financiera",
            ui.div(
                ui.h3("Shadow Network (Grafo Corporativo)", style="color:#ffffff; margin-bottom:15px; font-weight:700;"),
                ui.p("Grafo interactivo de relaciones financieras, empresas fachada (LLCs) y actores clave que facilitaron el flujo de dinero en la organización.", style="color:#bfaec2; margin-bottom:25px;"),
                ui.layout_columns(
                    ui.output_ui("shadow_network_ui"),
                    ui.div(
                        ui.h4("Anatomía Financiera", style="color:#10b981; font-weight:bold; margin-bottom:15px;"),
                        ui.markdown("""
**Cuentas Ciegas (Tier 1):**
J.P. Morgan y Deutsche Bank proveyeron la infraestructura para flujos masivos de liquidez.
                        
**El Escudo Corporativo (Tier 2):**
Entidades offshore como *Financial Trust Co.* y *Liquid Funding Ltd.* operando bajo la laxa jurisdicción de las Islas Vírgenes para mover capital sin trazabilidad directa.
                        
**Ejecutores (Tier 3):**
Darren Indyke (Abogado) y Richard Kahn (Contador). Fueron los arquitectos detrás de la creación de las LLCs (Sociedades de Responsabilidad Limitada) para adquirir propiedades e inyectar fondos.
                        """),
                        ui.download_button("download_network_report", "Descargar Reporte de Red Financiera", class_="btn-primary", style="margin-top:16px; background:#a855f7; border:none; height:40px; font-weight:bold; width:100%;"),
                        style="background:rgba(15, 11, 27, 0.85); padding:20px; border-radius:12px; border:1px solid rgba(16,185,129,0.3); color:#e5e0eb; height:100%;"
                    ),
                    col_widths=[9, 3]
                ),
                style="padding: 20px;"
            )
        ),
        
        # TAB 7: Co-ocurrencia Social
        ui.nav_panel(
            "Co-ocurrencia Social",
            ui.div(
                ui.h3("Red de Co-ocurrencia en el Expediente", style="color:#ffffff; margin-bottom:15px; font-weight:700;"),
                ui.p("Este módulo identifica qué actores de alto perfil aparecen mencionados simultáneamente en las mismas páginas del expediente, evidenciando conexiones documentadas.", style="color:#bfaec2; margin-bottom:25px;"),
                ui.layout_columns(
                    ui.output_ui("co_occur_chart_ui"),
                    ui.div(
                        ui.h4("Lectura de Co-ocurrencia", style="color:#c084fc; font-weight:bold; margin-bottom:15px;"),
                        ui.markdown("""
**¿Qué significa esto?**
Esta red no asume culpabilidad por sí sola, pero **mapea la proximidad en los testimonios**. 
Si dos nodos (personas) están conectados, significa que sus nombres fueron documentados en el mismo contexto o evento (por ejemplo, los mismos registros de vuelo o testimonios cruzados).

**Nodos (Personas):** El tamaño representa su peso total en los documentos.
**Aristas (Líneas):** El grosor indica la frecuencia de aparición simultánea (co-ocurrencia).

**Código de Colores:**
- **Rojo:** Núcleo de la investigación (Epstein, Maxwell).
- **Celeste:** Víctimas, testigos y denunciantes clave (Virginia Giuffre, etc.).
- **Dorado:** Políticos y figuras públicas de alto perfil (Clinton, Trump, etc.).
- **Morado:** Prominentes asociados e individuos de interés legal/social.
- **Gris:** Otras entidades o vínculos secundarios.
                        """),
                        style="background:rgba(15, 11, 27, 0.85); padding:20px; border-radius:12px; border:1px solid rgba(192,132,252,0.3); color:#e5e0eb; height:100%;"
                    ),
                    col_widths=[8, 4]
                ),
                ui.output_ui("co_occur_metrics_ui"),
                style="padding: 20px;"
            )
        ),
        
        # TAB 8: Olvera AI (AI Chatbot)
        ui.nav_panel(
            "Olvera AI",
            ui.div(
                ui.row(
                    ui.column(
                        12,
                        ui.div(
                            ui.output_ui("welcome_ui"),
                            style="margin-bottom: 20px; flex-shrink: 0;"
                        )
                    )
                ),
                ui.div(
                    ui.chat_ui("chat"),
                    style="flex-grow: 1; min-height: 0; display: flex; flex-direction: column;"
                ),
                ui.div(
                    ui.output_ui("chat_toolbar_ui"),
                    style="flex-shrink: 0; margin-top: 15px;"
                ),
                style="padding: 20px; max-width: 900px; margin: 0 auto; height: 80vh; display: flex; flex-direction: column;"
            )
        ),
        id="main_nav_tabs"
    ),
    
    ui.tags.head(
        ui.tags.style(CUSTOM_CSS),
        ui.tags.script("""
            function injectStylesRecursively(root) {
                if (!root) return;
                
                // Si el elemento tiene Shadow DOM
                if (root.shadowRoot) {
                    const shadow = root.shadowRoot;
                    if (!shadow.querySelector('#shadow-table-styles')) {
                        const style = document.createElement('style');
                        style.id = 'shadow-table-styles';
                        style.textContent = `
                            /* Tablas dentro del Shadow DOM */
                            table {
                                width: 100% !important;
                                border-collapse: collapse !important;
                                margin: 14px 0 !important;
                                font-size: 0.84rem !important;
                                background-color: #0e0a17 !important;
                                color: #ebdff5 !important;
                                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                                border-radius: 6px !important;
                                overflow: hidden !important;
                            }
                            th {
                                background-color: #1a152e !important;
                                color: #ffffff !important;
                                padding: 10px 14px !important;
                                text-align: left !important;
                                border: 1px solid rgba(255, 255, 255, 0.15) !important;
                                font-weight: 700 !important;
                                letter-spacing: 0.5px !important;
                                font-size: 0.8rem !important;
                                text-transform: uppercase !important;
                            }
                            td {
                                background-color: #120e20 !important;
                                color: #ebdff5 !important;
                                padding: 8px 14px !important;
                                border: 1px solid rgba(255, 255, 255, 0.08) !important;
                                vertical-align: top !important;
                            }
                            tr:nth-child(even) td {
                                background-color: #0e0a17 !important;
                            }
                            tr:hover td {
                                background-color: #1a152e !important;
                            }
                            
                            /* Bloques de código (pre, code) dentro del Shadow DOM */
                            pre, code, .code-block, .markdown-code-block {
                                background-color: #0e0a17 !important;
                                color: #ebdff5 !important;
                                border: 1px solid rgba(255, 255, 255, 0.12) !important;
                                padding: 12px !important;
                                border-radius: 8px !important;
                                display: block !important;
                            }
                        `;
                        shadow.appendChild(style);
                        console.log("Estilos inyectados exitosamente en Shadow Root de:", root.tagName);
                    }
                    // Buscar recursivamente dentro del Shadow DOM
                    shadow.querySelectorAll('*').forEach(child => injectStylesRecursively(child));
                }
                
                // Buscar recursivamente en hijos estándar
                if (root.children) {
                    Array.from(root.children).forEach(child => injectStylesRecursively(child));
                }
            }

            function runShadowInjection() {
                injectStylesRecursively(document.body);
            }

            // Monitorear e inyectar de manera constante cada 300ms
            setInterval(runShadowInjection, 300);
            document.addEventListener('DOMContentLoaded', runShadowInjection);
        """)
    ),
    title=""
)


# --- LÓGICA DEL SERVIDOR (SERVER) ---
def server(input, output, session):
    
    is_empty = reactive.Value(True)
    current_report_data = reactive.Value(None)
    current_audit_data = reactive.Value(None)
    chat = ui.Chat(id="chat")

    # Obtener el motor de procesamiento para el archivo seleccionado
    @reactive.calc
    def pdf_engine():
        if not pdf_files or pdf_files[0].startswith("Ningún archivo"):
            return None
        
        datapath = os.path.join(DATA_DIR, pdf_files[0])
        if not os.path.exists(datapath):
            return None
            
        return PDFExtractorEngine(datapath)

    # Reactive calc para el total de páginas del PDF cargado
    @reactive.calc
    def pdf_pages():
        engine = pdf_engine()
        return engine.num_pages if engine else 1

    # Proceso de extracción e inteligencia analítico reactiva
    @reactive.calc
    def extraction_results():
        engine = pdf_engine()
        
        # Si no hay PDF, usar engine en modo CSV-only (lee los datasets precalculados directamente)
        if not engine:
            engine = PDFExtractorEngine(None)
        
        start = 1
        # Si el engine no tiene PDF cargado, usar el total conocido del corpus (5,028 páginas)
        end = engine.num_pages if engine.num_pages > 0 else 5028
        clean = True
        lang = "en"
            
        text, metrics = engine.process_document(start, end, clean=clean, language=lang)
        
        orig_name = pdf_files[0] if pdf_files and not pdf_files[0].startswith("Ningún") else "Epstein_documents.pdf"
        filename = f"analytic_{orig_name.replace('.pdf', '')}.txt"
        meta = engine.extract_metadata()
        
        return {
            "text": text,
            "metrics": metrics,
            "filename": filename,
            "metadata": meta,
            "pages_processed": end
        }


    # Descargar TXT limpio
    @render.download(filename=lambda: extraction_results()["filename"] if extraction_results() else "analytic.txt")
    def download_btn():
        results = extraction_results()
        if not results:
            return None
        path = "temp_extracted.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(results["text"])
        return path

    # RENDERIZADO DEL TAB 1: DASHBOARD ANALÍTICO
    @render.ui
    def analytic_dashboard_ui():
        try:
            results = extraction_results()
        except Exception:
            results = None
            
        if not results:
            return ui.div(
                ui.span("", style="font-size: 3.5rem; display: block; margin-bottom: 0.8rem;"),
                ui.h4("Error de Carga o Inicialización", style="color: #ef4444;"),
                ui.p("Por favor, asegúrate de que el archivo Epstein_documents.pdf exista en la carpeta '01 Datasets Usados'.", style="color: #bfaec2;"),
                style="text-align: center; padding: 5rem 2rem; background: rgba(255,255,255,0.012); border-radius: 12px; border: 1px dashed rgba(239,68,68,0.2);"
            )
            
        metrics = results["metrics"]
        
        return ui.div(
            # Fila de KPIs
            ui.div(
                ui.div(
                    ui.div(
                        ui.div("Páginas Escaneadas", class_="kpi-title"),
                        ui.div(f"{results['pages_processed']}", class_="kpi-value", style="color: #c084fc;"),
                        class_="kpi-card"
                    ),
                    class_="kpi-wrapper"
                ),
                ui.div(
                    ui.div(
                        ui.div("Palabras Procesadas", class_="kpi-title"),
                        ui.div(f"{metrics['total_words']:,}", class_="kpi-value"),
                        class_="kpi-card"
                    ),
                    class_="kpi-wrapper"
                ),
                ui.div(
                    ui.div(
                        ui.div("Menciones Censuradas", class_="kpi-title"),
                        ui.div(f" {metrics['redactions_count']:,}", class_="kpi-value", style="color: #ef4444;"),
                        class_="kpi-card"
                    ),
                    class_="kpi-wrapper"
                ),
                ui.div(
                    ui.div(
                        ui.div("Índice Censura (x1k)", class_="kpi-title"),
                        ui.div(f"{metrics['censorship_index']:.1f}", class_="kpi-value", style="color: #fca5a5;"),
                        class_="kpi-card"
                    ),
                    class_="kpi-wrapper"
                ),
                ui.div(
                    ui.div(
                        ui.div("Total Evasivas", class_="kpi-title"),
                        ui.div(f"🤐 {metrics['evasions_count']:,}", class_="kpi-value", style="color: #eab308;"),
                        class_="kpi-card"
                    ),
                    class_="kpi-wrapper"
                ),
                ui.div(
                    ui.div(
                        ui.div("Índice Evasividad (x1k)", class_="kpi-title"),
                        ui.div(f"{metrics['evasiveness_index']:.1f}", class_="kpi-value", style="color: #fef08a;"),
                        class_="kpi-card"
                    ),
                    class_="kpi-wrapper"
                ),
                class_="kpi-row"
            ),
            
            ui.hr(style="border-color: rgba(168, 85, 247, 0.2); margin: 1.2rem 0;"),
            
            # FILA "STREAMING" (Filtros Reactivos)
            ui.layout_columns(
                ui.div(
                    ui.div(ui.output_text("out_conteo_streaming", inline=True), class_="kpi-value", style="font-size: 3.5rem; color: #34d399; font-weight: 900; line-height: 1; margin-bottom: 10px;"),
                    ui.div("Total Menciones Filtradas", class_="kpi-title"),
                    ui.div("Reactivo en Tiempo Real", style="font-size: 0.7rem; color: #7f8c8d; margin-top: 5px;"),
                    class_="kpi-card", style="display: flex; flex-direction: column; justify-content: center; align-items: center; background: rgba(52, 211, 153, 0.05); border-color: rgba(52, 211, 153, 0.3); padding: 30px;"
                ),
                ui.card(
                    ui.card_header("Proporción de Red Filtrada (Donut Reactivo)"),
                    ui.output_plot("plot_anillo_streaming"),
                    ui.div(
                        ui.div("STREAMING DE PROPORCIONES", class_="explanation-title"),
                        ui.p("Gráfica de anillo interactiva que reacciona instantáneamente a los sliders y checkboxes del panel lateral."),
                        class_="explanation-box"
                    )
                ),
                col_widths=[4, 8]
            ),
            
            ui.hr(style="border-color: rgba(168, 85, 247, 0.2); margin: 1.2rem 0;"),
            
            # FILA DE GRÁFICOS 1 (Top 10 Personas y Co-ocurrencias)
            ui.layout_columns(
                ui.card(
                    ui.card_header("Personas Clave Identificadas (Menciones)"),
                    ui.output_plot("person_chart"),
                    ui.div(
                        ui.div("ANÁLISIS DE ENTIDADES DE ALTO INTERÉS", class_="explanation-title"),
                        ui.p("Rastrea menciones de personajes clave en la red del caso Epstein (como Ghislaine Maxwell, Donald Trump, Virginia Giuffre, Prince Andrew, Bill Clinton) combinando listas y heurísticas de reconocimiento de entidades."),
                        class_="explanation-box"
                    )
                ),
                col_widths=[12]
            ),
            
            # FILA DE GRÁFICOS 2 (Evasión Verbal y Temáticas)
            ui.layout_columns(
                ui.card(
                    ui.card_header("Tácticas de Evasividad Verbal Detectadas"),
                    ui.output_plot("evasions_details_chart"),
                    ui.div(
                        ui.div("🤐 PERFIL DE POSTURA DEFENSIVA", class_="explanation-title"),
                        ui.p("Clasifica las evasiones lingüísticas más comunes realizadas en el documento, distinguiendo objeciones de abogados de la pérdida de memoria alegada ('no recuerdo') o apelaciones constitucionales a la Quinta Enmienda."),
                        class_="explanation-box"
                    )
                ),
                ui.card(
                    ui.card_header("Prevalencia Temática en el Documento"),
                    ui.output_plot("topics_prevalence_chart"),
                    ui.div(
                        ui.div("MAPEO DE TEMÁTICAS DE SOSPECHA", class_="explanation-title"),
                        ui.p("Cuantifica el volumen de palabras asociadas a categorías sospechosas: Propiedades/Lugares de interés, Logística y vuelos de Lolita Express, Tópicos de Abuso y vocabulario del Ámbito Judicial del Juicio."),
                        class_="explanation-box"
                    )
                ),
                col_widths=[6, 6]
            ),
            

            
            # FILA DE GRÁFICOS 3 (Riesgo vs Sentimiento y Vocabulario Clave)
            ui.layout_columns(
                ui.card(
                    ui.card_header("Correlación de Riesgo vs Sentimiento por Persona"),
                    ui.output_plot("risk_sentiment_chart"),
                    ui.div(
                        ui.div("CUADRANTE DE RIESGO SEMÁNTICO", class_="explanation-title"),
                        ui.p("Cruza el Índice de Sentimiento Analítico (eje X, negativo a positivo) con el Índice de Riesgo Analítico (eje Y, co-ocurrencia con abusos o logística). Las burbujas más grandes indican mayor volumen de menciones. Los implicados en el cuadrante superior izquierdo representan el perfil de mayor criticidad en el expediente."),
                        class_="explanation-box"
                    )
                ),
                ui.card(
                    ui.card_header("Top 10 Vocablos Semánticos más Frecuentes"),
                    ui.output_plot("content_words_chart"),
                    ui.div(
                        ui.div("ANÁLISIS DE FRECUENCIA DE TÉRMINOS", class_="explanation-title"),
                        ui.p("Muestra los términos generales más recurrentes dentro de la transcripción judicial, excluyendo stopwords y nombres propios. Revela los conceptos clave en torno a los cuales giran las deposiciones y testimonios."),
                        class_="explanation-box"
                    )
                ),
                col_widths=[6, 6]
            ),
            
            ui.hr(style="border-color: rgba(168, 85, 247, 0.2); margin: 1.5rem 0;"),
            ui.div(
                ui.download_button(
                    "download_dashboard_report", 
                    "Descargar Reporte Ejecutivo del Dashboard (PDF)", 
                    class_="btn-primary", 
                    style="background:#10b981; border:none; height:45px; font-weight:bold; font-size:1rem; width:100%; max-width:400px; display:inline-block;"
                ),
                style="text-align: center; padding-bottom: 20px;"
            )
        )

    # RENDERIZADO DEL TAB 2: EXPLORADOR DE DOCUMENTOS Y CRONOLOGÍA
    @render.ui
    def document_explorer_ui():
        try:
            results = extraction_results()
        except Exception:
            results = None
            
        if not results:
            return ui.div(
                ui.span("", style="font-size: 3.5rem; display: block; margin-bottom: 0.8rem;"),
                ui.h4("Error de Carga o Inicialización", style="color: #ef4444;"),
                ui.p("Por favor, asegúrate de que el archivo Epstein_documents.pdf exista en la carpeta '01 Datasets Usados'.", style="color: #bfaec2;"),
                style="text-align: center; padding: 5rem 2rem; background: rgba(255,255,255,0.012); border-radius: 12px; border: 1px dashed rgba(239,68,68,0.2);"
            )
            
        meta = results["metadata"]
        title_val = meta.get("Título", "No especificado")
        author_val = meta.get("Autor", "No especificado")
        
        return ui.layout_columns(
            ui.card(
                ui.card_header("Vista Previa Judicial (Transcripción Limpia)"),
                ui.input_text_area(
                    "preview_area", 
                    "", 
                    value=results["text"][:3500] + ("\n\n[Expediente truncado para visualización rápida...]" if len(results["text"]) > 3500 else ""), 
                    height="320px", 
                    width="100%"
                ),
                ui.download_button(
                    "download_btn", 
                    "DESCARGAR TRANSCRIPCIÓN ANALÍTICO (.TXT)", 
                    class_="btn-primary btn-download w-100",
                    style="margin-top: 0.8rem;"
                ),
                ui.div(
                    ui.row(
                        ui.column(6, ui.div(ui.div("Título de Expediente", class_="meta-item-title"), ui.div(title_val, class_="meta-item-value"))),
                        ui.column(6, ui.div(ui.div("Autoría Legal", class_="meta-item-title"), ui.div(author_val, class_="meta-item-value")))
                    ),
                    class_="meta-container"
                )
            ),
            ui.card(
                ui.card_header("Frecuencia Temporal (Años Mencionados)"),
                ui.output_plot("timeline_chart"),
                ui.div(
                    ui.div("HISTOGRAMA CRONOLÓGICO ANALÍTICO", class_="explanation-title"),
                    ui.p("Rastrea la presencia de años lógicos específicos dentro de los testimonios o deposiciones judiciales. Ayuda a identificar en qué años se concentran los abusos o vuelos reportados en este expediente judicial."),
                    class_="explanation-box"
                )
            ),
            col_widths=[8, 4]
        )

    # --- MATPLOTLIB PLOTS ---
    
    @render.plot
    def person_chart():
        results = extraction_results()
        if not results or not results["metrics"]["top_persons"]:
            fig, ax = plt.subplots(figsize=(5, 3.8), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.axis('off')
            return fig
            
        top_persons = results["metrics"]["top_persons"]
        selected = list(input.selected_persons())
        min_m = input.min_mentions()
        filtered = [item for item in top_persons if item[0] in selected and item[1] >= min_m]
        
        if not filtered:
            fig, ax = plt.subplots(figsize=(5, 3.8), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.text(0.5, 0.5, "Sin resultados para los filtros seleccionados", ha='center', va='center', color='#bfaec2', fontsize=9)
            ax.axis('off')
            return fig
            
        names = [item[0] for item in filtered][::-1] 
        freqs = [item[1] for item in filtered][::-1]
        
        fig, ax = plt.subplots(figsize=(5, 3.8), facecolor='#0b090f')
        ax.set_facecolor('#0b090f')
        
        bars = ax.barh(names, freqs, color='#a855f7', edgecolor='#d8b4fe', height=0.55)
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.xaxis.grid(True, linestyle='--', alpha=0.1, color='#ffffff')
        ax.set_axisbelow(True)
        ax.tick_params(colors='#bfaec2', labelsize=9, length=0)
        
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + (max(freqs)*0.015 if max(freqs)>0 else 0), 
                bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', 
                ha='left', 
                va='center', 
                color='#d8b4fe', 
                fontweight='bold', 
                fontsize=8.5
            )
        plt.tight_layout()
        return fig

    @render.ui
    def person_list_ui():
        results = extraction_results()
        if not results or not results["metrics"]["top_persons"]:
            return None
            
        top_persons = results["metrics"]["top_persons"]
        selected = list(input.selected_persons())
        min_m = input.min_mentions()
        filtered = [item for item in top_persons if item[0] in selected and item[1] >= min_m]
        
        if not filtered:
            return ui.p("Sin personas bajo los filtros seleccionados.", style="color: #bfaec2; font-style: italic; font-size: 0.85rem;")
            
        list_items = []
        for i, (name, freq) in enumerate(filtered, 1):
            emoji = "" if i == 1 else "" if i <= 3 else ""
            list_items.append(
                ui.div(
                    ui.span(f"{emoji} {i}. "),
                    ui.strong(f"{name}", style="color: #ffffff;"),
                    ui.span(f" ({freq} menciones)"),
                    style="margin-bottom: 0.3rem; font-size: 0.9rem;"
                )
            )
        return ui.div(*list_items)

    @render.ui
    def co_occur_chart_ui():
        results = extraction_results()
        if not results or not results["metrics"].get("top_co_occurrences"):
            return ui.HTML("<div style='color:#bfaec2;text-align:center;padding:40px;'>Sin co-ocurrencias suficientes</div>")
            
        top_co = results["metrics"]["top_co_occurrences"]
        selected = list(input.selected_persons())
        filtered = []
        for pair, freq in top_co:
            parts = pair.split(" & ")
            # Solo filtramos si hay seleccionados, pero el grafo es mejor si mostramos la red completa
            if not selected or (len(parts) == 2 and (parts[0] in selected or parts[1] in selected)):
                filtered.append((parts[0], parts[1], freq))
                
        if not filtered:
            return ui.HTML("<div style='color:#bfaec2;text-align:center;padding:40px;'>Sin conexiones para los filtros activos</div>")
            
        import networkx as nx
        from pyvis.network import Network
        import tempfile
        import os
        
        # Crear grafo de NetworkX
        G = nx.Graph()
        
        # Clasificación semántica de actores para colores consistentes y significativos
        node_colors = {
            "Jeffrey Epstein": "#f43f5e",
            "Ghislaine Maxwell": "#f43f5e",
            "Virginia Giuffre": "#06b6d4",
            "Annie Farmer": "#06b6d4",
            "Johanna Sjoberg": "#06b6d4",
            "Bill Clinton": "#eab308",
            "Donald Trump": "#eab308",
            "Al Gore": "#eab308",
            "Prince Andrew": "#eab308",
            "Stephen Hawking": "#a855f7",
            "David Copperfield": "#a855f7",
            "Alan Dershowitz": "#a855f7",
            "Kevin Spacey": "#a855f7",
            "Leslie Wexner": "#a855f7",
            "Jean-Luc Brunel": "#a855f7",
        }
        
        for p1, p2, freq in filtered:
            c1 = node_colors.get(p1, "#9ca3af")
            c2 = node_colors.get(p2, "#9ca3af")
            G.add_node(p1, title=p1, color=c1)
            G.add_node(p2, title=p2, color=c2)
            # Añadir arista con peso
            G.add_edge(p1, p2, value=freq, title=f"Co-ocurrencias: {freq}", color="rgba(255,255,255,0.2)")
            
        # Calcular grados para el tamaño de los nodos
        degrees = dict(G.degree())
        for node in G.nodes():
            G.nodes[node]['size'] = 10 + (degrees[node] * 3)
            
        # Crear red interactiva de PyVis (Altura aumentada a 650px para pantalla completa)
        net = Network(height="650px", width="100%", bgcolor="#0b090f", font_color="#e5e0eb", select_menu=False)
        # Opciones de física para que parezca una red neuronal/criminal espaciosa y legible
        net.set_options("""
        var options = {
          "nodes": {
            "borderWidth": 2,
            "borderWidthSelected": 4,
            "font": {
              "color": "#e5e0eb",
              "size": 14,
              "face": "Outfit"
            },
            "shape": "dot"
          },
          "edges": {
            "smooth": {
              "type": "continuous",
              "forceDirection": "none"
            }
          },
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -180,
              "centralGravity": 0.015,
              "springLength": 160,
              "springConstant": 0.05
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"iterations": 150}
          }
        }
        """)
        net.from_nx(G)
        
        # Guardar en archivo temporal y leer el HTML
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.html', delete=False) as f:
            temp_path = f.name
            
        net.write_html(temp_path)
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        os.unlink(temp_path)
        
        # Eliminar el borde blanco/gris feo por defecto de pyvis
        html_content = html_content.replace('border: 1px solid lightgray', 'border: none')
        
        # Usamos srcdoc para inyectar el HTML directamente en un iframe sin necesidad de servidor estático
        import html
        escaped_html = html.escape(html_content)
        
        return ui.HTML(f"<iframe srcdoc='{escaped_html}' style='width:100%; height:650px; border:none; border-radius:10px; background:#0b090f;'></iframe>")

    @render.ui
    def co_occur_metrics_ui():
        results = extraction_results()
        if not results or not results["metrics"].get("top_co_occurrences"):
            return ui.div()
            
        top_co = results["metrics"]["top_co_occurrences"]
        selected = list(input.selected_persons())
        filtered = []
        for pair, freq in top_co:
            parts = pair.split(" & ")
            if not selected or (len(parts) == 2 and (parts[0] in selected or parts[1] in selected)):
                filtered.append((parts[0], parts[1], freq))
                
        if not filtered:
            return ui.HTML("<div style='color:#bfaec2;text-align:center;padding:20px;'>Sin datos suficientes para calcular métricas</div>")
            
        import networkx as nx
        import pandas as pd
        
        G = nx.Graph()
        for p1, p2, freq in filtered:
            G.add_node(p1)
            G.add_node(p2)
            G.add_edge(p1, p2, weight=freq)
            
        if len(G.nodes) == 0:
            return ui.HTML("<div style='color:#bfaec2;text-align:center;padding:20px;'>Grafo vacío</div>")
            
        # Calcular métricas de NetworkX
        deg_raw = dict(G.degree())
        deg_cent = nx.degree_centrality(G)
        try:
            between_cent = nx.betweenness_centrality(G, weight='weight')
        except Exception:
            between_cent = nx.betweenness_centrality(G)
        clustering_coef = nx.clustering(G)
        
        # Consolidar en un DataFrame
        metrics_data = []
        for node in G.nodes():
            metrics_data.append({
                "Personaje": node,
                "Conexiones": deg_raw.get(node, 0),
                "Centralidad_Grado": deg_cent.get(node, 0.0),
                "Centralidad_Intermediacion": between_cent.get(node, 0.0),
                "Coeficiente_Agrupacion": clustering_coef.get(node, 0.0)
            })
            
        df_metrics = pd.DataFrame(metrics_data)
        # Ordenar por intermediación y conexiones descendente
        df_metrics = df_metrics.sort_values(by=["Centralidad_Intermediacion", "Conexiones"], ascending=False).reset_index(drop=True)
        
        # Generar filas de la tabla HTML
        table_rows = []
        for idx, row in df_metrics.iterrows():
            # Asignar color semántico coincidente con el grafo
            node_colors = {
                "Jeffrey Epstein": "#f43f5e",
                "Ghislaine Maxwell": "#f43f5e",
                "Virginia Giuffre": "#06b6d4",
                "Annie Farmer": "#06b6d4",
                "Johanna Sjoberg": "#06b6d4",
                "Bill Clinton": "#eab308",
                "Donald Trump": "#eab308",
                "Al Gore": "#eab308",
                "Prince Andrew": "#eab308",
                "Stephen Hawking": "#a855f7",
                "David Copperfield": "#a855f7",
                "Alan Dershowitz": "#a855f7",
                "Kevin Spacey": "#a855f7",
                "Leslie Wexner": "#a855f7",
                "Jean-Luc Brunel": "#a855f7",
            }
            color = node_colors.get(row['Personaje'], "#9ca3af")
            
            table_rows.append(f"""
                <tr style="border-bottom: 1px solid rgba(168, 85, 247, 0.15); transition: background-color 0.2s;">
                    <td style="padding: 12px 15px; font-weight: bold; color: {color};">{row['Personaje']}</td>
                    <td style="padding: 12px 15px; text-align: center; color: #ffffff;">{row['Conexiones']}</td>
                    <td style="padding: 12px 15px; text-align: center; color: #e5e0eb;">{row['Centralidad_Grado']:.3f}</td>
                    <td style="padding: 12px 15px; text-align: center; color: #e5e0eb; font-weight: bold;">{row['Centralidad_Intermediacion']:.3f}</td>
                    <td style="padding: 12px 15px; text-align: center; color: #bfaec2;">{row['Coeficiente_Agrupacion']:.3f}</td>
                </tr>
            """)
            
        table_content = "".join(table_rows)
        
        html_markup = f"""
        <div style="background: rgba(15, 11, 27, 0.85); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 12px; padding: 24px; color: #e5e0eb; margin-top: 15px;">
            <h4 style="color: #c084fc; font-weight: bold; margin-bottom: 8px;">Métricas Avanzadas de Teoría de Grafos (Cálculo en Tiempo Real)</h4>
            <p style="color: #bfaec2; font-size: 0.85rem; margin-bottom: 20px; line-height: 1.4;">
                Estas métricas matemáticas describen cuantitativamente el rol estructural de cada actor en la red. 
                <strong>Centralidad de Grado:</strong> Fracción de nodos a los que está conectado. 
                <strong>Centralidad de Intermediación (Betweenness):</strong> Frecuencia con la que el actor actúa como puente en el camino más corto entre otros dos actores (indica control e influencia de flujos). 
                <strong>Coeficiente de Agrupación (Clustering):</strong> Mide qué tan conectados están los vecinos de este actor entre sí (cohesión interna).
            </p>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem;">
                    <thead>
                        <tr style="border-bottom: 2px solid #a855f7; color: #a855f7; font-weight: bold;">
                            <th style="padding: 12px 15px; text-align: left;">Personaje</th>
                            <th style="padding: 12px 15px; text-align: center;">Conexiones Directas</th>
                            <th style="padding: 12px 15px; text-align: center;">Centralidad de Grado</th>
                            <th style="padding: 12px 15px; text-align: center;">Centralidad de Intermediación</th>
                            <th style="padding: 12px 15px; text-align: center;">Coeficiente de Agrupación</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_content}
                    </tbody>
                </table>
            </div>
        </div>
        """
        return ui.HTML(html_markup)

    @render.plot
    def timeline_chart():
        results = extraction_results()
        if not results or not results["metrics"].get("timeline"):
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.text(0.5, 0.5, "Sin datos de línea de tiempo", ha='center', va='center', color='#bfaec2', fontsize=10)
            ax.axis('off')
            return fig
            
        timeline = results["metrics"]["timeline"]
        timeline_filtered = [item for item in timeline if 1995 <= int(item[0]) <= 2024]
        if not timeline_filtered:
            timeline_filtered = timeline
            
        years = [int(item[0]) for item in timeline_filtered]
        freqs = [item[1] for item in timeline_filtered]
        
        fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
        ax.set_facecolor('#0b090f')
        
        ax.plot(years, freqs, color='#f43f5e', linewidth=2.2, marker='o', markersize=5, markerfacecolor='#ffffff', markeredgecolor='#f43f5e')
        ax.fill_between(years, freqs, color='#f43f5e', alpha=0.15)
        
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
        
        ax.tick_params(colors='#e5e0eb', labelsize=9)
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig


    @output
    @render.text
    def out_conteo_streaming():
        results = extraction_results()
        if not results or not results["metrics"].get("top_persons"):
            return "0"
        
        top_persons = results["metrics"]["top_persons"]
        selected = list(input.selected_persons())
        min_m = input.min_mentions()
        filtered = [item for item in top_persons if item[0] in selected and item[1] >= min_m]
        
        total_menciones = sum([item[1] for item in filtered])
        return f"{total_menciones:,}"

    @output
    @render.plot
    def plot_anillo_streaming():
        results = extraction_results()
        if not results or not results["metrics"].get("top_persons"):
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.axis('off')
            return fig
            
        top_persons = results["metrics"]["top_persons"]
        selected = list(input.selected_persons())
        min_m = input.min_mentions()
        filtered = [item for item in top_persons if item[0] in selected and item[1] >= min_m]
        
        if not filtered:
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.text(0.5, 0.5, "Sin resultados para los filtros", ha='center', va='center', color='#bfaec2', fontsize=9)
            ax.axis('off')
            return fig
            
        labels = [item[0] for item in filtered]
        sizes = [item[1] for item in filtered]
        
        # Generar colores dinámicos
        import matplotlib.cm as cm
        import numpy as np
        colors = cm.plasma(np.linspace(0.2, 0.9, len(labels)))
        
        fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
        ax.set_facecolor('#0b090f')
        
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, colors=colors, autopct='%1.1f%%', 
            startangle=90, textprops=dict(color='#bfaec2', size=8.5),
            wedgeprops=dict(width=0.45, edgecolor='#0b090f', linewidth=2)
        )
        
        plt.setp(autotexts, size=9, weight="bold", color="#ffffff")
        plt.setp(texts, size=8.5)
        
        plt.tight_layout()
        return fig

    @render.plot
    def evasions_details_chart():
        results = extraction_results()
        if not results or "evasions_details" not in results["metrics"]:
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.axis('off')
            return fig
            
        details = results["metrics"]["evasions_details"]
        labels = list(details.keys())
        sizes = list(details.values())
        
        if sum(sizes) == 0:
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.text(0.5, 0.5, "Sin tácticas de evasión detectadas", ha='center', va='center', color='#bfaec2', fontsize=10)
            ax.axis('off')
            return fig
            
        colors = ['#eab308', '#ca8a04', '#a16207', '#854d0e', '#713f12']
        
        fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
        ax.set_facecolor('#0b090f')
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            colors=colors, 
            autopct='%1.1f%%', 
            startangle=140, 
            pctdistance=0.75,
            textprops=dict(color='#bfaec2', size=8.5),
            wedgeprops=dict(width=0.45, edgecolor='#0b090f', linewidth=2)
        )
        
        for autotext in autotexts:
            autotext.set_color('#ffffff')
            autotext.set_fontsize(8.5)
            autotext.set_weight('bold')
            
        ax.axis('equal')  
        plt.tight_layout()
        return fig

    @render.plot
    def topics_prevalence_chart():
        results = extraction_results()
        if not results or "topic_scores" not in results["metrics"]:
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.axis('off')
            return fig
            
        scores = results["metrics"]["topic_scores"]
        topics = list(scores.keys())
        values = list(scores.values())
        
        fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
        ax.set_facecolor('#0b090f')
        
        # Determinar colores reactivos basados en el filtro de Sephora
        colors = []
        edgecolors = []
        selected_topic = input.dominant_topic()
        for t in topics:
            if selected_topic != "Todos" and t.startswith(selected_topic[:5]):
                colors.append('#f43f5e') # Rosa neón Sephora
                edgecolors.append('#ffffff') # Resaltado blanco pulido
            else:
                colors.append('#10b981') # Verde esmeralda por defecto
                edgecolors.append('#34d399')
        
        bars = ax.bar(topics, values, color=colors, edgecolor=edgecolors, width=0.45)
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.yaxis.grid(True, linestyle='--', alpha=0.1, color='#ffffff')
        ax.set_axisbelow(True)
        ax.tick_params(colors='#bfaec2', labelsize=8.5, length=0)
        
        for i, bar in enumerate(bars):
            height = bar.get_height()
            is_highlighted = (selected_topic != "Todos" and topics[i].startswith(selected_topic[:5]))
            ax.text(
                bar.get_x() + bar.get_width()/2, 
                height + (max(values)*0.015 if max(values)>0 else 0), 
                f'{int(height)}', 
                ha='center', 
                va='bottom', 
                color='#ffffff' if is_highlighted else '#34d399', 
                fontweight='bold', 
                fontsize=8.5
            )
        plt.tight_layout()
        return fig

    @render.plot
    def risk_sentiment_chart():
        results = extraction_results()
        if not results or not results["metrics"].get("person_sentiment_analytics"):
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.axis('off')
            return fig
            
        analytics = results["metrics"]["person_sentiment_analytics"]
        selected = list(input.selected_persons())
        min_m = input.min_mentions()
        valid_data = [p for p in analytics if p["Persona"] in selected and p["Menciones"] >= min_m]
        
        if not valid_data:
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.text(0.5, 0.5, "Sin correlaciones para los filtros activos", ha='center', va='center', color='#bfaec2', fontsize=9)
            ax.axis('off')
            return fig
            
        names = [p["Persona"] for p in valid_data]
        sentiment = [p["Indice Sentimiento"] for p in valid_data]
        risk = [p["Indice de Riesgo Analítico"] for p in valid_data]
        mentions = [p["Menciones"] for p in valid_data]
        
        fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
        ax.set_facecolor('#0b090f')
        
        max_mentions = max(mentions) if mentions else 1
        sizes = [max(80, (m / max_mentions) * 450) for m in mentions]
        
        scatter = ax.scatter(sentiment, risk, s=sizes, c=risk, cmap='plasma', alpha=0.75, edgecolors='#ffffff', linewidths=1)
        
        for i, txt in enumerate(names):
            ax.annotate(
                txt, 
                (sentiment[i], risk[i]),
                xytext=(5, 5), 
                textcoords='offset points',
                color='#ffffff',
                fontsize=7.8,
                fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.2', fc='black', alpha=0.4, ec='none')
            )
            
        for spine in ax.spines.values():
            spine.set_color((168/255, 85/255, 247/255, 0.2))
            
        ax.xaxis.grid(True, linestyle='--', alpha=0.1, color='#ffffff')
        ax.yaxis.grid(True, linestyle='--', alpha=0.1, color='#ffffff')
        ax.set_axisbelow(True)
        
        ax.tick_params(colors='#bfaec2', labelsize=8.5)
        ax.set_xlim(-1.05, 1.05)
        
        ax.axvline(0, color=(1.0, 1.0, 1.0, 0.15), linestyle=':', linewidth=1)
        ax.axhline(sum(risk)/len(risk) if risk else 1, color=(1.0, 1.0, 1.0, 0.15), linestyle=':', linewidth=1)
        
        plt.tight_layout()
        return fig

    @render.plot
    def content_words_chart():
        results = extraction_results()
        if not results or not results["metrics"].get("top_words"):
            fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
            ax.set_facecolor('#0b090f')
            ax.axis('off')
            return fig
            
        top_words = results["metrics"]["top_words"]
        words = [item[0] for item in top_words][::-1]
        freqs = [item[1] for item in top_words][::-1]
        
        fig, ax = plt.subplots(figsize=(5, 3.2), facecolor='#0b090f')
        ax.set_facecolor('#0b090f')
        
        bars = ax.barh(words, freqs, color='#f59e0b', edgecolor='#fcd34d', height=0.55)
        for spine in ax.spines.values():
            spine.set_visible(False)
            
        ax.xaxis.grid(True, linestyle='--', alpha=0.1, color='#ffffff')
        ax.set_axisbelow(True)
        ax.tick_params(colors='#bfaec2', labelsize=9, length=0)
        
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + (max(freqs)*0.015 if max(freqs)>0 else 0), 
                bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', 
                ha='left', 
                va='center', 
                color='#fcd34d', 
                fontweight='bold', 
                fontsize=8.5
            )
        plt.tight_layout()
        return fig


    @chat.on_user_submit
    async def _handle_user_submit():
        is_empty.set(False)
        ui_messages = list(chat.messages())
        # Limitar historial a 6 mensajes (3 turnos) para reducir tokens y latencia
        if len(ui_messages) > 6:
            ui_messages = ui_messages[-6:]
            
        # Crear copia limpia de mensajes para enviar al LLM
        llm_messages = []
        for m in ui_messages:
            role = m.role if hasattr(m, 'role') else m.get('role', '')
            content = m.content if hasattr(m, 'content') else m.get('content', '')
            llm_messages.append({"role": role, "content": content})
            
        # Inyectar contexto analítico SOLO en el primer mensaje del turno actual (el último del usuario)
        # Fragmento reducido a 2,500 chars para no saturar el payload
        try:
            with reactive.isolate():
                results = extraction_results()
            if results and llm_messages and llm_messages[-1]["role"] == "user":
                metrics = results["metrics"]
                meta = results["metadata"]
                doc_name = pdf_files[0] if pdf_files else "Epstein_documents.pdf"
                
                is_first_message = len([m for m in llm_messages if m["role"] == "user"]) == 1
                
                ctx = f"\n\n[CONTEXTO ANALÍTICO — {doc_name}]\n"
                ctx += f"Páginas: {results['pages_processed']}  Censura [REDACTED]: {metrics['redactions_count']} (idx: {metrics['censorship_index']:.1f})  Evasiones: {metrics.get('evasiones_count', metrics.get('evasions_count', 0))} (idx: {metrics['evasiveness_index']:.1f})\n"
                ctx += f"Tópicos: {metrics['topic_scores']}\n"
                ctx += f"Metadata: {meta}\n"
                
                # Solo inyectar el texto del documento en el primer mensaje del chat
                if is_first_message:
                    ctx += f"Fragmento del expediente (primeras 2500 chars):\n{results['text'][:2500]}\n"
                
                llm_messages[-1]["content"] += ctx
        except Exception as e:
            print(f"Error inyectando contexto analítico al Copilot: {e}")

        # Inyectar instrucción de sistema (comportamiento del analista)
        system_msg = {
            "role": "system", 
            "content": "Eres Olvera AI, un analista de inteligencia experto. Responde siempre analizando profundamente los datos. Redacta en párrafos continuos, fluidos y profesionales. PROHIBIDO escupir listas de viñetas, bullet-points o formatos robóticos predefinidos. Interpreta qué significa la evidencia."
        }
        llm_messages.insert(0, system_msg)

        async_gen = logic.stream_chat_response(
            messages=llm_messages,
            model=providers.DEFAULT_MODEL,
            web_search_enabled=False,
            image_b64=None
        )
        await chat.append_message_stream(async_gen)

    # Evento de click en sugerencia de chat
    @reactive.Effect
    @reactive.event(input.suggestion_click)
    async def _handle_suggestion():
        prompt = input.suggestion_click()
        if not prompt:
            return
        is_empty.set(False)
        await chat.append_message({"role": "user", "content": prompt})
        
        # Contexto reducido (fragmento de 2,500 chars) para respuesta rápida
        try:
            with reactive.isolate():
                results = extraction_results()
            if results:
                metrics = results["metrics"]
                meta = results["metadata"]
                doc_name = pdf_files[0] if pdf_files else "Epstein_documents.pdf"
                ctx = f"\n\n[CONTEXTO ANALÍTICO — {doc_name}]\n"
                ctx += f"Páginas: {results['pages_processed']}  Censura [REDACTED]: {metrics['redactions_count']} (idx: {metrics['censorship_index']:.1f})  Evasiones: {metrics.get('evasiones_count', metrics.get('evasions_count', 0))} (idx: {metrics['evasiveness_index']:.1f})\n"
                ctx += f"Tópicos: {metrics['topic_scores']}\n"
                ctx += f"Metadata: {meta}\n"
                ctx += f"Fragmento del expediente (primeras 2500 chars):\n{results['text'][:2500]}\n"
                enriched_prompt = prompt + ctx
            else:
                enriched_prompt = prompt
        except Exception as e:
            print(f"Error inyectando contexto de sugerencia analítico: {e}")
            enriched_prompt = prompt
            
        system_msg = {
            "role": "system", 
            "content": "Eres Olvera AI, un analista de inteligencia experto. Responde siempre analizando profundamente los datos. Redacta en párrafos continuos, fluidos y profesionales. PROHIBIDO escupir listas de viñetas, bullet-points o formatos robóticos predefinidos. Interpreta qué significa la evidencia."
        }
        messages = [system_msg, {"role": "user", "content": enriched_prompt}]
        async_gen = logic.stream_chat_response(
            messages=messages,
            model=providers.DEFAULT_MODEL,
            web_search_enabled=False,
            image_b64=None
        )
        await chat.append_message_stream(async_gen)

    @output
    @render.ui
    def welcome_ui():
        if not is_empty.get():
            return ui.div()
        return ui.div(
            ui.div(
                ui.HTML("""
                    <div style="width:68px;height:68px;background:#161224;border:1px solid #a855f7;border-radius:18px;display:flex;align-items:center;justify-content:center;margin:0 auto 16px;box-shadow:0 10px 30px rgba(168,85,247,0.2)">
                        <svg viewBox='0 0 24 24' fill='none' stroke='#c084fc' stroke-width='1.5' style='width:38px;height:38px;'>
                            <path d='M12 2L3 7V17L12 22L21 17V7L12 2Z'/>
                            <path d='M12 22V12'/><path d='M12 12L21 7'/><path d='M12 12L3 7'/>
                        </svg>
                    </div>
                    <h2 style='font-family:"Space Grotesk",sans-serif;font-weight:800;font-size:1.4rem;color:#ffffff;margin-bottom:8px;'>Hola, soy Olvera AI</h2>
                    <p style='color:#bfaec2;font-size:0.95rem;'>Tengo acceso en tiempo real a los resultados de minería y transcripciones analíticas del documento. ¿Qué deseas examinar?</p>
                """),
                style="text-align:center;padding:30px 20px 20px;"
            ),
            ui.div(
                ui.div(
                    ui.HTML("<div style='font-weight:700;color:#ffffff;font-size:0.9rem;margin-bottom:4px;'> Explicar Métricas</div><div style='color:#bfaec2;font-size:0.82rem;'>Analiza los gráficos y los KPIs actuales</div>"),
                    onclick="Shiny.setInputValue('suggestion_click', 'Analiza y resume los KPIs y gráficos analíticas del documento actual', {priority:'event'})",
                    class_="chat-suggestion-box",
                    style="background:#161224;border:1px solid rgba(168,85,247,0.22);border-radius:10px;padding:14px 16px;cursor:pointer;transition:all 0.2s;"
                ),
                ui.div(
                    ui.HTML("<div style='font-weight:700;color:#ffffff;font-size:0.9rem;margin-bottom:4px;'> Personas Implicadas</div><div style='color:#bfaec2;font-size:0.82rem;'>Busca conexiones e implicaciones de red</div>"),
                    onclick="Shiny.setInputValue('suggestion_click', '¿Qué personas clave tienen mayor número de menciones y co-ocurrencias en este expediente y qué sugiere esto?', {priority:'event'})",
                    class_="chat-suggestion-box",
                    style="background:#161224;border:1px solid rgba(168,85,247,0.22);border-radius:10px;padding:14px 16px;cursor:pointer;transition:all 0.2s;"
                ),
                ui.div(
                    ui.HTML("<div style='font-weight:700;color:#ffffff;font-size:0.9rem;margin-bottom:4px;'>🤐 Estrategia de Evasión</div><div style='color:#bfaec2;font-size:0.82rem;'>Analiza las tácticas evasivas del testimonio</div>"),
                    onclick="Shiny.setInputValue('suggestion_click', 'Evalúa las tácticas de evasión verbal encontradas. ¿Se observa una postura defensiva o evasiva sistemática?', {priority:'event'})",
                    class_="chat-suggestion-box",
                    style="background:#161224;border:1px solid rgba(168,85,247,0.22);border-radius:10px;padding:14px 16px;cursor:pointer;transition:all 0.2s;"
                ),
                ui.div(
                    ui.HTML("<div style='font-weight:700;color:#ffffff;font-size:0.9rem;margin-bottom:4px;'> Censura e Información</div><div style='color:#bfaec2;font-size:0.82rem;'>Determina el nivel de censura [REDACTED]</div>"),
                    onclick="Shiny.setInputValue('suggestion_click', 'Explica el índice de censura encontrado. ¿Qué tan censurado está el documento y qué podemos deducir?', {priority:'event'})",
                    class_="chat-suggestion-box",
                    style="background:#161224;border:1px solid rgba(168,85,247,0.22);border-radius:10px;padding:14px 16px;cursor:pointer;transition:all 0.2s;"
                ),
                style="display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:0 20px 20px;"
            ),
            style="max-width:680px;margin:0 auto;"
        )

    @output
    @render.ui
    def chat_toolbar_ui():
        return ui.HTML("""
            <div style='border-top:1px solid rgba(168, 85, 247, 0.2);padding:12px 10px 0;margin-top:8px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;'>
                <span style='font-size:0.78rem;color:#ffffff;font-weight:700;letter-spacing:0.5px;'>OLVERA AI</span>
                <span style='font-size:0.78rem;color:rgba(168,85,247,0.4);'></span>
                <span style='font-size:0.78rem;color:#bfaec2;'>Llama 3.3 70B (Groq) &bull; Contexto analítico inyectado &bull; Fallback multi-proveedor activo</span>
            </div>
        """)

    @render.ui
    @reactive.event(input.search_btn)
    async def search_results_ui():
        query = input.search_query()
        if not query:
            return ui.HTML("<div style='color:#bfaec2;'>Por favor ingresa un término de búsqueda y presiona Buscar.</div>")
            
        results = extraction_results()
        if not results:
            return ui.HTML("<div style='color:#bfaec2;'>No hay documentos procesados.</div>")
            
        full_text = results["text"]
        import re
        # Extraer páginas conservando su numeración original para geolocalización de citas
        parts = re.split(r'---\s*P[ÁA]GINA\s+(\d+)\s*---', full_text)
        pages_list = []
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                page_num = parts[i]
                page_text = parts[i+1].strip()
                if page_text:
                    pages_list.append({"page": page_num, "text": page_text})
                    
        if not pages_list:
            return ui.HTML("<div style='color:#bfaec2;'>El documento está vacío o no tiene la estructura de páginas esperada.</div>")
            
        pages = [p["text"] for p in pages_list]
            
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        # TF-IDF Vectorization
        vectorizer = TfidfVectorizer(stop_words='english', max_df=0.85)
        try:
            tfidf_matrix = vectorizer.fit_transform(pages)
            query_vec = vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
            
            top_indices = similarities.argsort()[-3:][::-1]
            
            ui_elements = [ui.h4(f"Resultados Semánticos para: '{query}'", style="color:#06b6d4; margin-bottom:15px; font-weight:bold;")]
            collected_snippets = []
            
            for idx in top_indices:
                score = similarities[idx]
                if score > 0.05:  # Umbral mínimo de relevancia
                    page_num = pages_list[idx]["page"]
                    # Limpieza de transcripción cruda (quitar confidencialidad sin borrar el texto)
                    clean_text = pages[idx]
                    clean_text = re.sub(r'Highly Confidential', '', clean_text, flags=re.IGNORECASE)
                    clean_text = re.sub(r'HIGHLY CONFIDENTIAL AEO', '', clean_text, flags=re.IGNORECASE)
                    clean_text = re.sub(r'Page \d+', '', clean_text, flags=re.IGNORECASE)
                    clean_text = re.sub(r'\b\d+\s+', ' ', clean_text)  # Quitar números de línea sueltos
                    clean_text = clean_text.replace("Q. ", "\n\n**Abogado/Juez:** ")
                    clean_text = clean_text.replace("A. ", "\n**Testigo:** ")
                    
                    if len(clean_text.strip()) < 50:
                        continue
                    
                    # Tratar de centrar el snippet alrededor de la palabra clave
                    search_term = query.lower().split()[0] if query else ""
                    match = re.search(re.escape(search_term), clean_text, re.IGNORECASE)
                    
                    if match:
                        start_idx = max(0, match.start() - 300)
                        end_idx = min(len(clean_text), match.end() + 800)
                        snippet = clean_text[start_idx:end_idx]
                        if start_idx > 0: snippet = "..." + snippet
                        if end_idx < len(clean_text): snippet = snippet + "..."
                    else:
                        snippet = clean_text[:1000] + "..." if len(clean_text) > 1000 else clean_text
                        
                    collected_snippets.append(snippet)
                    ui_elements.append(
                        ui.div(
                            ui.div(
                                ui.HTML(f'<span style="background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 0.8rem;">{score*100:.1f}% de Similitud Semántica</span>'),
                                ui.HTML(f'<span style="background: rgba(6, 182, 212, 0.15); color: #06b6d4; border: 1px solid rgba(6, 182, 212, 0.4); padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 0.8rem; margin-left: 8px;">Página {page_num}</span>'),
                                style="margin-bottom: 12px; display: flex; align-items: center;"
                            ),
                            ui.markdown(snippet.strip()),
                            style="background:#161224; border-left:4px solid #a855f7; padding:20px; margin-bottom:15px; border-radius:8px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); color:#e5e0eb; font-size:0.95em; line-height:1.6;"
                        )
                    )
            
            if len(ui_elements) == 1:
                return ui.HTML(f"<div style='color:#f43f5e; padding:20px; background:#161224; border-radius:8px;'>No se encontraron coincidencias semánticas fuertes para '{query}'.</div>")
                
            # INYECCIÓN LLM: Explicar los fragmentos
            try:
                import providers
                import logic
                model = providers.DEFAULT_MODEL
                system_prompt = "Eres un analista experto. Lee los siguientes fragmentos judiciales que el usuario buscó. Escribe un resumen de máximo 2 párrafos explicando qué revelan estos fragmentos de manera clara, directa y fácil de entender. Sin saludos ni conclusiones genéricas."
                combined_context = "\n\n---\n\n".join(collected_snippets)
                
                ai_explanation = await logic.call_llm_async(model, system_prompt, f"Término buscado: '{query}'\n\nFragmentos:\n{combined_context}")
                
                # Actualizar el valor reactivo para el generador de PDF
                current_report_data.set({
                    "query": query,
                    "summary": ai_explanation,
                    "snippets": collected_snippets
                })
                
                explanation_box = ui.div(
                    ui.h5("Interpretación de la IA", style="color:#06b6d4; font-weight:bold; margin-bottom:10px;"),
                    ui.markdown(ai_explanation),
                    style="background:rgba(6, 182, 212, 0.1); border:1px solid #06b6d4; padding:20px; border-radius:8px; margin-bottom:15px; color:#e5e0eb; font-size:1.05em; line-height:1.6;"
                )
                
                # Insertar la explicación justo después del título
                ui_elements.insert(1, explanation_box)
            except Exception as e:
                print(f"Error en AI explanation: {e}")
                
            return ui.div(*ui_elements)
            
        except Exception as e:
            return ui.HTML(f"<div style='color:#f43f5e;'>Error en motor semántico: {str(e)}</div>")

    @render.ui
    def geospatial_map_ui():
        try:
            from map_generator import generate_geospatial_map
            map_html = generate_geospatial_map()
            return ui.HTML(f"<div style='border-radius:12px; overflow:hidden; border:1px solid rgba(168,85,247,0.5); box-shadow:0 10px 30px rgba(0,0,0,0.5);'>{map_html}</div>")
        except Exception as e:
            return ui.HTML(f"<div style='color:#f43f5e;'>Error renderizando mapa: {str(e)}</div>")

    @render.ui
    def shadow_network_ui():
        try:
            from network_generator import generate_shadow_network
            import html
            html_content = generate_shadow_network()
            escaped_html = html.escape(html_content)
            return ui.HTML(f"<iframe srcdoc='{escaped_html}' style='width:100%; height:650px; border:none; border-radius:12px; box-shadow:0 10px 30px rgba(0,0,0,0.5); background:#0b090f;'></iframe>")
        except Exception as e:
            return ui.HTML(f"<div style='color:#f43f5e;'>Error renderizando red: {str(e)}</div>")

    @render.download(
        filename=lambda: f"Reporte_Evidencia_{input.search_query().replace(' ', '_').replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    )
    def download_report():
        data = current_report_data.get()
        if not data:
            return ""
            
        metrics = {
            "Término Rastreado": str(data['query']),
            "Fragmentos Encontrados": str(len(data['snippets'])),
            "Clasificación": "ALTA PRIORIDAD / DOCUMENTO ANALIZADO POR IA"
        }
        
        filepath = generate_report(data['query'], data['summary'], data['snippets'], metrics)
        return filepath

    # --- DESCARGA: REPORTE DE AUDITORÍA ---
    @render.download(
        filename=lambda: f"Auditoria_{input.audit_target().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    )
    def download_audit_report():
        data = current_audit_data.get()
        if not data:
            return ""
        return generate_audit_report(data['target'], data['text'])

    # --- DESCARGA: REPORTE DEL DASHBOARD ---
    @render.download(
        filename=lambda: f"Reporte_Dashboard_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    )
    def download_dashboard_report():
        import json
        json_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "03 Procesamiento Anal\u00edtico", "analytic_report_full.json")
        )
        metrics_dict = {"Estado": "Datos no encontrados"}
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                metrics_dict = {
                    "Total de P\u00e1ginas Procesadas": str(data.get("total_paginas", 0)),
                    "Entidades Detectadas": str(data.get("total_entidades_unicas", 0)),
                    "Menciones Evasivas": str(data.get("total_menciones_evasivas", 0)),
                    "Frases Censuradas (Redacted)": str(data.get("total_frases_censuradas", 0)),
                }
        except Exception:
            pass
        return generate_dashboard_report(metrics_dict)

    # --- DESCARGA: REPORTE GEOESPACIAL ---
    @render.download(
        filename=lambda: f"Reporte_Geoespacial_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    )
    def download_geo_report():
        import pandas as pd
        csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "03 Procesamiento Anal\u00edtico", "geospatial_data.csv")
        )
        df = pd.read_csv(csv_path) if os.path.exists(csv_path) else pd.DataFrame()
        return generate_geo_report(df)

    # --- DESCARGA: REPORTE DE RED FINANCIERA ---
    @render.download(
        filename=lambda: f"Reporte_Red_Financiera_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    )
    def download_network_report():
        import pandas as pd
        csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "03 Procesamiento Anal\u00edtico", "financial_network_data.csv")
        )
        df = pd.read_csv(csv_path) if os.path.exists(csv_path) else pd.DataFrame()
        return generate_network_report(df)

    @render.ui
    @reactive.event(input.audit_btn)
    async def contradictions_results_ui():
        # Agente Lógico que evalúa contradicciones
        ui_loading = ui.HTML("""
        <div style='color:#06b6d4; padding:30px; text-align:center;'>
            <div style='font-size:2em; margin-bottom:15px;'></div>
            <div style='font-weight:bold;'>AGENTE LÓGICO INICIADO</div>
            <div style='color:#bfaec2; font-size:0.9em;'>Cruzando declaraciones de testigos... Evaluando inconsistencias temporales...</div>
        </div>
        """)
        
        # En una app de producción Shiny real, haríamos el yield del HTML, pero en @render.ui async
        # esperamos la respuesta de la IA.
        try:
            results = extraction_results()
            focus = input.audit_focus()
            target = input.audit_target()
            strictness = input.audit_strictness()
            
            context = "Contexto no disponible."
            if results and results.get("text"):
                full_text = results["text"]
                import re
                pages_raw = re.split(r'---\s*P[ÁA]GINA\s+\d+\s*---', full_text)
                pages = [p.strip() for p in pages_raw if p.strip()]
                
                if pages:
                    search_query = f"{focus} {target if target != 'Todos' else ''}"
                    from sklearn.feature_extraction.text import TfidfVectorizer
                    from sklearn.metrics.pairwise import cosine_similarity
                    
                    try:
                        vectorizer = TfidfVectorizer(stop_words='english', max_df=0.85)
                        tfidf_matrix = vectorizer.fit_transform(pages)
                        query_vec = vectorizer.transform([search_query])
                        similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
                        
                        top_indices = similarities.argsort()[-5:][::-1] # 5 páginas más relevantes
                        relevant_pages = [pages[idx] for idx in top_indices if similarities[idx] > 0.01]
                        
                        if relevant_pages:
                            # Limitar el contexto a unos ~12,000 caracteres para evitar limites de token
                            context_raw = "\n\n...[SALTO DE PÁGINA]...\n\n".join(relevant_pages)
                            context = context_raw[:12000]
                        else:
                            context = "No se encontraron fragmentos relevantes para auditar con esos parámetros."
                    except Exception as e:
                        print(f"Error de vectorización en auditor: {e}")
                        context = pages[0][:4000]
            
            system_prompt = (
                f"Eres un Agente Analítico de Inteligencia Lógica. Nivel de severidad: {strictness}. "
                f"Analiza el siguiente fragmento del expediente de Epstein y extrae ÚNICAMENTE contradicciones, mentiras probables o evasiones notorias. "
                f"Enfócate principalmente en: {focus}. "
            )
            if target != "Todos":
                system_prompt += f"Audita de manera rigurosa a: {target}. "
            
            system_prompt += "Sé directo, analítico y crudo. Usa viñetas breves."
            
            import providers
            model = providers.DEFAULT_MODEL
            response = await logic.call_llm_async(model, system_prompt, f"Analiza contradicciones en este texto:\n\n{context}")
            
            # Formatear la respuesta usando markdown a HTML básico o dejar que Shiny lo renderice
            return ui.div(
                ui.h4("Reporte de Auditoría de Contradicciones", style="color:#f43f5e; margin-bottom:15px; font-weight:bold;"),
                ui.div(
                    ui.markdown(response),
                    style="background:#161224; border:1px solid #f43f5e; padding:20px; border-radius:8px; color:#e5e0eb; font-size:1em; line-height:1.7;"
                )
            )
        except Exception as e:
            return ui.HTML(f"<div style='color:#f43f5e; padding:20px; background:#161224;'>Error del Agente: {str(e)}</div>")

import os
# Instanciar aplicación Shiny
app = App(app_ui, server, static_assets={"/": os.path.join(os.path.dirname(__file__), "www")})
