"""
Geocodificação com Nominatim - Com prints detalhados
"""

import pandas as pd
import time
import re
import sys
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

print("Iniciando script...")
print(f"Python: {sys.version}")
sys.stdout.flush()

# Bounding box de Nossa Senhora do Socorro, SE
BBOX_NSS = {
    "lat_min": -11.05, "lat_max": -10.75,
    "lon_min": -37.25, "lon_max": -37.00
}

def validar_coordenadas(lat, lon):
    if lat is None or lon is None:
        return False
    return (BBOX_NSS["lat_min"] <= lat <= BBOX_NSS["lat_max"] and
            BBOX_NSS["lon_min"] <= lon <= BBOX_NSS["lon_max"])

def normalizar_endereco(endereco):
    endereco = re.sub(r'\s*-\s*SE$', ', Sergipe, Brasil', endereco)
    endereco = endereco.replace("Av.", "Avenida").replace("Tv.", "Travessa").replace("R.", "Rua")
    return endereco

print("Carregando CSV...")
sys.stdout.flush()

ARQUIVO_ENTRADA = r"c:\Users\drmax\mapeamento_sms\dados\UBS_Ruas - Unificada.csv"
df = pd.read_csv(ARQUIVO_ENTRADA)
total = len(df)
print(f"Total de enderecos: {total}")
sys.stdout.flush()

print("Inicializando geolocator...")
sys.stdout.flush()
geolocator = Nominatim(user_agent="geocodificador_ubs_nss_v3")

sucessos = []
falhas = []

print("\n" + "="*60)
print("PROCESSANDO ENDERECOS")
print("="*60)
sys.stdout.flush()

for idx, row in df.iterrows():
    endereco = row["endereco_completo"]
    endereco_curto = endereco[:45] + "..." if len(endereco) > 45 else endereco
    
    print(f"[{idx+1:3d}/{total}] {endereco_curto}", end=" ")
    sys.stdout.flush()
    
    try:
        time.sleep(1.1)
        endereco_norm = normalizar_endereco(endereco)
        location = geolocator.geocode(endereco_norm, timeout=10)
        
        row_dict = row.to_dict()
        
        if location and validar_coordenadas(location.latitude, location.longitude):
            row_dict["latitude"] = location.latitude
            row_dict["longitude"] = location.longitude
            row_dict["fonte"] = "nominatim"
            row_dict["confianca"] = "alta"
            sucessos.append(row_dict)
            print(f"-> OK ({location.latitude:.4f}, {location.longitude:.4f})")
        else:
            row_dict["latitude"] = None
            row_dict["longitude"] = None
            row_dict["fonte"] = None
            row_dict["confianca"] = None
            falhas.append(row_dict)
            print("-> NAO ENCONTRADO")
        sys.stdout.flush()
        
    except Exception as e:
        row_dict = row.to_dict()
        row_dict["latitude"] = None
        row_dict["longitude"] = None
        row_dict["fonte"] = None
        row_dict["confianca"] = None
        falhas.append(row_dict)
        print(f"-> ERRO: {str(e)[:30]}")
        sys.stdout.flush()

# Salvar
print("\nSalvando arquivos...")
sys.stdout.flush()

ARQUIVO_SUCESSO = r"c:\Users\drmax\mapeamento_sms\dados\UBS_Ruas_Nominatim_OK.csv"
ARQUIVO_FALHAS = r"c:\Users\drmax\mapeamento_sms\dados\UBS_Ruas_Nominatim_FALHAS.csv"

if len(sucessos) > 0:
    pd.DataFrame(sucessos).to_csv(ARQUIVO_SUCESSO, index=False, encoding="utf-8-sig")
if len(falhas) > 0:
    pd.DataFrame(falhas).to_csv(ARQUIVO_FALHAS, index=False, encoding="utf-8-sig")

print("\n" + "="*60)
print("RESUMO")
print("="*60)
print(f"Encontrados:      {len(sucessos)} ({100*len(sucessos)/total:.1f}%)")
print(f"Nao encontrados:  {len(falhas)} ({100*len(falhas)/total:.1f}%)")
print(f"\nArquivos salvos:")
print(f"  OK:     {ARQUIVO_SUCESSO}")
print(f"  FALHAS: {ARQUIVO_FALHAS}")
