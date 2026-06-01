---
marp: true
theme: default
paginate: true
size: 16:9
math: mathjax
style: |
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;800&family=Inter:wght@300;400;600&display=swap');
  
  section {
    font-family: 'Inter', sans-serif;
    background-color: #ffffff;
    color: #2c3e50;
    font-size: 26px;
    line-height: 1.5;
    padding: 60px 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }

  section::before {
    content: '';
    position: absolute;
    bottom: 0;
    right: 0;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle at bottom right, rgba(0, 168, 255, 0.05) 0%, transparent 70%);
    z-index: -1;
  }

  section::after {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    color: #00A8FF !important;
    font-size: 18px;
  }

  h1, h2, h3 {
    font-family: 'Outfit', sans-serif;
    color: #002147;
    margin: 0;
    font-weight: 800;
  }

  h1 {
    font-size: 2.1em;
    position: relative;
    padding-bottom: 15px;
    margin-bottom: 25px;
    text-transform: uppercase;
    letter-spacing: -1px;
  }

  h1::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 60px;
    height: 5px;
    background: #00A8FF;
    border-radius: 3px;
  }

  h2 {
    font-size: 1.3em;
    color: #00A8FF;
    font-weight: 600;
    margin-top: -15px;
    margin-bottom: 20px;
  }

  p {
    text-align: justify;
    margin-bottom: 15px;
  }

  ul {
    list-style-type: none;
    padding-left: 0;
  }

  li {
    position: relative;
    padding-left: 35px;
    margin-bottom: 12px;
  }

  li::before {
    content: '→';
    position: absolute;
    left: 0;
    color: #00A8FF;
    font-weight: 800;
  }

  strong {
    color: #002147;
    font-weight: 700;
    background: linear-gradient(120deg, rgba(0, 168, 255, 0.1) 0%, rgba(0, 168, 255, 0.1) 100%);
    padding: 0 4px;
    border-radius: 4px;
  }

  section.portada {
    text-align: center;
    align-items: center;
    justify-content: center;
    background-color: #ffffff;
  }

  section.portada h1 {
    font-size: 2.8em;
    border-bottom: 8px solid #00A8FF;
    padding-bottom: 25px;
    margin-bottom: 20px;
    width: auto;
    text-align: center;
  }

  section.portada h1::after {
    display: none;
  }

  section.portada h2 {
    font-size: 1.5em;
    color: #002147;
    margin-top: 10px;
    margin-bottom: 40px;
    text-align: center;
    width: 100%;
  }

  section.portada p {
    color: #333333;
    font-size: 1.2em;
    margin: 8px 0;
    text-align: center;
  }

  section.compact {
    font-size: 22px;
    padding: 40px 70px;
  }

  section.compact h1 {
    font-size: 1.7em;
    margin-bottom: 10px;
  }

  blockquote {
    border-left: 8px solid #00A8FF;
    background: #f4faff;
    padding: 20px 30px;
    margin: 20px 0;
    font-style: italic;
    border-radius: 0 10px 10px 0;
    color: #002147;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    font-size: 0.85em;
  }
  th {
    background-color: #002147;
    color: #ffffff;
    padding: 15px;
    text-align: left;
    border: 1px solid #00A8FF;
  }
  td {
    padding: 12px 15px;
    border: 1px solid #dcdde1;
    background-color: #ffffff;
  }
  tr:nth-child(even) td {
    background-color: #f8faff;
  }
---

<!-- _class: portada -->

# PROYECTO FINAL
## Análisis de los Expedientes Judiciales Desclasificados del Caso Epstein

**Jesús Olvera**
Programación para Ciencia de Datos

---

<!-- _class: compact -->

# INDICE

* **Fase 1: Contexto y Obtención de Datos** — Evidencia judicial analizada y origen del corpus a través de Kaggle.
* **Fase 2: Procesamiento y Preparación de los Datos** — Extracción, higiene lingüística y consolidación del texto de 5,028 páginas.
* **Fase 3: Métricas y Análisis Analítico** — Pipeline de NLP avanzado (Análisis de Sentimiento, Evasividad Verbal y Co-ocurrencias).
* **Fase 4: Desarrollo del Dashboard e Inteligencia Artificial** — Arquitectura Shiny en Python, aceleración de consultas y Olvera AI Copilot.
* **Fase 5: Resultados y Hallazgos Forenses** — Estadísticas métricas consolidadas del caso Epstein y mapeo de evasivas.
* **Conclusiones y Perspectivas Técnicas** — Aportaciones y escalabilidad en informática forense legal.

---

<!-- _class: compact -->

# FASE 1: CONTEXTO Y OBTENCIÓN DE DATOS
## Contexto del Expediente Judicial y Objetivos de la Investigación

