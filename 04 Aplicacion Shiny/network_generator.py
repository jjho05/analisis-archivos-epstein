import os
from pyvis.network import Network

def generate_shadow_network(output_dir="www/graphs"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    html_path = os.path.join(output_dir, "shadow_network.html")
    
    # Inicializar red PyVis (fondo oscuro y sin bordes)
    net = Network(height='100vh', width='100%', bgcolor='#0b090f', font_color='#e5e0eb')
    
    # Configurar física para que se vea orgánico e interactivo
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=150)
    
    import pandas as pd
    
    # Leer datos de la red financiera estructurada
    csv_path = os.path.join(os.path.dirname(__file__), "financial_network_data.csv")
    df = pd.read_csv(csv_path)
    
    # --- NODOS Y ARISTAS ---
    # Recolectar nodos únicos
    nodes = {}
    
    # Nodos especiales y sus configuraciones
    node_configs = {
        "Jeffrey Epstein": {"size": 35, "color": "#f43f5e", "desc": "Centro de Operaciones"},
        "J.P. Morgan Chase": {"size": 25, "color": "#06b6d4", "desc": "Banco Principal"},
        "Deutsche Bank": {"size": 22, "color": "#06b6d4", "desc": "Cuentas Off-shore"},
        "Wexner Foundation": {"size": 20, "color": "#a855f7", "desc": "Filantropía fachada"},
        "Financial Trust Co.": {"size": 20, "color": "#a855f7", "desc": "Fideicomiso corporativo"},
        "Liquid Funding Ltd.": {"size": 18, "color": "#a855f7", "desc": "Sociedad fantasma (LLC)"},
        "Southern Trust Co.": {"size": 18, "color": "#a855f7", "desc": "Entidad corporativa (USVI)"},
        "St. Thomas LLC": {"size": 15, "color": "#a855f7", "desc": "Propiedades marítimas"},
        "Darren Indyke": {"size": 22, "color": "#10b981", "desc": "Ejecutor legal"},
        "Richard Kahn": {"size": 20, "color": "#10b981", "desc": "Ejecutor financiero"},
        "Ghislaine Maxwell": {"size": 28, "color": "#f43f5e", "desc": "Operadora principal"},
        "Les Wexner": {"size": 25, "color": "#eab308", "desc": "Fuente de capital"}
    }
    
    for _, row in df.iterrows():
        source = row['source']
        target = row['target']
        
        if source not in nodes:
            cfg = node_configs.get(source, {"size": 15, "color": "#9ca3af", "desc": "Entidad vinculada"})
            net.add_node(source, size=cfg["size"], color=cfg["color"], title=cfg["desc"])
            nodes[source] = True
            
        if target not in nodes:
            cfg = node_configs.get(target, {"size": 15, "color": "#9ca3af", "desc": "Entidad vinculada"})
            net.add_node(target, size=cfg["size"], color=cfg["color"], title=cfg["desc"])
            nodes[target] = True
            
        # Añadir arista
        net.add_edge(source, target, color=row['color'], width=int(row['width']), title=row['type'])
        

    
    # Generar y guardar el HTML temporalmente para leerlo
    net.save_graph(html_path)
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    return html_content
