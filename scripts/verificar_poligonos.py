"""
Verificação dos Polígonos GeoJSON
Analisa se os polígonos gerados fazem sentido geográfico
"""

import json
from pathlib import Path
import math

def calcular_area_km2(coords):
    """
    Calcula a área aproximada de um polígono em km² usando a fórmula de Shoelace.
    Considera conversão aproximada de graus para km na latitude de NSS (~10.85°S).
    """
    # Fator de conversão: 1 grau de latitude ≈ 111 km, longitude varia com latitude
    lat_media = -10.85
    km_por_grau_lat = 111.0
    km_por_grau_lon = 111.0 * math.cos(math.radians(lat_media))
    
    # Converter coordenadas para km
    coords_km = []
    for lon, lat in coords:
        x = lon * km_por_grau_lon
        y = lat * km_por_grau_lat
        coords_km.append((x, y))
    
    # Fórmula de Shoelace para área
    n = len(coords_km)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coords_km[i][0] * coords_km[j][1]
        area -= coords_km[j][0] * coords_km[i][1]
    return abs(area) / 2.0

def calcular_centroide(coords):
    """Calcula o centróide de um polígono"""
    n = len(coords)
    sum_lon = sum(c[0] for c in coords)
    sum_lat = sum(c[1] for c in coords)
    return (sum_lon / n, sum_lat / n)

def calcular_extensao(coords):
    """Calcula a extensão (bounding box) do polígono"""
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    return {
        "lon_min": min(lons),
        "lon_max": max(lons),
        "lat_min": min(lats),
        "lat_max": max(lats)
    }

def distancia_km(p1, p2):
    """Calcula distância aproximada em km entre dois pontos"""
    lat_media = -10.85
    km_por_grau_lat = 111.0
    km_por_grau_lon = 111.0 * math.cos(math.radians(lat_media))
    
    dlat = (p2[1] - p1[1]) * km_por_grau_lat
    dlon = (p2[0] - p1[0]) * km_por_grau_lon
    return math.sqrt(dlat**2 + dlon**2)

