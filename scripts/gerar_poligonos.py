"""
Geração de Polígonos Convex Hull para Microáreas de UBS
Versão 3: Usa o CSV consolidado como fonte de dados
"""

import pandas as pd
import json
import math
from pathlib import Path

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Distância máxima em km para considerar um ponto como outlier
MAX_DISTANCIA_OUTLIER_KM = 5.0

# Dados das UBS: Localização e cores para visualização
UBS_INFO = {
    "Muciano Guajara": {
        "nome_completo": "UBS Muciano Cabral (Guajará)",
        "endereco": "Av. Principal, 515 - Guajará, Nossa Sra. do Socorro - SE",
        "latitude": -10.8860,
        "longitude": -37.1460,
        "cor": "#E63946",  # Vermelho
    },
    "Valter Rocha": {
        "nome_completo": "UBS Valter Rocha (Jardim Mariana)",
        "endereco": "Tv. 3 A Jd Mariana, 500 - Lot. Jardim Mariana, Nossa Sra. do Socorro - SE",
        "latitude": -10.8459,
        "longitude": -37.0522,
        "cor": "#1D3557",  # Azul escuro
    },
}


def distancia_km(p1, p2):
    """Calcula distância aproximada em km entre dois pontos (lon, lat)."""
    lat_media = (p1[1] + p2[1]) / 2
    km_por_grau_lat = 111.0
    km_por_grau_lon = 111.0 * math.cos(math.radians(lat_media))
    
    dlat = (p2[1] - p1[1]) * km_por_grau_lat
    dlon = (p2[0] - p1[0]) * km_por_grau_lon
    return math.sqrt(dlat**2 + dlon**2)


def calcular_centroide(points):
    """Calcula o centróide de um conjunto de pontos."""
    if not points:
        return None
    n = len(points)
    sum_lon = sum(p[0] for p in points)
    sum_lat = sum(p[1] for p in points)
    return (sum_lon / n, sum_lat / n)


def filtrar_outliers(points, max_dist_km=MAX_DISTANCIA_OUTLIER_KM):
    """Remove pontos que estão muito distantes do centróide."""
    if len(points) < 3:
        return points
    
    centroide = calcular_centroide(points)
    
    pontos_filtrados = []
    for p in points:
        dist = distancia_km(p, centroide)
        if dist <= max_dist_km:
            pontos_filtrados.append(p)
    
    return pontos_filtrados


def convex_hull(points):
    """
    Calcula o Convex Hull de um conjunto de pontos usando o algoritmo de Graham Scan.
    Retorna os pontos do polígono em ordem anti-horária.
    """
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
    points = list(set(points))
    
    if len(points) < 3:
        return points
    
    points = sorted(points)
    
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    
    return lower[:-1] + upper[:-1]