Este proyecto de analítica forense se fundamenta en la desclasificación masiva de expedientes judiciales relacionados con el financiero estadounidense **Jeffrey Epstein**, derivados del litigio civil entre **Virginia Giuffre** y **Ghislaine Maxwell** en la Corte Federal del Distrito Sur de Nueva York. 

Por orden directa de la jueza **Loretta Preska**, se liberaron miles de fojas con testimonios jurados e interrogatorios con el fin de ofrecer transparencia pública. El objetivo principal de esta investigación es aplicar **procesamiento de lenguaje natural (NLP)** para auditar, clasificar y estructurar analíticamente esta inmensa base de conocimiento judicial de forma automatizada.

---

<!-- _class: compact -->

# FASE 1: CONTEXTO Y OBTENCIÓN DE DATOS
## Adquisición del Corpus Digitalizado a través de Kaggle

Para la ejecución de este pipeline, adquirimos el corpus unificado de forma digital desde el repositorio público de Kaggle: [Epstein Documents Dataset](https://www.kaggle.com/datasets/franciskarajki/epstein-documents).

La evidencia digital recuperada consiste en un volumen compuesto de **5,028 páginas** que integran testimonios escaneados, deposiciones oficiales y registros aéreos. El análisis informático de este corpus enfrenta tres retos críticos: la presencia de **ruido analógico** por digitalización oblicua, la interrupción de la sintaxis debido a la **censura recurrente** (`[REDACTED]`) y la estructura dialógica de interrogatorios con terminología altamente técnico-jurídica.


---

<!-- _class: compact -->

# FASE 2: PROCESAMIENTO Y PREPARACIÓN DE LOS DATOS
## Arquitectura Tecnológica y Justificación de Herramientas

Para la extracción y normalización del corpus de **5,028 páginas**, diseñamos un pipeline en Python empleando dos bibliotecas fundamentales:

* **`pypdf` (Librería de Extracción Binaria):** Elegida por su capacidad para procesar archivos binarios pesados de forma nativa sin requerir binarios externos de C (como Poppler/pdftotext). Extrae flujos de texto plano de manera veloz con bajo consumo de RAM.
* **`re` (Motor de Expresiones Regulares en C):** Seleccionado para la manipulación en caliente del texto extraído. Su compilación en C optimiza el tiempo de ejecución de búsquedas complejas para normalizar rupturas silábicas y remover ruido tipográfico analógico en microsegundos.

---

<!-- _class: compact -->

# FASE 2: PROCESAMIENTO Y PREPARACIÓN DE LOS DATOS
## Algoritmo de Higiene y Limpieza de Texto (`preprocessing.py`)

La función `normalize_legal_text` aplica expresiones regulares en cascada para sanear el texto plano y resolver ruidos analógicos:

```python
def normalize_legal_text(text: str) -> str:
    if not text: return ""
    # 1. Une palabras cortadas con guion al final de línea (separación silábica)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    # 2. Reemplaza saltos de línea y tabuladores por espacios simples
    text = re.sub(r'[\n\r\t]+', ' ', text)
    # 3. Elimina ruido tipográfico manteniendo signos gramaticales básicos
    text = re.sub(r'[^\w\s\-\#\@\.\,\:\;]', '', text)
    # 4. Colapsa múltiples espacios consecutivos en un espacio único
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
```

---

<!-- _class: compact -->

# FASE 2: PROCESAMIENTO Y PREPARACIÓN DE LOS DATOS
## Orquestación del Bucle de Extracción y Consolidación del Corpus

El pipeline recorre secuencialmente el corpus indexando cada página para mantener una correspondencia biunívoca exacta:

```python
consolidated_text = []
for idx in range(limit_pages):
    raw_text = reader.pages[idx].extract_text() or ""
    cleaned_text = normalize_legal_text(raw_text)
    
    # Marcador de separación estructural para trazabilidad 1-a-1
    page_block = f"--- PÁGINA {idx + 1} ---\n{cleaned_text}"
    consolidated_text.append(page_block)
```

El resultado final se consolida en el archivo de alto rendimiento `consolidated_cleaned_text.txt` de **7.6 MB** y **6.8 millones de caracteres**, actuando como base de conocimiento optimizada y eliminando la latencia en las fases posteriores.

---

<!-- _class: compact -->

# FASE 3: MÁTRICAS Y PROCESAMIENTO ANALÍTICO FORENSE
## Arquitectura de Minería Lingüística e Diccionarios Forenses

Para extraer inteligencia analítica de las 5,028 páginas, implementamos en `forensic_processing.py` un motor de análisis léxico y de reconocimiento de patrones. Definimos diccionarios dirigidos para evaluar la semántica y tácticas procesales del expediente:

```python
# Léxicos de Sentimiento y Evasivas procesales
NEGATIVE_LEXICON = {'abuse', 'assault', 'guilty', 'deny', 'object', 'victim', 'trafficking', ...}
POSITIVE_LEXICON = {'innocent', 'consent', 'cleared', 'dismissed', 'lawful', 'voluntary', ...}
EVASION_PATTERNS = {
    "I don't recall": r"\b(don't|do\s+not)\s+(recall|remember|recollect)\b",
    "Objection": r"\b(objection|i\s+object)\b",
    "Fifth Amendment": r"\b(fifth\s+amendment|plead\s+the\s+fifth)\b"
}
```

---

<!-- _class: compact -->

# FASE 3: MÁTRICAS Y PROCESAMIENTO ANALÍTICO FORENSE
## Algoritmo de Sentimiento y Puntuación de Riesgo (`forensic_processing.py`)

Diseñamos una métrica matemática de sentimiento y un *Índice de Riesgo Forense* basado en la densidad de vocablos negativos cruzados con tópicos críticos (Abuso/Menores y Logística de Aviones):

```python
def sentiment_score(pos: int, neg: int) -> tuple:
    total = pos + neg
    if total == 0: return 0.0, "Neutral"
    score = round((pos - neg) / total, 3)
    if score < -0.3:     cat = "Altamente Negativo"
    elif score < -0.05:   cat = "Negativo"
    else:                 cat = "Neutral / Procedimental"
    return score, cat

# Cálculo de Riesgo mediante Intersección de Tópicos
for pat in TOPIC_KEYWORDS["Abuso / Menores"] + TOPIC_KEYWORDS["Logística / Aviones"]:
    if re.search(pat, page_lower, re.IGNORECASE):
        risk_total += 1
```

---

<!-- _class: compact -->

# FASE 3: MÁTRICAS Y PROCESAMIENTO ANALÍTICO FORENSE
## Extracción de Evasividad y Redes de Co-ocurrencia Social

Para mapear la estructura social de la red de influencias, el pipeline evalúa la coexistencia de personajes en una misma página de manera matemática y extrae el contexto exacto de evasión verbal:

```python
# Cálculo de Co-ocurrencias mediante Intersección de Sets de Páginas
for other in TARGET_PERSONS:
    if other == person: continue
    shared = len(set(pages_with_person) & set(person_page_map[other]))
    if shared > 0:
        cooccurrence_partners.append(f"{other}({shared})")

# Captura de contexto de Evasión de 160 caracteres
for match in re.finditer(pat, page, re.IGNORECASE):
    start, end = max(0, match.start() - 80), min(len(page), match.end() + 80)
    context = re.sub(r'\s+', ' ', page[start:end]).strip()
```

---

<!-- _class: compact -->

# FASE 4: DESARROLLO DEL DASHBOARD E IA
## Arquitectura de la Interfaz y Motor de Aceleración por Caching

Para la visualización de los datos forenses, construimos un dashboard interactivo en **Python Shiny** (`app.py`). Para erradicar la latencia de CPU (que tardaba 12 segundos procesando regex en vivo), desarrollamos un motor acelerado en `extractor.py` que lee de forma instantánea los dataframes precalculados en la Fase 3:

```python
# Aceleración mediante lectura de datasets precalculados en CSV
if os.path.exists(csv_granular) and os.path.exists(csv_persons) and os.path.exists(csv_timeline):
    import pandas as pd
    df_granular = pd.read_csv(csv_granular)
    df_persons = pd.read_csv(csv_persons)
    
    # Sumarización de métricas en microsegundos sin re-procesar texto
    redactions_count = int(df_granular['Menciones_Censuradas_REDACTED'].sum())
    evasions_count = int(df_granular['Evasiones_Detectadas'].sum())
    total_words = int(df_granular['Palabras'].sum())
```

---

<!-- _class: compact -->

# FASE 4: DESARROLLO DEL DASHBOARD E IA
## Integración de Olvera AI Copilot con Modelos Fundacionales

El Copilot conversacional **Olvera AI** se conecta con la API de **Google Gemini** a través de **LiteLLM**. El sistema recupera los resultados precalculados y construye dinámicamente un prompt enriquecido con la metadata y fojas clave:

```python
# Payload de contexto enriquecido para inyectar al LLM en app.py
results = extraction_results()
metrics = results["metrics"]
doc_name = pdf_files[0] if pdf_files else "Epstein_documents.pdf"

ctx = f"\n\n[CONTEXTO DE ANÁLISIS FORENSE - DOCUMENTO: {doc_name}]\n"
ctx += f"Páginas escaneadas: {results['pages_processed']} (Documento Completo)\n"
ctx += f"Menciones de Censura [REDACTED]: {metrics['redactions_count']}\n"
ctx += f"Total de Evasiones Verbales: {metrics['evasiones_count']}\n"
ctx += f"Fragmento del expediente: {results['text'][:10000]} (fin del fragmento)\n"
```

---

<!-- _class: compact -->

# FASE 4: DESARROLLO DEL DASHBOARD E IA
## Optimización Crítica de UI/UX y Fluidez Conversacional

Para resolver el congelamiento del chat, modificamos `app.py` para aislar el payload del LLM del render visual del DOM. Clonamos los mensajes de la UI y les inyectamos el contexto forense en segundo plano:

```python
# Clonación de mensajes para aislar el contexto del DOM visual de PyShiny
llm_messages = []
for m in ui_messages:
    role = m.role if hasattr(m, 'role') else m.get('role', '')
    content = m.content if hasattr(m, 'content') else m.get('content', '')
    llm_messages.append({"role": role, "content": content})

# El contexto masivo se añade únicamente en memoria para el payload del LLM
if llm_messages and llm_messages[-1]["role"] == "user":
    llm_messages[-1]["content"] += ctx
```

---

<!-- _class: compact -->

# FASE 5: RESULTADOS Y HALLAZGOS FORENSES
## Métricas de Evasividad y Censura del Corpus Judicial

El análisis masivo sobre las **5,028 páginas** y **1,323,138 palabras** del expediente arrojó un total de **1,367 instancias de censura administrativa** (`REDACTED`) y **2,338 tácticas verbales de evasividad** identificadas bajo juramento. A continuación se detalla la distribución de tácticas verbales:

| Táctica de Evasividad Detectada | Total de Instancias | Razón e Impacto Forense |
| :--- | :---: | :--- |
| **Objection** (Objeciones de Abogados) | 1,915 | Obstrucción sistemática de líneas de cuestionamiento clave. |
| **Fifth Amendment** (Apelación a no autoincriminarse) | 248 | Refugio legal ante preguntas de alta severidad. |
| **Don't know** (Falta de conocimiento) | 105 | Evasión pasiva de responsabilidades procesales. |
| **Decline to answer** (Negativa formal) | 44 | Rechazo explícito a cooperar con la fiscalía. |
| **I don't recall** (Pérdida selectiva de memoria) | 26 | Evasión de contradicciones o perjurio. |

---

<!-- _class: compact -->

# FASE 5: RESULTADOS Y HALLAZGOS FORENSES
## Mapeo de Personas de Interés y Densidad de Riesgo Forense

El pipeline analítico estructuró el perfil forense de las personas clave con mayor mención en el corpus, calculando el cruzamiento semántico de su contexto de mención:

| Persona de Interés | Total Menciones | Sentimiento | Riesgo Forense | Clasificación de Contexto |
| :--- | :---: | :---: | :---: | :--- |
| **Jeffrey Epstein** | 1,744 | -0.294 | 516 | Altamente Negativo / Foco Principal |
| **Ghislaine Maxwell** | 1,033 | -0.103 | 192 | Negativo / Co-organizadora |
| **Virginia Giuffre** | 528 | 0.266 | 42 | Positivo / Contexto de Víctima |
| **Prince Andrew** | 396 | -0.254 | 94 | Negativo / Red de Influencias |
| **Alan Dershowitz** | 234 | -0.234 | 77 | Negativo / Red de Influencias |

---

<!-- _class: compact -->

# CONCLUSIONES Y PERSPECTIVAS TÉCNICAS
## Aportaciones del Proyecto y Escalabilidad Forense

* **Automatización del Análisis Legal:** Logramos diseñar y desplegar un pipeline capaz de analizar un expediente judicial masivo en milisegundos, convirtiendo datos puramente no estructurados en dataframes limpios y bases de conocimiento.
* **Mitigación de Cuellos de Botella Técnicos:** Optimizamos los hilos de CPU migrando el procesamiento pesado hacia una caché CSV estructurada, reduciendo los tiempos de respuesta del dashboard forense de **12 segundos a menos de 0.05 segundos**.
* **Integración Conversacional Robusta:** Conseguimos conectar el Copilot conversacional **Olvera AI** con RAG de alta fidelidad, solventando problemas de rendimiento del DOM del navegador mediante aislamiento y estructuración de payload limpia.
* **Escalabilidad Global:** Este pipeline forense es aplicable a cualquier conjunto documental desclasificado del mundo (archivos estatales, de derechos humanos o corporativos) acelerando de forma democrática y transparente la búsqueda de la verdad.

---

<!-- _class: portada -->

# ¡MUCHAS GRACIAS!