def main():
    base_dir = Path(__file__).parent.parent
    dados_dir = base_dir / "dados"
    
    # Carregar GeoJSON de microáreas
    with open(dados_dir / "microareas_ubs.geojson", "r", encoding="utf-8") as f:
        microareas = json.load(f)
    
    # Carregar GeoJSON de UBS
    with open(dados_dir / "ubs_areas.geojson", "r", encoding="utf-8") as f:
        ubs_areas = json.load(f)
    
    print("=" * 70)
    print("VERIFICAÇÃO DOS POLÍGONOS GERADOS")
    print("=" * 70)
    
    # Bounding box esperada de Nossa Senhora do Socorro
    BBOX_NSS = {
        "lat_min": -11.05, "lat_max": -10.75,
        "lon_min": -37.25, "lon_max": -37.00
    }
    
    print(f"\n📍 Bounding Box esperada de N. Sra. do Socorro:")
    print(f"   Latitude:  {BBOX_NSS['lat_min']:.2f} a {BBOX_NSS['lat_max']:.2f}")
    print(f"   Longitude: {BBOX_NSS['lon_min']:.2f} a {BBOX_NSS['lon_max']:.2f}")
    
    print("\n" + "-" * 70)
    print("ANÁLISE DAS MICROÁREAS")
    print("-" * 70)
    
    problemas = []
    
    for feature in microareas["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"][0]
        
        ubs = props["ubs_referencia"]
        micro = props["micro_area"]
        
        # Calcular métricas
        area_km2 = calcular_area_km2(coords)
        centroide = calcular_centroide(coords)
        extensao = calcular_extensao(coords)
        
        # Largura e altura em km
        lat_media = -10.85
        km_por_grau_lon = 111.0 * math.cos(math.radians(lat_media))
        largura_km = (extensao["lon_max"] - extensao["lon_min"]) * km_por_grau_lon
        altura_km = (extensao["lat_max"] - extensao["lat_min"]) * 111.0
        
        print(f"\n🔷 {ubs} - Microárea {micro}")
        print(f"   Área: {area_km2:.2f} km²")
        print(f"   Dimensões: {largura_km:.2f} km x {altura_km:.2f} km")
        print(f"   Centróide: ({centroide[0]:.5f}, {centroide[1]:.5f})")
        print(f"   Vértices: {len(coords)}")
        
        # Verificações
        alertas = []
        
        # 1. Verificar se está dentro da bounding box de NSS
        if (extensao["lat_min"] < BBOX_NSS["lat_min"] or 
            extensao["lat_max"] > BBOX_NSS["lat_max"] or
            extensao["lon_min"] < BBOX_NSS["lon_min"] or 
            extensao["lon_max"] > BBOX_NSS["lon_max"]):
            alertas.append("⚠️  FORA da bounding box de N. Sra. do Socorro!")
            problemas.append(f"{ubs} - Microárea {micro}: fora da bbox")
        
        # 2. Verificar área razoável (microárea típica: 0.1 a 10 km²)
        if area_km2 < 0.01:
            alertas.append("⚠️  Área muito pequena (< 0.01 km²)")
            problemas.append(f"{ubs} - Microárea {micro}: área muito pequena")
        elif area_km2 > 50:
            alertas.append("⚠️  Área muito grande (> 50 km²)")
            problemas.append(f"{ubs} - Microárea {micro}: área muito grande")
        
        # 3. Verificar extensão razoável (não deve ultrapassar 15 km)
        if largura_km > 15 or altura_km > 15:
            alertas.append(f"⚠️  Extensão muito grande: {max(largura_km, altura_km):.1f} km")
            problemas.append(f"{ubs} - Microárea {micro}: extensão exagerada")
        
        if alertas:
            for a in alertas:
                print(f"   {a}")
        else:
            print(f"   ✅ Polígono dentro dos parâmetros esperados")
    
    print("\n" + "-" * 70)
    print("ANÁLISE DAS ÁREAS AGREGADAS POR UBS")
    print("-" * 70)
    
    centroides_ubs = {}
    
    for feature in ubs_areas["features"]:
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"][0]
        
        ubs = props["ubs_referencia"]
        
        area_km2 = calcular_area_km2(coords)
        centroide = calcular_centroide(coords)
        centroides_ubs[ubs] = centroide
        
        extensao = calcular_extensao(coords)
        lat_media = -10.85
        km_por_grau_lon = 111.0 * math.cos(math.radians(lat_media))
        largura_km = (extensao["lon_max"] - extensao["lon_min"]) * km_por_grau_lon
        altura_km = (extensao["lat_max"] - extensao["lat_min"]) * 111.0
        
        print(f"\n🏥 {ubs}")
        print(f"   Área total: {area_km2:.2f} km²")
        print(f"   Dimensões: {largura_km:.2f} km x {altura_km:.2f} km")
        print(f"   Centróide: ({centroide[0]:.5f}, {centroide[1]:.5f})")
        print(f"   Microáreas: {props['num_microareas']}")
    
    # Distância entre as duas UBS
    if len(centroides_ubs) == 2:
        ubs_list = list(centroides_ubs.keys())
        dist = distancia_km(centroides_ubs[ubs_list[0]], centroides_ubs[ubs_list[1]])
        print(f"\n📏 Distância entre centróides das UBS: {dist:.2f} km")
        
        if dist < 0.5:
            print("   ⚠️  UBS muito próximas - podem estar sobrepostas!")
            problemas.append("UBS estão muito próximas")
        elif dist > 20:
            print("   ⚠️  UBS muito distantes - verificar se estão no mesmo município")
            problemas.append("UBS estão muito distantes")
        else:
            print("   ✅ Distância parece razoável para UBS em bairros diferentes")
    
    print("\n" + "=" * 70)
    print("RESUMO DA VERIFICAÇÃO")
    print("=" * 70)
    
    if problemas:
        print("\n❌ PROBLEMAS ENCONTRADOS:")
        for p in problemas:
            print(f"   • {p}")
        print("\n⚠️  Recomenda-se revisar manualmente os dados geocodificados")
    else:
        print("\n✅ TODOS OS POLÍGONOS PASSARAM NA VERIFICAÇÃO!")
        print("   Os polígonos parecem razoáveis para microáreas de saúde.")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