def main():
    base_dir = Path(__file__).parent.parent
    dados_dir = base_dir / "dados"
    
    # 1. Carregar CSV consolidado
    csv_path = dados_dir / "UBS_Ruas_Coordenadas_Consolidado.csv"
    df = pd.read_csv(csv_path)
    print(f"Carregados {len(df)} endereços do CSV consolidado")
    
    # 2. Filtrar apenas endereços com coordenadas válidas
    df_valido = df[df['latitude'].notna() & df['longitude'].notna()].copy()
    print(f"Endereços com coordenadas: {len(df_valido)}")
    
    # Mostrar resumo por método
    print("\n=== RESUMO POR MÉTODO ===")
    for metodo, count in df_valido['metodo'].value_counts().items():
        print(f"  {metodo}: {count}")
    
    # 3. Agrupar pontos por UBS e microárea
    all_points = {}
    
    for _, row in df_valido.iterrows():
        key = (row['ubs_referencia'], row['micro_area'])
        if key not in all_points:
            all_points[key] = []
        all_points[key].append((row['longitude'], row['latitude']))
    
    # 4. Gerar polígonos
    features = []
    linha_features = []
    
    for (ubs, micro_area), points in all_points.items():
        print(f"\n📍 {ubs} - Microárea {int(micro_area)}")
        print(f"   Pontos originais: {len(points)}")
        
        unique_points = list(set(points))
        print(f"   Pontos únicos: {len(unique_points)}")
        
        filtered_points = filtrar_outliers(unique_points)
        print(f"   Pontos após filtro: {len(filtered_points)}")
        
        if len(filtered_points) < 3:
            print(f"   ⚠️  Menos de 3 pontos, criando buffer")
            if len(filtered_points) == 1:
                lon, lat = filtered_points[0]
                buffer = 0.002
                hull_coords = [
                    [lon - buffer, lat - buffer],
                    [lon + buffer, lat - buffer],
                    [lon + buffer, lat + buffer],
                    [lon - buffer, lat + buffer],
                    [lon - buffer, lat - buffer],
                ]
            elif len(filtered_points) == 2:
                buffer = 0.001
                p1, p2 = filtered_points
                hull_coords = [
                    [p1[0] - buffer, p1[1] - buffer],
                    [p2[0] + buffer, p2[1] - buffer],
                    [p2[0] + buffer, p2[1] + buffer],
                    [p1[0] - buffer, p1[1] + buffer],
                    [p1[0] - buffer, p1[1] - buffer],
                ]
            else:
                continue
        else:
            hull = convex_hull(filtered_points)
            hull_coords = [list(p) for p in hull] + [list(hull[0])]
        
        # Obter cor da UBS
        ubs_cor = UBS_INFO.get(ubs, {}).get("cor", "#888888")
        
        # Feature de polígono
        feature = {
            "type": "Feature",
            "properties": {
                "ubs_referencia": ubs,
                "micro_area": int(micro_area),
                "num_ruas": len(points),
                "num_pontos_unicos": len(filtered_points),
                "cor": ubs_cor,
                "stroke": ubs_cor,
                "stroke-width": 2,
                "fill": ubs_cor,
                "fill-opacity": 0.3
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [hull_coords]
            }
        }
        features.append(feature)
        
        # Feature de linha (só arestas)
        linha_feature = {
            "type": "Feature",
            "properties": {
                "ubs_referencia": ubs,
                "micro_area": int(micro_area),
                "cor": ubs_cor,
                "stroke": ubs_cor,
                "stroke-width": 2
            },
            "geometry": {
                "type": "LineString",
                "coordinates": hull_coords
            }
        }
        linha_features.append(linha_feature)
        
        print(f"   ✅ Polígono gerado com {len(hull_coords)-1} vértices")
    
    # 5. Salvar GeoJSON de polígonos
    geojson = {
        "type": "FeatureCollection",
        "name": "microareas_ubs",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": features
    }
    
    output_path = dados_dir / "microareas_ubs.geojson"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Polígonos salvos em: {output_path}")
    
    # 6. Salvar GeoJSON de linhas
    linhas_geojson = {
        "type": "FeatureCollection",
        "name": "microareas_ubs_linhas",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": linha_features
    }
    
    linhas_path = dados_dir / "microareas_ubs_linhas.geojson"
    with open(linhas_path, "w", encoding="utf-8") as f:
        json.dump(linhas_geojson, f, ensure_ascii=False, indent=2)
    print(f"✅ Linhas salvas em: {linhas_path}")
    
    # 7. Criar GeoJSON agregado por UBS
    ubs_points = {}
    for (ubs, _), points in all_points.items():
        if ubs not in ubs_points:
            ubs_points[ubs] = []
        ubs_points[ubs].extend(points)
    
    ubs_features = []
    for ubs, points in ubs_points.items():
        unique_points = list(set(points))
        filtered_points = filtrar_outliers(unique_points)
        
        if len(filtered_points) >= 3:
            hull = convex_hull(filtered_points)
            hull_coords = [list(p) for p in hull] + [list(hull[0])]
            ubs_cor = UBS_INFO.get(ubs, {}).get("cor", "#888888")
            
            feature = {
                "type": "Feature",
                "properties": {
                    "ubs_referencia": ubs,
                    "num_microareas": len([k for k in all_points.keys() if k[0] == ubs]),
                    "num_ruas_total": len(points),
                    "cor": ubs_cor,
                    "stroke": ubs_cor,
                    "fill": ubs_cor,
                    "fill-opacity": 0.2
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [hull_coords]
                }
            }
            ubs_features.append(feature)
    
    ubs_geojson = {
        "type": "FeatureCollection",
        "name": "ubs_areas",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": ubs_features
    }
    
    ubs_output_path = dados_dir / "ubs_areas.geojson"
    with open(ubs_output_path, "w", encoding="utf-8") as f:
        json.dump(ubs_geojson, f, ensure_ascii=False, indent=2)
    print(f"✅ Áreas UBS salvas em: {ubs_output_path}")
    
    # 8. Criar GeoJSON com pontos das UBS
    ubs_pontos_features = []
    for ubs_nome, ubs_data in UBS_INFO.items():
        ponto_feature = {
            "type": "Feature",
            "properties": {
                "nome": ubs_data["nome_completo"],
                "ubs_referencia": ubs_nome,
                "endereco": ubs_data["endereco"],
                "cor": ubs_data["cor"],
                "marker-color": ubs_data["cor"],
                "marker-size": "large",
                "marker-symbol": "hospital"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [ubs_data["longitude"], ubs_data["latitude"]]
            }
        }
        ubs_pontos_features.append(ponto_feature)
    
    ubs_pontos_geojson = {
        "type": "FeatureCollection",
        "name": "ubs_pontos",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
        "features": ubs_pontos_features
    }
    
    ubs_pontos_path = dados_dir / "ubs_pontos.geojson"
    with open(ubs_pontos_path, "w", encoding="utf-8") as f:
        json.dump(ubs_pontos_geojson, f, ensure_ascii=False, indent=2)
    print(f"✅ Pontos das UBS salvos em: {ubs_pontos_path}")


if __name__ == "__main__":
    main()
