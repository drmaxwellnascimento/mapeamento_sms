"""
Geocodificação Híbrida: Nominatim + Perplexity
===============================================
Processa o CSV de ruas das UBS e adiciona coordenadas geográficas.

Estratégia:
1. Tenta Nominatim (gratuito, OSM)
2. Se falhar, usa Perplexity para buscar no Google Maps
3. Valida se coordenadas estão dentro de Nossa Senhora do Socorro
4. Adiciona coluna de confiança (alta/média/baixa)
"""

import pandas as pd
import time
import re
import sys
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Tentar importar requests para Perplexity
try:
    import requests
except ImportError:
    print("Instalando requests...")
    os.system("pip install requests")
    import requests

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

# Bounding box de Nossa Senhora do Socorro, SE (aproximado)
BBOX_NSS = {
    "lat_min": -11.05,
    "lat_max": -10.75,
    "lon_min": -37.25,
    "lon_max": -37.00
}

# API Key do Perplexity (será solicitada se não fornecida)
PERPLEXITY_API_KEY = None

# =============================================================================
# FUNÇÕES DE GEOCODIFICAÇÃO
# =============================================================================

def validar_coordenadas(lat, lon):
    """Verifica se as coordenadas estão dentro do município."""
    if lat is None or lon is None:
        return False
    return (BBOX_NSS["lat_min"] <= lat <= BBOX_NSS["lat_max"] and
            BBOX_NSS["lon_min"] <= lon <= BBOX_NSS["lon_max"])

def geocodificar_nominatim(endereco, geolocator, tentativas=3):
    """Tenta geocodificar usando Nominatim/OSM."""
    for tentativa in range(tentativas):
        try:
            time.sleep(1.1)  # Respeitar rate limit
            location = geolocator.geocode(endereco, timeout=10)
            if location:
                lat, lon = location.latitude, location.longitude
                if validar_coordenadas(lat, lon):
                    return {
                        "latitude": lat,
                        "longitude": lon,
                        "fonte": "nominatim",
                        "confianca": "alta",
                        "endereco_encontrado": location.address
                    }
                else:
                    # Coordenadas fora do bounding box
                    return None
            return None
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            if tentativa < tentativas - 1:
                time.sleep(2 ** tentativa)  # Backoff exponencial
            continue
    return None

