"""
Geocodificação usando Google Maps Geocoding API
Camada 1 de verificação de coordenadas

Usa:
- region=br para viés regional
- components=country:BR para restringir ao Brasil
- bounds para limitar à região de Nossa Senhora do Socorro
"""

import requests
import pandas as pd
import time
from pathlib import Path

# Configuração
API_KEY = "AIzaSyDTOJJmPDfQp9bL7tFGwVEM4AsID5UJm1M"
BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# Bounding box de Nossa Senhora do Socorro (SW e NE corners)
BOUNDS_SW = "-11.05,-37.25"  # Sudoeste
BOUNDS_NE = "-10.75,-37.00"  # Nordeste
BOUNDS = f"{BOUNDS_SW}|{BOUNDS_NE}"

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DADOS_DIR = BASE_DIR / "dados"


def geocode_address(address: str, verbose: bool = False) -> dict:
    """
    Geocodifica um endereço usando a API do Google Maps.
    
    Retorna:
        dict com 'lat', 'lon', 'formatted_address', 'location_type', 'status'
    """
    params = {
        "address": address,
        "key": API_KEY,
        "region": "br",  # Viés para Brasil
        "language": "pt-BR",
        "components": "country:BR|administrative_area:SE",  # Restringe a Sergipe, Brasil
        "bounds": BOUNDS  # Limita à região de Nossa Senhora do Socorro
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if verbose:
            print(f"  Status: {data.get('status')}")
        
        if data["status"] == "OK" and len(data["results"]) > 0:
            result = data["results"][0]
            location = result["geometry"]["location"]
            location_type = result["geometry"].get("location_type", "UNKNOWN")
            
            # Verificar se está dentro do bounding box esperado
            lat = location["lat"]
            lon = location["lng"]
            
            in_bounds = (-11.05 <= lat <= -10.75) and (-37.25 <= lon <= -37.00)
            
            return {
                "lat": lat,
                "lon": lon,
                "formatted_address": result.get("formatted_address", ""),
                "location_type": location_type,
                "in_bounds": in_bounds,
                "status": "OK"
            }
        elif data["status"] == "ZERO_RESULTS":
            return {"status": "ZERO_RESULTS"}
        else:
            return {"status": data.get("status", "ERROR")}
            
    except Exception as e:
        return {"status": f"ERROR: {str(e)}"}


def main():
    # Carregar CSV consolidado atual
    csv_path = DADOS_DIR / "UBS_Ruas_Coordenadas_Consolidado.csv"
    df = pd.read_csv(csv_path)
    
    print(f"Total de endereços: {len(df)}")
    
    # Filtrar apenas os que estão marcados como 'manual'
    df_manual = df[df['metodo'] == 'manual'].copy()
    print(f"Endereços para verificar via Google Maps API: {len(df_manual)}")
    
    # Processar cada endereço
    resultados = []
    
    for idx, row in df_manual.iterrows():
        endereco = row['endereco_completo']
        print(f"\n[{len(resultados)+1}/{len(df_manual)}] {endereco}")
        
        result = geocode_address(endereco, verbose=True)
        
        if result["status"] == "OK":
            if result["in_bounds"]:
                print(f"  ✅ ENCONTRADO: ({result['lat']}, {result['lon']})")
                print(f"     Tipo: {result['location_type']}")
                print(f"     Endereço formatado: {result['formatted_address']}")
                resultados.append({
                    "endereco_original": endereco,
                    "latitude": result["lat"],
                    "longitude": result["lon"],
                    "location_type": result["location_type"],
                    "formatted_address": result["formatted_address"],
                    "metodo": "google_api"
                })
            else:
                print(f"  ⚠️  FORA DO BOUNDING BOX: ({result['lat']}, {result['lon']})")
                print(f"     Endereço formatado: {result['formatted_address']}")
                resultados.append({
                    "endereco_original": endereco,
                    "latitude": result["lat"],
                    "longitude": result["lon"],
                    "location_type": result["location_type"],
                    "formatted_address": result["formatted_address"],
                    "metodo": "google_api_fora_bounds"
                })
        else:
            print(f"  ❌ {result['status']}")
            resultados.append({
                "endereco_original": endereco,
                "latitude": None,
                "longitude": None,
                "location_type": None,
                "formatted_address": None,
                "metodo": "manual"
            })
        
        # Rate limiting - 50 requests/second é o limite, mas vamos ser conservadores
        time.sleep(0.1)
    
    # Salvar resultados
    df_resultados = pd.DataFrame(resultados)
    output_path = DADOS_DIR / "UBS_Ruas_GoogleAPI_Resultados.csv"
    df_resultados.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ Resultados salvos em: {output_path}")
    
    # Resumo
    encontrados = len([r for r in resultados if r["metodo"] == "google_api"])
    fora_bounds = len([r for r in resultados if r["metodo"] == "google_api_fora_bounds"])
    nao_encontrados = len([r for r in resultados if r["metodo"] == "manual"])
    
    print(f"\n=== RESUMO ===")
    print(f"  Encontrados (dentro do bounding box): {encontrados}")
    print(f"  Encontrados (fora do bounding box): {fora_bounds}")
    print(f"  Não encontrados: {nao_encontrados}")


if __name__ == "__main__":
    main()
