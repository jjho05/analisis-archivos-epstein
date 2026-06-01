# -*- coding: utf-8 -*-
"""
preprocessing.py
-------------------------------------------------------------------------
PASO 2: PREPROCESAMIENTO Y NORMALIZACIÓN DE EXPEDIENTES JUDICIALES
-------------------------------------------------------------------------
"""

import os
import re
import pypdf
import sys

def normalize_legal_text(text: str) -> str:
    """Aplica una limpieza profunda basada en expresiones regulares para actas legales.
    """
    if not text:
        return ""
    
    # 1. Unir palabras que se cortaron con guion al final de línea
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # 2. Reemplazar saltos de línea y tabuladores por espacios sencillos
    text = re.sub(r'[\n\r\t]+', ' ', text)
    
    # 3. Eliminar caracteres especiales manteniendo puntuación gramatical y tags básicos
    text = re.sub(r'[^\w\s\-\#\@\.\,\:\;]', '', text)
    
    # 4. Eliminar múltiples espacios en blanco consecutivos
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def main():
    print("=" * 70)
    print("INICIANDO PIPELINE DE PREPROCESAMIENTO ANALÍTICO (PASO 2) ")
    print("=" * 70)
    
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "01 Datasets Usados"))
    if not os.path.exists(dataset_dir):
        print(f"Error: La carpeta '{dataset_dir}' no existe.")
        print("Por favor, cree la carpeta y coloque los PDFs judiciales allí.")
        sys.exit(1)
        
    pdf_files = [f for f in os.listdir(dataset_dir) if f.endswith(".pdf")]
    if not pdf_files:
        print(f"Error: No se encontraron archivos PDF en '{dataset_dir}'.")
        sys.exit(1)
        
    # Seleccionamos el expediente principal (el más grande o el primero de la lista)
    pdf_files.sort(key=lambda x: os.path.getsize(os.path.join(dataset_dir, x)), reverse=True)
    selected_pdf = pdf_files[0]
    pdf_path = os.path.join(dataset_dir, selected_pdf)
    
    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"Archivo seleccionado para procesamiento: {selected_pdf} ({size_mb:.2f} MB)")
    
    try:
        reader = pypdf.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"Total de páginas detectadas: {total_pages}")
    except Exception as e:
        print(f"Error al abrir el PDF: {e}")
        sys.exit(1)
        
    # Se ha configurado para procesar la totalidad de las páginas (5,000+ páginas) del expediente judicial.
    limit_pages = total_pages
    print(f"Procesando y normalizando las {limit_pages} páginas totales del expediente...")
    
    consolidated_text = []
    
    for idx in range(limit_pages):
        try:
            raw_text = reader.pages[idx].extract_text() or ""
            cleaned_text = normalize_legal_text(raw_text)
            
            # Formato de salida estructurado
            page_block = f"--- PÁGINA {idx + 1} ---\n{cleaned_text}"
            consolidated_text.append(page_block)
            
            # Barra de progreso sencilla
            if (idx + 1) % 10 == 0 or (idx + 1) == limit_pages:
                percent = ((idx + 1) / limit_pages) * 100
                print(f"   [+] Progreso: {idx + 1}/{limit_pages} páginas ({percent:.1f}%)")
                
        except Exception as e:
            print(f"   [ Warning] Error procesando página {idx + 1}: {e}")
            
    # Guardar el texto plano consolidado
    output_filename = "consolidated_cleaned_text.txt"
    output_path = os.path.join(os.path.dirname(__file__), output_filename)
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n\n".join(consolidated_text))
        print("=" * 70)
        print("PIPELINE DE PREPROCESAMIENTO COMPLETADO")
        print(f"Archivo de texto plano guardado en: {output_path}")
        print(f"Páginas consolidadas: {limit_pages}  Caracteres totales: {sum(len(p) for p in consolidated_text):,}")
        print("=" * 70)
    except Exception as e:
        print(f"Error al guardar el archivo consolidado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
