ø.
import pandas as pd
import time
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from lxml import etree
import os

# --- CONFIGURA√á√ÉO ---
NOME_UBS_ALVO = "UBS VALTER DE JESUS ROCHA"  # EDITE AQUI SE NECESS√ÅRIO
ARQUIVO_KML = "ubs.kml"
ARQUIVO_CSV = "Valter_Rocha (1).csv"
ARQUIVO_SAIDA = "resultado_geocodificacao.xlsx"
CIDADE_ESTADO = "Nossa Senhora do Socorro, Sergipe, Brasil" # Ajuste conforme a cidade prov√°vel das UBS e endere√ßos

def ler_ubs_kml(caminho_kml):
    """L√™ o arquivo KML e retorna um dicion√°rio {nome: (lat, lon)}."""
    if not os.path.exists(caminho_kml):
        raise FileNotFoundError(f"Arquivo KML n√£o encontrado: {caminho_kml}")

    ubs_dict = {}
    try:
        tree = etree.parse(caminho_kml)
        root = tree.getroot()
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        placemarks = root.findall('.//kml:Placemark', ns)
        
        for pm in placemarks:
            name_elem = pm.find('kml:name', ns)
            name = name_elem.text.strip() if name_elem is not None else "Sem Nome"
            
            point = pm.find('.//kml:Point/kml:coordinates', ns)
            if point is not None and point.text:
                parts = point.text.strip().split(',')
                if len(parts) >= 2:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    ubs_dict[name] = (lat, lon)
    except Exception as e:
        print(f"Erro ao ler KML: {e}")
        return {}
        
    return ubs_dict

def main():
    print("=== INICIANDO APP MAPEADOR ===")
    
    # PASSO 2: LEITURA DO KML
    print(f"Lendo KML: {ARQUIVO_KML}...")
    todas_ubs = ler_ubs_kml(ARQUIVO_KML)
    
    if NOME_UBS_ALVO not in todas_ubs:
        print(f"ERRO CR√çTICO: UBS '{NOME_UBS_ALVO}' n√£o encontrada no arquivo KML.")
        print("UBS Dispon√≠veis:")
        for nome in todas_ubs.keys():
            print(f"- {nome}")
        return

    coords_ubs = todas_ubs[NOME_UBS_ALVO]
    print(f"UBS Alvo Identificada: {NOME_UBS_ALVO}")
    print(f"Coordenadas: {coords_ubs}") # (Lat, Lon)

    # PASSO 3: CONFIGURA√á√ÉO DO GEODECODER
    print("Configurando Geocodificador (Nominatim)...")
    geolocator = Nominatim(user_agent="saude_municipio_app_v1")
    
    # Viewbox: +/- 0.04 graus (~4-5km) ao redor da UBS
    # Formato viewbox do geopy pode ser lista de Points ou string.
    # Vamos usar points (nordeste, sudoeste) ou apenas biasing.
    # Nominatim viewbox parameter expects two points: (lat1, lon1), (lat2, lon2)
    delta = 0.04
    viewbox = [
        (coords_ubs[0] + delta, coords_ubs[1] + delta), # Nordeste
        (coords_ubs[0] - delta, coords_ubs[1] - delta)  # Sudoeste
    ]
    
    # PASSO 4: PROCESSAMENTO
    print(f"Lendo Planilha: {ARQUIVO_CSV}...")
    try:
        # Tenta ler com separador ; e encoding comum
        df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='latin1')
    except Exception as e:
        print(f"Erro ao abrir CSV: {e}")
        return

    resultados = []
    
    total_linhas = len(df)
    print(f"Iniciando geocodifica√ß√£o de {total_linhas} endere√ßos...")

    for index, row in df.iterrows():
        # Assume colunas 'Endereco_Completo' e 'Microarea' (baseado na inspe√ß√£o anterior)
        # Se 'Endereco_Completo' n√£o existir, tenta pegar a segunda coluna
        endereco_base = row.get('Endereco_Completo')
        if pd.isna(endereco_base):
            # Fallback se coluna tiver outro nome ou indice
            endereco_base = row.iloc[1] if len(row) > 1 else str(row.iloc[0])
            
        microarea = row.get('Microarea', f"Linha {index}")

        # Monta query de busca
        query = f"{endereco_base}, {CIDADE_ESTADO}"
        
        status = "PENDENTE"
        lat_enc = None
        lon_enc = None
        distancia = None
        addr_match = None
        
        try:
            # Geocoding
            # viewbox espera dois pontos (Point objects ou tuples). bounded=True for√ßa a busca na √°rea.
            location = geolocator.geocode(query, viewbox=viewbox, bounded=False, timeout=10) 
            # Bounded=False d√° prioridade mas n√£o exclui resultados fora. Bounded=True pode ser restritivo demais se endere√ßo for mal formatado.
            
            if location:
                lat_enc = location.latitude
                lon_enc = location.longitude
                addr_match = location.address
                
                # Calculo Distancia
                coords_enc = (lat_enc, lon_enc)
                distancia = geodesic(coords_ubs, coords_enc).meters
                
                if distancia < 3000:
                    status = "OK"
                else:
                    status = "ALERTA_LONGE"
            else:
                status = "NAO_ENCONTRADO"
                
        except Exception as e:
            print(f"Erro na linha {index}: {e}")
            status = "ERRO_API"
        
        # Log console
        dist_str = f"{distancia:.1f}m" if distancia is not None else "N/A"
        print(f"[{index+1}/{total_linhas}] {microarea} - {status} ({dist_str})")
        
        # Salvar resultado
        resultados.append({
            "Microarea": microarea,
            "Endereco_Original": endereco_base,
            "Endereco_Encontrado": addr_match,
            "Latitude": lat_enc,
            "Longitude": lon_enc,
            "Distancia_UBS_Metros": distancia,
            "Status": status
        })
        
        # Sleep para respeitar API
        time.sleep(1.2)

    # PASSO 5: SA√çDA
    print("Salvando resultados...")
    df_res = pd.DataFrame(resultados)
    df_res.to_excel(ARQUIVO_SAIDA, index=False)
    print(f"Conclu√≠do! Arquivo gerado: {ARQUIVO_SAIDA}")

if __name__ == "__main__":
    main()
˙ *cascade08˙˚*cascade08˚¸ *cascade08¸ˇ*cascade08ˇÄ *cascade08ÄÜ*cascade08Üá *cascade08áí*cascade08íˇ' *cascade08ˇ'À(*cascade08À(ã) *cascade08ã)è)*cascade08è)ø. *cascade082Ffile:///c:/Users/drmax/Documents/SECRETARIA/mapeamento/app_mapeador.py