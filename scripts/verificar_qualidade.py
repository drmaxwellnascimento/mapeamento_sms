"""
Verificação de Qualidade das Coordenadas
Detecta coordenadas genéricas/suspeitas nos resultados do Google API
"""

import pandas as pd
from pathlib import Path
from collections import Counter
import math

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DADOS_DIR = BASE_DIR / "dados"

# Coordenadas conhecidas como genéricas (centroides de bairros/cidades)
COORDENADAS_GENERICAS = [
    # Centróide de Nossa Senhora do Socorro
    {"lat": -10.8531544, "lon": -37.1270097, "nome": "Centróide N.Sra.Socorro"},
    {"lat": -10.8531643, "lon": -37.1269791, "nome": "Centróide N.Sra.Socorro (var)"},
    # Centróide do bairro Guajará
    {"lat": -10.89845, "lon": -37.15609, "nome": "Centróide Guajará"},
    {"lat": -10.8989307, "lon": -37.1556814, "nome": "Centróide Guajará (var)"},
    # Centróide do bairro São Braz
    {"lat": -10.84992, "lon": -37.05153, "nome": "Centróide São Braz"},
]

TOLERANCIA = 0.001  # ~100m


def is_coord_generica(lat, lon):
    """Verifica se uma coordenada é genérica."""
    for gen in COORDENADAS_GENERICAS:
        if (abs(lat - gen["lat"]) < TOLERANCIA and 
            abs(lon - gen["lon"]) < TOLERANCIA):
            return gen["nome"]
    return None


def main():
    # Carregar CSV consolidado
    csv_path = DADOS_DIR / "UBS_Ruas_Coordenadas_Consolidado.csv"
    df = pd.read_csv(csv_path)
    
    print("=" * 70)
    print("VERIFICAÇÃO DE QUALIDADE DAS COORDENADAS")
    print("=" * 70)
    
    # 1. Verificar coordenadas genéricas
    print("\n🔍 1. VERIFICAÇÃO DE COORDENADAS GENÉRICAS")
    print("-" * 50)
    
    genericas = []
    for idx, row in df.iterrows():
        gen = is_coord_generica(row['latitude'], row['longitude'])
        if gen:
            genericas.append({
                'endereco': row['endereco_completo'],
                'ubs': row['ubs_referencia'],
                'micro_area': row['micro_area'],
                'lat': row['latitude'],
                'lon': row['longitude'],
                'tipo_generico': gen
            })
    
    if len(genericas) > 0:
        print(f"\n⚠️  {len(genericas)} coordenadas genéricas encontradas:")
        for g in genericas:
            print(f"   - [{g['ubs']}, MA{g['micro_area']}] {g['endereco'][:50]}...")
            print(f"     Coordenada: ({g['lat']}, {g['lon']}) → {g['tipo_generico']}")
    else:
        print("\n✅ Nenhuma coordenada genérica encontrada!")
    
    # 2. Verificar coordenadas duplicadas (muitas ruas no mesmo ponto)
    print("\n🔍 2. VERIFICAÇÃO DE COORDENADAS DUPLICADAS")
    print("-" * 50)
    
    coord_count = Counter()
    for _, row in df.iterrows():
        coord_key = (round(row['latitude'], 5), round(row['longitude'], 5))
        coord_count[coord_key] += 1
    
    duplicadas = [(coord, count) for coord, count in coord_count.items() if count >= 3]
    duplicadas.sort(key=lambda x: -x[1])
    
    if len(duplicadas) > 0:
        print(f"\n⚠️  {len(duplicadas)} coordenadas aparecem 3+ vezes:")
        for coord, count in duplicadas[:10]:  # Top 10
            print(f"\n   Coordenada ({coord[0]}, {coord[1]}) - {count} ocorrências:")
            ruas = df[(abs(df['latitude'] - coord[0]) < 0.00001) & 
                     (abs(df['longitude'] - coord[1]) < 0.00001)]
            for _, r in ruas.iterrows():
                print(f"     - [{r['ubs_referencia']}, MA{r['micro_area']}] {r['endereco_completo'][:40]}...")
    else:
        print("\n✅ Nenhuma coordenada com 3+ duplicatas!")
    
    # 3. Verificar endereços possivelmente fora da microárea
    print("\n🔍 3. VERIFICAÇÃO DE LOCATION_TYPE (se disponível)")
    print("-" * 50)
    
    if 'nota' in df.columns:
        location_types = df['nota'].value_counts()
        print("\nDistribuição de tipos de localização:")
        for lt, count in location_types.items():
            if 'APPROXIMATE' in str(lt):
                print(f"   ⚠️  {lt}: {count}")
            elif 'ROOFTOP' in str(lt) or 'GEOMETRIC_CENTER' in str(lt):
                print(f"   ✅ {lt}: {count}")
            else:
                print(f"   📍 {lt}: {count}")
    
    # 4. Verificar coordenadas fora do bounding box esperado
    print("\n🔍 4. VERIFICAÇÃO DE BOUNDING BOX")
    print("-" * 50)
    
    # Bounding box de Nossa Senhora do Socorro
    lat_min, lat_max = -11.05, -10.75
    lon_min, lon_max = -37.25, -37.00
    
    fora_bbox = df[
        (df['latitude'] < lat_min) | (df['latitude'] > lat_max) |
        (df['longitude'] < lon_min) | (df['longitude'] > lon_max)
    ]
    
    if len(fora_bbox) > 0:
        print(f"\n⚠️  {len(fora_bbox)} coordenadas FORA do bounding box esperado:")
        for _, row in fora_bbox.iterrows():
            print(f"   - [{row['ubs_referencia']}, MA{row['micro_area']}] {row['endereco_completo'][:40]}...")
            print(f"     Coordenada: ({row['latitude']}, {row['longitude']})")
    else:
        print("\n✅ Todas as coordenadas estão dentro do bounding box!")
    
    # 5. Resumo
    print("\n" + "=" * 70)
    print("RESUMO DA VERIFICAÇÃO")
    print("=" * 70)
    
    problemas = len(genericas) + len(duplicadas) + len(fora_bbox)
    if problemas == 0:
        print("\n✅ NENHUM PROBLEMA DETECTADO!")
    else:
        print(f"\n⚠️  {problemas} problemas potenciais detectados:")
        print(f"   - Coordenadas genéricas: {len(genericas)}")
        print(f"   - Coordenadas muito duplicadas: {len(duplicadas)}")
        print(f"   - Coordenadas fora do bounding box: {len(fora_bbox)}")


if __name__ == "__main__":
    main()
