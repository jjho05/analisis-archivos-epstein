import os
from fpdf import FPDF
from datetime import datetime

class DossierPDF(FPDF):
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
        self.cell(0, 10, f"Documento Forense Generado Automáticamente | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Página {self.page_no()}/{{nb}}", align="C")

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

def generate_dossier(target_person, ai_summary, snippets, metrics_dict, output_dir="www/dossiers"):
    """
    Genera el PDF del dossier y retorna la ruta del archivo generado.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    pdf = DossierPDF()
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
        
    filename = f"Dossier_{target_person.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    
    return filepath
