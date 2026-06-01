import folium
from folium.plugins import MarkerCluster, HeatMap

import os
import pandas as pd

def generate_geospatial_map():
    # Leer datos geoespaciales desde el CSV estructurado
    csv_path = os.path.join(os.path.dirname(__file__), "geospatial_data.csv")
    df = pd.read_csv(csv_path)
    locations = df.to_dict('records')

    # Crear el mapa base con estilo oscuro forense
    m = folium.Map(location=[35.0, -50.0], zoom_start=3, tiles="CartoDB dark_matter")
    
    # Añadir HeatMap para mostrar intensidad visual
    heat_data = [[loc["lat"], loc["lon"], loc["mentions"]] for loc in locations]
    HeatMap(heat_data, radius=35, blur=25, gradient={0.4: '#a855f7', 0.6: '#06b6d4', 1: '#f43f5e'}).add_to(m)

    # Añadir marcadores interactivos
    for loc in locations:
        # Colores según tipo
        color = 'purple' if loc["type"] == "Isla Privada" else 'cyan'
        if loc["mentions"] > 1000: color = 'red'
        
        popup_html = f"""
        <div style="font-family: 'Space Grotesk', sans-serif; background: #161224; color: #e5e0eb; padding: 15px; border-radius: 8px; border: 1px solid #a855f7; width: 220px;">
            <h4 style="color: #06b6d4; margin-top: 0; font-weight: bold;">{loc['name']}</h4>
            <p style="margin: 5px 0;"><b>Tipo:</b> <span style="color:#f43f5e;">{loc['type']}</span></p>
            <p style="margin: 5px 0;"><b>Relevancia Judicial:</b> {loc['mentions']} menciones</p>
            <hr style="border-color: rgba(168, 85, 247, 0.3);">
            <p style="font-size: 0.85em; color: #bfaec2;">{loc['desc']}</p>
        </div>
        """
        
        folium.CircleMarker(
            location=[loc["lat"], loc["lon"]],
            radius=8,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"Ver Detalles: {loc['name']}",
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7
        ).add_to(m)
        
    # Trazar líneas de vuelo (Red Logística del 'Lolita Express')
    # Desde USVI a NY, Palm Beach, NM, Paris
    usvi = [18.3003, -64.8255]
    ny = [40.7736, -73.9566]
    pb = [26.7056, -80.0364]
    nm = [35.2500, -106.0167]
    paris = [48.8566, 2.3522]
    london = [51.5074, -0.1278]
    
    routes = [
        (usvi, ny), (usvi, pb), (ny, paris), (ny, london), (pb, nm), (usvi, paris)
    ]
    
    for route in routes:
        folium.PolyLine(
            route, 
            color="#a855f7", 
            weight=2, 
            opacity=0.6, 
            dash_array='5, 5',
            tooltip="Ruta de Vuelo Frecuente (Logística Documentada)"
        ).add_to(m)

    # Retornar el HTML del mapa
    return m._repr_html_()
