import os
from fpdf import FPDF
from datetime import datetime

class ReportPDF(FPDF):
    def header(self):
        # Fondo oscuro para el encabezado (simulando la app)
        self.set_fill_color(11, 9, 15) # #0b090f
        self.rect(0, 0, 210, 35, 'F')
        
        # Título principal
        self.set_font("helvetica", "B", 20)
        self.set_text_color(168, 85, 247) # Púrpura brillante
        self.set_y(10)
        self.cell(0, 10, "REPORTE DE ANÁLISIS DE EVIDENCIA", border=0, align="L", new_x="LMARGIN", new_y="NEXT")
        
        # Subtítulo
        self.set_font("helvetica", "I", 11)
        self.set_text_color(229, 224, 235)
        self.cell(0, 6, "Sistema Analítico Desclasificado", border=0, align="L", new_x="LMARGIN", new_y="NEXT")
        
        # Línea separadora
        self.set_draw_color(6, 182, 212) # Cyan
        self.set_line_width(0.8)
        self.line(10, 32, 200, 32)
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Documento Forense Generado Automáticamente  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  Página {self.page_no()}/{{nb}}", align="C")

    def chapter_title(self, title, color=(6, 182, 212)):
        self.set_font("helvetica", "B", 14)
        self.set_text_color(*color)
        self.set_fill_color(240, 240, 245)
        self.cell(0, 10, f" {title.upper()}", border=0, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(3)

    def chapter_body(self, text):
        self.set_font("helvetica", "", 10)
        self.set_text_color(40, 40, 40)
        
        # Sanitizar texto para la fuente estándar (evita errores con emojis o caracteres raros)
        safe_text = text.encode('latin-1', 'ignore').decode('latin-1')
        
        self.multi_cell(0, 6, safe_text)
        self.ln(5)
        
    def add_metric_box(self, title, value):
        self.set_font("helvetica", "B", 10)
        self.set_text_color(168, 85, 247)
        self.cell(60, 8, title + ": ", border=0)
        
        self.set_font("helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        safe_val = str(value).encode('latin-1', 'ignore').decode('latin-1')
        self.cell(0, 8, safe_val, border=0, new_x="LMARGIN", new_y="NEXT")

def generate_report(target_person, ai_summary, snippets, metrics_dict, output_dir="www/reports"):
    """Genera el PDF del reporte y retorna la ruta del archivo generado.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Sección 1: Objetivo
    pdf.chapter_title("1. PERFIL DE OBJETIVO E INVESTIGACIÓN")
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Sujeto/Tema de Interés: {target_person.upper()}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    for k, v in metrics_dict.items():
        pdf.add_metric_box(k, v)
    pdf.ln(5)
    
    # Sección 2: Resumen Ejecutivo
    pdf.chapter_title("2. SÍNTESIS DE LA INVESTIGACIÓN", color=(168, 85, 247))
    pdf.chapter_body(ai_summary)
    
    # Sección 3: Fragmentos Evidenciales
    pdf.chapter_title("3. EXTRACTOS JUDICIALES CRUDOS (EVIDENCIA DIRECTA)")
    
    for idx, snip in enumerate(snippets):
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, f"--- Fragmento {idx+1} ---", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_fill_color(250, 250, 250)
        pdf.set_font("courier", "", 9)
        pdf.set_text_color(20, 20, 20)
        
        safe_snip = snip.encode('latin-1', 'ignore').decode('latin-1')
        # Limpiar saltos dobles innecesarios
        safe_snip = safe_snip.replace('\n\n', '\n')
        pdf.multi_cell(0, 5, safe_snip, border=1, fill=True)
        pdf.ln(4)
        
    filename = f"Reporte_{target_person.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    
    return filepath

def generate_audit_report(target_person, analysis_text, output_dir="www/reports"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.chapter_title("1. AUDITORÍA LÓGICA DE CONTRADICCIONES", color=(244, 63, 94)) # Rojo (alerta)
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Sujeto Analizado: {target_person.upper()}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.chapter_title("2. RESULTADOS DEL AGENTE", color=(244, 63, 94))
    
    # Análisis de texto
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    safe_text = analysis_text.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 6, safe_text)
    
    filename = f"Auditoria_{target_person.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath

def generate_dashboard_report(metrics_dict, output_dir="www/reports"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.chapter_title("RESUMEN DE MÉTRICAS GLOBALES", color=(16, 185, 129)) # Verde
    pdf.ln(5)
    
    for k, v in metrics_dict.items():
        pdf.add_metric_box(k, v)
    
    filename = f"Dashboard_Metricas_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath

def generate_network_report(df_network, output_dir="www/reports"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.chapter_title("ESTRUCTURA DE RED CORPORATIVA FINANCIERA", color=(168, 85, 247))
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(60, 8, "Entidad Origen", border=1, fill=True)
    pdf.cell(60, 8, "Entidad Destino", border=1, fill=True)
    pdf.cell(70, 8, "Tipo de Vínculo", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 9)
    for _, row in df_network.iterrows():
        src = str(row.get('source', '')).encode('latin-1', 'ignore').decode('latin-1')
        tgt = str(row.get('target', '')).encode('latin-1', 'ignore').decode('latin-1')
        typ = str(row.get('type', '')).encode('latin-1', 'ignore').decode('latin-1')
        pdf.cell(60, 8, src[:30], border=1)
        pdf.cell(60, 8, tgt[:30], border=1)
        pdf.cell(70, 8, typ[:35], border=1, new_x="LMARGIN", new_y="NEXT")
        
    filename = f"Red_Financiera_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath

def generate_geo_report(df_geo, output_dir="www/reports"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    pdf = ReportPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.chapter_title("INTELIGENCIA GEOESPACIAL: LOCACIONES CLAVE", color=(16, 185, 129))
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.set_fill_color(220, 220, 220)
    pdf.cell(60, 8, "Locación", border=1, fill=True)
    pdf.cell(30, 8, "Tipo", border=1, fill=True)
    pdf.cell(25, 8, "Menciones", border=1, fill=True)
    pdf.cell(75, 8, "Descripción", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 8)
    for _, row in df_geo.iterrows():
        name = str(row.get('name', '')).encode('latin-1', 'ignore').decode('latin-1')
        t = str(row.get('type', '')).encode('latin-1', 'ignore').decode('latin-1')
        m = str(row.get('mentions', ''))
        d = str(row.get('desc', '')).encode('latin-1', 'ignore').decode('latin-1')
        
        # Guardar posición Y para MultiCell
        start_y = pdf.get_y()
        # Verificar salto de página
        if start_y > 250:
            pdf.add_page()
            start_y = pdf.get_y()
            
        pdf.cell(60, 10, name[:35], border=1)
        pdf.cell(30, 10, t[:15], border=1)
        pdf.cell(25, 10, m, border=1)
        # Use simple cell for desc instead of multicell for simplicity in the table
        pdf.cell(75, 10, d[:50] + "...", border=1, new_x="LMARGIN", new_y="NEXT")

    filename = f"Geoespacial_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath
