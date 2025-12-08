"""
Geração de Polígonos Convex Hull para Microáreas de UBS
Consolida dados geocodificados e gera GeoJSON para QGIS
"""

import pandas as pd
import json
from pathlib import Path

# ============================================================================
# COORDENADAS OBTIDAS VIA WEB SEARCH (endereços que falharam no Nominatim)
# ============================================================================

COORDENADAS_WEBSEARCH = [
    # UBS Muciano Guajara - Microárea 32
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua 12 de Fevereiro", "latitude": -10.8531643, "longitude": -37.1269791},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Travessa Quissamã", "latitude": -10.9007348, "longitude": -37.1540443},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua 1 de Fevereiro", "latitude": -10.89845, "longitude": -37.15609},  # coords do bairro Guajará
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Avenida Chesf 01", "latitude": -10.893889, "longitude": -37.1575},  # coords do bairro Guajará
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Avenida Quissamã", "latitude": -10.9007348, "longitude": -37.1540443},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Avenida Chesf", "latitude": -10.893889, "longitude": -37.1575},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua do Tanque", "latitude": -10.893889, "longitude": -37.1575},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua da Fazenda", "latitude": -10.893889, "longitude": -37.1575},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua C (São Benedito)", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua D (São Benedito)", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua E (São Benedito)", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua 10 de Janeiro", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua 11 de Janeiro", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua 12 de Janeiro", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua 13 de Janeiro", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Rua 14 de Janeiro", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 32, "endereco": "Praça 16 de Janeiro", "latitude": -10.89845, "longitude": -37.15609},
    
    # UBS Muciano Guajara - Microárea 9
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Existente", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Travessa Padre Cícero", "latitude": -10.8983621, "longitude": -37.1568275},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Otto", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Profeta Eliseu", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Jorge Amado", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua J. Emílio de Carvalho", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Joze Aloisio da Silva", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Antonio Torres", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Travessa Jucelino Emilio", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Ezequiel Cardoso", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Projetada", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Travessa Agepino", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Almeida Fraga", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Travessa Santa Bárbara", "latitude": -10.8988931, "longitude": -37.1449513},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Colonial", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Odálio Golveia", "latitude": -10.89845, "longitude": -37.15609},
    {"ubs_referencia": "Muciano Guajara", "micro_area": 9, "endereco": "Rua Bela Vista", "latitude": -10.89845, "longitude": -37.15609},
    
    # UBS Valter Rocha - Microárea 1
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Aramuru", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Caete", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Caxico", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Karapato", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Pataco", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Av. Tomoio", "latitude": -10.8491378, "longitude": -37.0541272},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Tapuia", "latitude": -10.8484291, "longitude": -37.0545519},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Tupinamba", "latitude": -10.8485457, "longitude": -37.0534716},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Xoco Guara", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Xingú", "latitude": -10.8489299, "longitude": -37.0523701},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Espirito Santo", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Av. Florionopolis", "latitude": -10.8494277, "longitude": -37.0710716},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Mato Grosso", "latitude": -10.8601494, "longitude": -37.0496621},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Travessa Mato Grosso", "latitude": -10.8601494, "longitude": -37.0496621},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Rua Santa Catarina", "latitude": -10.8531544, "longitude": -37.1270097},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Av. Curitiba", "latitude": -10.8514372, "longitude": -37.0727555},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Travessa Curitiba", "latitude": -10.8514372, "longitude": -37.0727555},
    {"ubs_referencia": "Valter Rocha", "micro_area": 1, "endereco": "Av. Eng. Galvão", "latitude": -10.8531544, "longitude": -37.1270097},
    
    # UBS Valter Rocha - Microárea 2
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Rua Parana", "latitude": -10.8531544, "longitude": -37.1270097},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Rua Porto Alegre", "latitude": -10.8531544, "longitude": -37.1270097},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Rua Rio de Janeiro", "latitude": -10.8529, "longitude": -37.0515},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Rua Sao Paulo", "latitude": -10.8599071, "longitude": -37.0914183},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Av. Engenheiro Luciano Santana Gaalvão", "latitude": -10.8531544, "longitude": -37.1270097},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Rua 05", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Travessa 19", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Travessa 17", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Rua Espirito Santo", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Rua Goias", "latitude": -10.8484291, "longitude": -37.0545519},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Rua Mato Grosso", "latitude": -10.8601494, "longitude": -37.0496621},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Travessa 16", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Travessa Maria Freire", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Travessa 20", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Rua A (Jardim Esperança)", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 2, "endereco": "Rua B (Jardim Esperança)", "latitude": -10.84992, "longitude": -37.05153},
    
    # UBS Valter Rocha - Microárea 3
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Rua 09", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Rua 03", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Rua 02", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Rua 01", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Rua Distrito Federal", "latitude": -10.8531544, "longitude": -37.1270097},
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Rua Minas Gerais", "latitude": -10.8531544, "longitude": -37.1270097},
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Rua Goias", "latitude": -10.8484291, "longitude": -37.0545519},
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Av. Curitiba", "latitude": -10.8514372, "longitude": -37.0727555},
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Av. Florionopolis", "latitude": -10.8494277, "longitude": -37.0710716},
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Rua Mato Grosso", "latitude": -10.8601494, "longitude": -37.0496621},
    {"ubs_referencia": "Valter Rocha", "micro_area": 3, "endereco": "Rua Mato Grosso do Sul", "latitude": -10.8532965, "longitude": -37.0550138},
    
    # UBS Valter Rocha - Microárea 4
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua Tapuia", "latitude": -10.8484291, "longitude": -37.0545519},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua Kariri-Xoco", "latitude": -10.8503197, "longitude": -37.0545200},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua Novo Acesso", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Av. Tupiniquins", "latitude": -10.8500450, "longitude": -37.0552734},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Av. Tamoio", "latitude": -10.8491378, "longitude": -37.0541272},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua Potiguara", "latitude": -10.8495149, "longitude": -37.0551425},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua 07", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua 08", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua 09", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua 10", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua 11", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua 12", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua 13", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua 14", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua 15", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua Bras", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua Diego Emerson", "latitude": -10.84992, "longitude": -37.05153},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Av. Eng. Luciano Galvão", "latitude": -10.8531544, "longitude": -37.1270097},
    {"ubs_referencia": "Valter Rocha", "micro_area": 4, "endereco": "Rua D3", "latitude": -10.84992, "longitude": -37.05153},
]

def convex_hull(points):
    """
    Calcula o Convex Hull de um conjunto de pontos usando o algoritmo de Graham Scan.
    Retorna os pontos do polígono em ordem anti-horária.
    """
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
    # Remove duplicatas
    points = list(set(points))
    
    if len(points) < 3:
        return points
    
    # Ordena por x, depois por y
    points = sorted(points)
    
    # Constrói a parte inferior
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    
    # Constrói a parte superior
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    
    # Remove o último ponto de cada metade (é repetido)
    return lower[:-1] + upper[:-1]


def main():
    # Diretório base
    base_dir = Path(__file__).parent.parent
    dados_dir = base_dir / "dados"
    
    # 1. Carregar dados do Nominatim OK
    nominatim_ok = pd.read_csv(dados_dir / "UBS_Ruas_Nominatim_OK.csv")
    print(f"Carregados {len(nominatim_ok)} endereços geocodificados pelo Nominatim")
    
    # 2. Criar DataFrame com coordenadas da web search
    websearch_df = pd.DataFrame(COORDENADAS_WEBSEARCH)
    print(f"Adicionados {len(websearch_df)} endereços geocodificados via Web Search")
    
    # 3. Consolidar todos os pontos por UBS e microárea
    all_points = {}
    
    # Processar dados do Nominatim
    for _, row in nominatim_ok.iterrows():
        key = (row['ubs_referencia'], row['micro_area'])
        if key not in all_points:
            all_points[key] = []
        all_points[key].append((row['longitude'], row['latitude']))
    
    # Processar dados da Web Search
    for _, row in websearch_df.iterrows():
        key = (row['ubs_referencia'], row['micro_area'])
        if key not in all_points:
            all_points[key] = []
        all_points[key].append((row['longitude'], row['latitude']))
    
    # 4. Gerar GeoJSON com polígonos Convex Hull
    features = []
    
    for (ubs, micro_area), points in all_points.items():
        # Remove duplicatas
        unique_points = list(set(points))
        
        if len(unique_points) < 3:
            print(f"⚠️  {ubs} - Microárea {micro_area}: apenas {len(unique_points)} pontos únicos, usando buffer circular")
            # Para menos de 3 pontos, criar um buffer circular aproximado
            if len(unique_points) == 1:
                lon, lat = unique_points[0]
                # Criar um quadrado pequeno ao redor do ponto
                buffer = 0.002  # ~200m
                hull_coords = [
                    [lon - buffer, lat - buffer],
                    [lon + buffer, lat - buffer],
                    [lon + buffer, lat + buffer],
                    [lon - buffer, lat + buffer],
                    [lon - buffer, lat - buffer],  # Fechar o polígono
                ]
            elif len(unique_points) == 2:
                # Criar um retângulo fino entre os dois pontos
                buffer = 0.001
                p1, p2 = unique_points
                hull_coords = [
                    [p1[0] - buffer, p1[1] - buffer],
                    [p2[0] + buffer, p2[1] - buffer],
                    [p2[0] + buffer, p2[1] + buffer],
                    [p1[0] - buffer, p1[1] + buffer],
                    [p1[0] - buffer, p1[1] - buffer],
                ]
        else:
            # Calcular Convex Hull
            hull = convex_hull(unique_points)
            # Fechar o polígono (GeoJSON requer que o primeiro e último ponto sejam iguais)
            hull_coords = [list(p) for p in hull] + [list(hull[0])]
        
        feature = {
            "type": "Feature",
            "properties": {
                "ubs_referencia": ubs,
                "micro_area": int(micro_area),
                "num_ruas": len(points),
                "num_pontos_unicos": len(unique_points)
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [hull_coords]
            }
        }
        features.append(feature)
        print(f"✓ {ubs} - Microárea {micro_area}: {len(unique_points)} pontos únicos → polígono gerado")
    
    # 5. Criar FeatureCollection
    geojson = {
        "type": "FeatureCollection",
        "name": "microareas_ubs",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": features
    }
    
    # 6. Salvar GeoJSON
    output_path = dados_dir / "microareas_ubs.geojson"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ GeoJSON salvo em: {output_path}")
    print(f"   Total de polígonos: {len(features)}")
    
    # 7. Criar também um GeoJSON agregado por UBS (união das microáreas)
    ubs_points = {}
    for (ubs, _), points in all_points.items():
        if ubs not in ubs_points:
            ubs_points[ubs] = []
        ubs_points[ubs].extend(points)
    
    ubs_features = []
    for ubs, points in ubs_points.items():
        unique_points = list(set(points))
        if len(unique_points) >= 3:
            hull = convex_hull(unique_points)
            hull_coords = [list(p) for p in hull] + [list(hull[0])]
            
            feature = {
                "type": "Feature",
                "properties": {
                    "ubs_referencia": ubs,
                    "num_microareas": len([k for k in all_points.keys() if k[0] == ubs]),
                    "num_ruas_total": len(points)
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [hull_coords]
                }
            }
            ubs_features.append(feature)
            print(f"✓ UBS {ubs}: {len(unique_points)} pontos únicos → polígono agregado gerado")
    
    ubs_geojson = {
        "type": "FeatureCollection",
        "name": "ubs_areas",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": ubs_features
    }
    
    ubs_output_path = dados_dir / "ubs_areas.geojson"
    with open(ubs_output_path, "w", encoding="utf-8") as f:
        json.dump(ubs_geojson, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ GeoJSON agregado por UBS salvo em: {ubs_output_path}")
    print(f"   Total de polígonos UBS: {len(ubs_features)}")


if __name__ == "__main__":
    main()
