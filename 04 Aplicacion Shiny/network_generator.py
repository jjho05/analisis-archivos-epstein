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
    
    # --- NODOS ---
    # Nivel 0: El Centro
    net.add_node("Jeffrey Epstein", size=35, color="#f43f5e", title="Centro de Operaciones", font={"size": 20, "color": "white", "weight": "bold"})
    
    # Nivel 1: Facilitadores Financieros e Instituciones
    institutions = [
        ("J.P. Morgan Chase", "#06b6d4", "Banco Principal (Flujos millonarios)", 25),
        ("Deutsche Bank", "#06b6d4", "Cuentas Off-shore y Préstamos", 22),
        ("Wexner Foundation", "#a855f7", "Origen de fondos iniciales y filantropía fachada", 20),
        ("Financial Trust Co.", "#a855f7", "Fideicomiso corporativo en Islas Vírgenes", 20),
        ("Liquid Funding Ltd.", "#a855f7", "Sociedad fantasma (LLC) para evasión", 18),
        ("Southern Trust Co.", "#a855f7", "Entidad corporativa de ocultamiento (USVI)", 18),
        ("St. Thomas LLC", "#a855f7", "Adquisición de propiedades marítimas", 15)
    ]
    for name, color, desc, size in institutions:
        net.add_node(name, size=size, color=color, title=desc)
        
    # Nivel 2: Abogados y Contadores (Cómplices Legales/Financieros)
    facilitators = [
        ("Darren Indyke", "#10b981", "Abogado Principal y ejecutor de fideicomisos", 22),
        ("Richard Kahn", "#10b981", "Contador (Manejo de flujo de efectivo no rastreable)", 20),
        ("Ghislaine Maxwell", "#f43f5e", "Reclutadora y Operadora de pagos en efectivo", 28),
        ("Les Wexner", "#eab308", "Multimillonario (Principal fuente de capital)", 25)
    ]
    for name, color, desc, size in facilitators:
        net.add_node(name, size=size, color=color, title=desc)

    # --- ARISTAS (Conexiones) ---
    # Conectar a Epstein
    for name, _, _, _ in institutions + facilitators:
        net.add_edge("Jeffrey Epstein", name, color="#3f3f46", width=2)
        
    # Interconexiones corporativas
    net.add_edge("Darren Indyke", "Financial Trust Co.", color="#10b981", width=3)
    net.add_edge("Darren Indyke", "Southern Trust Co.", color="#10b981", width=3)
    net.add_edge("Richard Kahn", "Liquid Funding Ltd.", color="#10b981", width=2)
    net.add_edge("Ghislaine Maxwell", "Wexner Foundation", color="#a855f7", width=1)
    net.add_edge("Les Wexner", "Wexner Foundation", color="#eab308", width=4)
    net.add_edge("Les Wexner", "Jeffrey Epstein", color="#eab308", width=3)
    
    net.add_edge("J.P. Morgan Chase", "Financial Trust Co.", color="#06b6d4", width=4)
    net.add_edge("Deutsche Bank", "Southern Trust Co.", color="#06b6d4", width=3)
    net.add_edge("Darren Indyke", "St. Thomas LLC", color="#10b981", width=2)
    
    # Generar y guardar el HTML temporalmente para leerlo
    net.save_graph(html_path)
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    return html_content
