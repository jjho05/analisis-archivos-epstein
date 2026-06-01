import os
import re

directories = ["02 Preprocesamiento", "03 Procesamiento Analítico", "04 Aplicacion Shiny", "."]

def replace_in_file(filepath):
    if not os.path.exists(filepath):
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    # Replace all caps
    new_content = new_content.replace('ANALÍTICO', 'ANALÍTICO')
    new_content = new_content.replace('ANALÍTICOS', 'ANALÍTICAS')
    new_content = new_content.replace('ANALYTIC', 'ANALYTIC')
    
    # Replace capitalized
    new_content = new_content.replace('Analítico', 'Analítico')
    new_content = new_content.replace('Analíticos', 'Analíticas')
    new_content = new_content.replace('Analytic', 'Analytic')
    
    # Replace lowercase
    new_content = new_content.replace('analítico', 'analítico')
    new_content = new_content.replace('analíticos', 'analíticas')
    new_content = new_content.replace('analytic', 'analytic')
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}")

for root, _, files in os.walk("."):
    for file in files:
        if file.endswith((".py", ".md", ".json", ".csv", ".txt")):
            if "consolidated_cleaned_text.txt" in file:
                continue # Do not modify raw source data
            if "requirements.txt" in file:
                continue
            filepath = os.path.join(root, file)
            replace_in_file(filepath)