def geocodificar_perplexity(endereco_rua, nome_ubs, endereco_ubs, api_key, tentativas=3):
    """Usa Perplexity para buscar coordenadas no Google Maps."""
    
    prompt = f"""Encontre as coordenadas geograficas (latitude e longitude) da seguinte rua no Google Maps:

RUA: "{endereco_rua}"

CONTEXTO:
- Esta rua pertence a area de cobertura da UBS {nome_ubs}
- A UBS fica em: {endereco_ubs}
- Cidade: Nossa Senhora do Socorro, Sergipe, Brasil
- Coordenadas aproximadas da regiao: -10.85 a -10.95 latitude, -37.05 a -37.20 longitude

INSTRUCOES IMPORTANTES:
1. Busque esta rua no Google Maps considerando o contexto acima
2. Se encontrar, retorne APENAS as coordenadas no formato exato abaixo
3. Se NAO encontrar a rua exata, retorne NOT_FOUND

FORMATO DA RESPOSTA (use exatamente este formato):
[[[LATITUDE, LONGITUDE]]]

Exemplos de resposta valida:
[[[-10.8935, -37.1567]]]
[[[-10.9012, -37.1234]]]

Se nao encontrar:
[[[NOT_FOUND]]]"""

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "sonar",  # Modelo gratuito
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }
    
    for tentativa in range(tentativas):
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 429:  # Rate limit
                wait_time = 2 ** (tentativa + 2)  # 4, 8, 16 segundos
                print(f"      [Rate limit] Aguardando {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            if response.status_code != 200:
                print(f"      [Erro API] Status: {response.status_code}")
                return None
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Parsing das coordenadas
            match = re.search(r'\[\[\[(-?\d+\.?\d*),\s*(-?\d+\.?\d*)\]\]\]', content)
            if match:
                lat = float(match.group(1))
                lon = float(match.group(2))
                
                if validar_coordenadas(lat, lon):
                    return {
                        "latitude": lat,
                        "longitude": lon,
                        "fonte": "perplexity",
                        "confianca": "media",
                        "endereco_encontrado": endereco_rua
                    }
                else:
                    print(f"      [!] Coordenadas fora do bounding box: {lat}, {lon}")
                    return None
            
            if "NOT_FOUND" in content:
                return None
            
            print(f"      [!] Resposta nao parseavel: {content[:50]}...")
            return None
            
        except Exception as e:
            if tentativa < tentativas - 1:
                time.sleep(2 ** tentativa)
            else:
                print(f"      [Erro] {str(e)[:50]}")
            continue
    
    return None

def normalizar_endereco(endereco):
    """Normaliza o endereço para melhorar chances de match."""
    # Remover " - SE" do final se existir
    endereco = re.sub(r'\s*-\s*SE$', ', Sergipe, Brasil', endereco)
    # Expandir abreviações
    endereco = endereco.replace("Av.", "Avenida")
    endereco = endereco.replace("Tv.", "Travessa")
    endereco = endereco.replace("R.", "Rua")
    return endereco

# =============================================================================
# PROCESSAMENTO PRINCIPAL
# =============================================================================

def processar_csv(arquivo_entrada, arquivo_saida, api_key_perplexity=None):
    """Processa o CSV e adiciona coordenadas."""
    
    print("=" * 70)
    print("GEOCODIFICACAO HIBRIDA - UBS Ruas")
    print("=" * 70)
    
    # Carregar CSV
    df = pd.read_csv(arquivo_entrada)
    total = len(df)
    print(f"\nTotal de enderecos: {total}")
    
    # Inicializar geolocator
    geolocator = Nominatim(user_agent="geocodificador_ubs_nss_v1")
    
    # Novas colunas
    df["latitude"] = None
    df["longitude"] = None
    df["fonte_geocod"] = None
    df["confianca"] = None
    df["endereco_encontrado"] = None
    
    # Contadores
    sucesso_nominatim = 0
    sucesso_perplexity = 0
    falhas = 0
    
    print("\nProcessando enderecos...")
    print("-" * 70)
    
    for idx, row in df.iterrows():
        endereco = row["endereco_completo"]
        nome_ubs = row["ubs_referencia"]
        endereco_ubs = row["localizacao_ubs"]
        micro_area = row["micro_area"]
        
        print(f"\n[{idx+1}/{total}] {endereco[:50]}...")
        
        # Tentar Nominatim primeiro
        endereco_normalizado = normalizar_endereco(endereco)
        resultado = geocodificar_nominatim(endereco_normalizado, geolocator)
        
        if resultado:
            print(f"   [OK] Nominatim: {resultado['latitude']:.6f}, {resultado['longitude']:.6f}")
            sucesso_nominatim += 1
        elif api_key_perplexity:
            # Fallback para Perplexity
            print(f"   [--] Nominatim falhou, tentando Perplexity...")
            resultado = geocodificar_perplexity(endereco, nome_ubs, endereco_ubs, api_key_perplexity)
            
            if resultado:
                print(f"   [OK] Perplexity: {resultado['latitude']:.6f}, {resultado['longitude']:.6f}")
                sucesso_perplexity += 1
            else:
                print(f"   [X] Nao encontrado")
                falhas += 1
        else:
            print(f"   [X] Nominatim falhou (sem Perplexity)")
            falhas += 1
        
        # Atualizar DataFrame
        if resultado:
            df.at[idx, "latitude"] = resultado["latitude"]
            df.at[idx, "longitude"] = resultado["longitude"]
            df.at[idx, "fonte_geocod"] = resultado["fonte"]
            df.at[idx, "confianca"] = resultado["confianca"]
            df.at[idx, "endereco_encontrado"] = resultado.get("endereco_encontrado", "")
    
    # Salvar CSV
    df.to_csv(arquivo_saida, index=False, encoding="utf-8-sig")
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO")
    print("=" * 70)
    print(f"Total processado:      {total}")
    print(f"Sucesso (Nominatim):   {sucesso_nominatim} ({100*sucesso_nominatim/total:.1f}%)")
    print(f"Sucesso (Perplexity):  {sucesso_perplexity} ({100*sucesso_perplexity/total:.1f}%)")
    print(f"Total encontrados:     {sucesso_nominatim + sucesso_perplexity} ({100*(sucesso_nominatim+sucesso_perplexity)/total:.1f}%)")
    print(f"Nao encontrados:       {falhas} ({100*falhas/total:.1f}%)")
    print(f"\nArquivo salvo: {arquivo_saida}")
    print("=" * 70)
    
    return df

# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":
    # Arquivos
    ARQUIVO_ENTRADA = r"c:\Users\drmax\mapeamento_sms\dados\UBS_Ruas - Unificada.csv"
    ARQUIVO_SAIDA = r"c:\Users\drmax\mapeamento_sms\dados\UBS_Ruas_Geocodificadas.csv"
    
    # API Key do Perplexity (pode ser passada como argumento)
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        # Tentar ler de variável de ambiente
        api_key = os.environ.get("PERPLEXITY_API_KEY")
    
    if not api_key:
        print("\n[!] API Key do Perplexity nao fornecida.")
        print("    Executando apenas com Nominatim (taxa de sucesso ~50%)")
        print("    Para usar Perplexity: python geocodificar_ubs.py SUA_API_KEY")
        print("")
    
    # Processar
    processar_csv(ARQUIVO_ENTRADA, ARQUIVO_SAIDA, api_key)
