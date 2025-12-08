"""
Pipeline Completo de Geocodificação
Versão 2.0 - Usando Google Maps API como fonte primária

Camadas de verificação:
1. Google Maps Geocoding API (primária)
2. Busca IA via web search (fallback)
3. Verificação manual (último recurso)
"""

import requests
import pandas as pd
import time
from pathlib import Path

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

API_KEY = "AIzaSyDTOJJmPDfQp9bL7tFGwVEM4AsID5UJm1M"
BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# Bounding box de Nossa Senhora do Socorro
BOUNDS_SW = "-11.05,-37.25"
BOUNDS_NE = "-10.75,-37.00"
BOUNDS = f"{BOUNDS_SW}|{BOUNDS_NE}"

# Coordenadas de fallback (bairros)
COORD_GUAJARA = (-10.89845, -37.15609)
COORD_SAO_BRAZ = (-10.84992, -37.05153)

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DADOS_DIR = BASE_DIR / "dados"

# ============================================================================
# FUNÇÕES DE GEOCODIFICAÇÃO
# ============================================================================

def geocode_google(address: str) -> dict:
    """
    Geocodifica usando a API do Google Maps.
    Retorna dict com lat, lon, status, location_type, formatted_address
    """
    params = {
        "address": address,
        "key": API_KEY,
        "region": "br",
        "language": "pt-BR",
        "components": "country:BR|administrative_area:SE",
        "bounds": BOUNDS
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if data["status"] == "OK" and len(data["results"]) > 0:
            result = data["results"][0]
            location = result["geometry"]["location"]
            location_type = result["geometry"].get("location_type", "UNKNOWN")
            
            lat = location["lat"]
            lon = location["lng"]
            
            # Verificar se está dentro do bounding box
            in_bounds = (-11.05 <= lat <= -10.75) and (-37.25 <= lon <= -37.00)
            
            if in_bounds:
                return {
                    "lat": lat,
                    "lon": lon,
                    "location_type": location_type,
                    "formatted_address": result.get("formatted_address", ""),
                    "status": "OK"
                }
            else:
                return {"status": "FORA_BOUNDS", "formatted_address": result.get("formatted_address", "")}
        else:
            return {"status": data.get("status", "ERROR")}
            
    except Exception as e:
        return {"status": f"ERROR: {str(e)}"}


def get_fallback_coord(endereco: str) -> dict:
    """
    Retorna coordenada de fallback baseada no bairro.
    """
    endereco_lower = endereco.lower()
    
    if "guajará" in endereco_lower or "guajara" in endereco_lower:
        return {
            "lat": COORD_GUAJARA[0],
            "lon": COORD_GUAJARA[1],
            "nota": "fallback_bairro_guajara"
        }
    elif "sao braz" in endereco_lower or "são braz" in endereco_lower or "são brás" in endereco_lower:
        return {
            "lat": COORD_SAO_BRAZ[0],
            "lon": COORD_SAO_BRAZ[1],
            "nota": "fallback_bairro_sao_braz"
        }
    else:
        return None


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 70)
    print("PIPELINE DE GEOCODIFICAÇÃO - v2.0")
    print("Google Maps API → Fallback Bairro → Manual")
    print("=" * 70)
    
    # 1. Carregar arquivo original
    csv_original = DADOS_DIR / "UBS_Ruas - Unificada.csv"
    df_original = pd.read_csv(csv_original)
    print(f"\nTotal de endereços: {len(df_original)}")
    
    # 2. Processar cada endereço
    resultados = []
    
    stats = {
        "google_api": 0,
        "fallback_bairro": 0,
        "manual": 0
    }
    
    for idx, row in df_original.iterrows():
        endereco = row['endereco_completo']
        ubs = row['ubs_referencia']
        micro_area = row['micro_area']
        
        print(f"\n[{idx+1}/{len(df_original)}] {endereco[:60]}...")
        
        resultado = {
            'ubs_referencia': ubs,
            'localizacao_ubs': row['localizacao_ubs'],
            'link_map_ubs': row['link_map_ubs'],
            'micro_area': micro_area,
            'endereco_completo': endereco,
            'latitude': None,
            'longitude': None,
            'metodo': 'manual',
            'nota': 'nao_encontrado'
        }
        
        # Camada 1: Google Maps API
        google_result = geocode_google(endereco)
        
        if google_result["status"] == "OK":
            resultado['latitude'] = google_result['lat']
            resultado['longitude'] = google_result['lon']
            resultado['metodo'] = 'google_api'
            resultado['nota'] = f"encontrado_{google_result['location_type']}"
            stats["google_api"] += 1
            print(f"  ✅ Google API: ({google_result['lat']:.6f}, {google_result['lon']:.6f})")
            
        elif google_result["status"] == "FORA_BOUNDS":
            # Google encontrou mas fora do bounding box - usar fallback
            print(f"  ⚠️  Google: FORA DO BOUNDING BOX ({google_result.get('formatted_address', '')})")
            
            fallback = get_fallback_coord(endereco)
            if fallback:
                resultado['latitude'] = fallback['lat']
                resultado['longitude'] = fallback['lon']
                resultado['metodo'] = 'manual'
                resultado['nota'] = fallback['nota']
                stats["fallback_bairro"] += 1
                print(f"  📍 Fallback: ({fallback['lat']:.6f}, {fallback['lon']:.6f})")
            else:
                stats["manual"] += 1
                print(f"  ❌ Sem fallback disponível")
                
        else:
            # Google não encontrou - usar fallback
            print(f"  ⚠️  Google: {google_result['status']}")
            
            fallback = get_fallback_coord(endereco)
            if fallback:
                resultado['latitude'] = fallback['lat']
                resultado['longitude'] = fallback['lon']
                resultado['metodo'] = 'manual'
                resultado['nota'] = fallback['nota']
                stats["fallback_bairro"] += 1
                print(f"  📍 Fallback: ({fallback['lat']:.6f}, {fallback['lon']:.6f})")
            else:
                stats["manual"] += 1
                print(f"  ❌ Sem fallback disponível")
        
        resultados.append(resultado)
        
        # Rate limiting
        time.sleep(0.05)
    
    # 3. Criar DataFrame e salvar
    df_consolidado = pd.DataFrame(resultados)
    
    output_path = DADOS_DIR / "UBS_Ruas_Coordenadas_Consolidado.csv"
    df_consolidado.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    print(f"\n✅ Google API:     {stats['google_api']} ({100*stats['google_api']/len(df_original):.1f}%)")
    print(f"⚠️  Fallback/Manual: {stats['fallback_bairro'] + stats['manual']} ({100*(stats['fallback_bairro']+stats['manual'])/len(df_original):.1f}%)")
    print(f"\n📁 CSV salvo em: {output_path}")
    
    # 4. Mostrar endereços que precisam de revisão manual
    manuais = df_consolidado[df_consolidado['metodo'] == 'manual']
    if len(manuais) > 0:
        print(f"\n⚠️  {len(manuais)} endereços para REVISÃO MANUAL:")
        for _, row in manuais.iterrows():
            print(f"   - [{row['ubs_referencia']}, MA{row['micro_area']}] {row['endereco_completo']}")
    
    return df_consolidado


if __name__ == "__main__":
    main()
