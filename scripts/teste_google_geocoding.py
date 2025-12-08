"""
Teste de Geocodificação usando Google Geocoding API
====================================================
Para usar este script, você precisa de uma API Key do Google Cloud.

Como obter:
1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto ou selecione um existente
3. Ative a "Geocoding API" em APIs & Services > Library
4. Crie uma API Key em APIs & Services > Credentials
5. Substitua 'SUA_API_KEY_AQUI' pela sua chave

Uso: python teste_google_geocoding.py SUA_API_KEY
"""

import sys
import time
import requests

def geocode_google(endereco, api_key):
    """Geocodifica um endereço usando a Google Geocoding API."""
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": endereco,
        "key": api_key,
        "language": "pt-BR",
        "region": "br"
    }
    
    response = requests.get(base_url, params=params)
    data = response.json()
    
    if data["status"] == "OK":
        result = data["results"][0]
        location = result["geometry"]["location"]
        return {
            "encontrado": True,
            "endereco_formatado": result["formatted_address"],
            "latitude": location["lat"],
            "longitude": location["lng"],
            "tipo": result["geometry"]["location_type"]
        }
    else:
        return {
            "encontrado": False,
            "status": data["status"]
        }

def main():
    if len(sys.argv) < 2:
        print("Uso: python teste_google_geocoding.py SUA_API_KEY")
        print("\nPara obter uma API Key:")
        print("1. Acesse: https://console.cloud.google.com/")
        print("2. Ative a 'Geocoding API'")
        print("3. Crie uma API Key em Credentials")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    # Mesmos endereços do teste anterior
    enderecos_teste = [
        "Avenida Principal, Guajara, Nossa Senhora do Socorro, SE, Brasil",
        "Rua A, Guajara, Nossa Senhora do Socorro, SE, Brasil",
        "Rua Aramuru, Sao Braz, Nossa Senhora do Socorro, SE, Brasil",
        "Rua 2 de Fevereiro, Guajara, Nossa Senhora do Socorro, SE, Brasil",
        "Av. Curitiba, Sao Braz, Nossa Senhora do Socorro, SE, Brasil",
        "Rua Tapuia, Sao Braz, Nossa Senhora do Socorro, SE, Brasil",
    ]
    
    print("=" * 70)
    print("TESTE DE GEOCODIFICACAO - Google Geocoding API")
    print("=" * 70)
    
    sucesso = 0
    falha = 0
    
    for endereco in enderecos_teste:
        time.sleep(0.1)  # Pequeno delay para evitar rate limit
        
        try:
            resultado = geocode_google(endereco, api_key)
            
            if resultado["encontrado"]:
                print(f"\n[OK] ENCONTRADO: {endereco[:55]}")
                print(f"     -> {resultado['endereco_formatado'][:65]}")
                print(f"     -> Lat: {resultado['latitude']}, Lon: {resultado['longitude']}")
                print(f"     -> Precisao: {resultado['tipo']}")
                sucesso += 1
            else:
                print(f"\n[X] NAO ENCONTRADO: {endereco[:55]}")
                print(f"    Status: {resultado['status']}")
                falha += 1
                
        except Exception as e:
            print(f"\n[!] ERRO: {endereco[:55]}")
            print(f"    {str(e)}")
            falha += 1
    
    print("\n" + "=" * 70)
    print(f"RESULTADO: {sucesso}/{len(enderecos_teste)} enderecos encontrados ({100*sucesso/len(enderecos_teste):.0f}%)")
    print("=" * 70)
    
    # Comparação com Nominatim
    print("\nCOMPARACAO:")
    print(f"  - Nominatim (OSM): 50% de sucesso")
    print(f"  - Google API:      {100*sucesso/len(enderecos_teste):.0f}% de sucesso")

if __name__ == "__main__":
    main()
