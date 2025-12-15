"""
Geração de KML a partir de CSV de ruas das UBS
Usa Google Maps Geocoding API com fallback por bairro

Uso:
    python gerar_kml.py <arquivo_csv>
    
O KML será salvo em dados/saídas/ com o mesmo nome do CSV.
"""

import requests
import pandas as pd
import time
import sys
import os
import colorsys
import hashlib
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not API_KEY:
    print("❌ ERRO: GOOGLE_MAPS_API_KEY não encontrada no .env")
    sys.exit(1)

BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

# Bounding box de Nossa Senhora do Socorro
BOUNDS_SW = "-11.05,-37.25"
BOUNDS_NE = "-10.75,-37.00"
BOUNDS = f"{BOUNDS_SW}|{BOUNDS_NE}"

# Coordenadas de fallback (bairros conhecidos)
COORDS_FALLBACK = {
    "guajará": (-10.89845, -37.15609),
    "guajara": (-10.89845, -37.15609),
    "sao braz": (-10.84992, -37.05153),
    "são braz": (-10.84992, -37.05153),
    "são brás": (-10.84992, -37.05153),
    "taboca": (-10.8722, -37.1354),
    "jardim mariana": (-10.8459, -37.0522),
    "marcos freire": (-10.8765, -37.0894),
    "piabeta": (-10.8531, -37.1270),
    "parque são josé": (-10.8631, -37.1170),
    "conjunto fernando collor": (-10.8780, -37.0950),
    "conjunto albano franco": (-10.8650, -37.1050),
    "pajuçara": (-10.8590, -37.1180),
    "taiçoca": (-10.8500, -37.1100),
    "parque dos faróis": (-10.8550, -37.1050),
    "maria do carmo": (-10.8600, -37.1000),
    "fernando collor": (-10.8780, -37.0950),
    "albano franco": (-10.8650, -37.1050),
}

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DADOS_DIR = BASE_DIR / "dados"
SAIDAS_DIR = DADOS_DIR / "saídas"


# ============================================================================
# SISTEMA DE CORES POR UBS
# ============================================================================

def gerar_cor_ubs(nome_ubs: str) -> tuple:
    """
    Gera uma cor base (hue) única para cada UBS baseada em seu nome.
    Retorna (hue, saturation, lightness) onde hue é 0-360.
    """
    # Hash do nome para gerar cor consistente
    hash_val = int(hashlib.md5(nome_ubs.encode()).hexdigest()[:8], 16)
    hue = hash_val % 360  # Valor entre 0 e 360
    return hue


def gerar_cor_microarea(hue_base: float, micro_area: int, total_microareas: int = 10) -> str:
    """
    Gera uma variação de cor para cada microárea.
    Mantém o mesmo matiz (hue) mas varia a saturação e luminosidade.
    Retorna cor em formato hex (#RRGGBB)
    """
    # Variar saturação entre 0.5 e 1.0
    saturation = 0.5 + (micro_area % 5) * 0.1
    # Variar luminosidade entre 0.35 e 0.65
    lightness = 0.35 + (micro_area % 6) * 0.05
    
    # Converter HSL para RGB
    hue_normalized = hue_base / 360.0
    r, g, b = colorsys.hls_to_rgb(hue_normalized, lightness, saturation)
    
    # Converter para hex
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def hex_para_kml(hex_cor: str) -> str:
    """
    Converte cor hex (#RRGGBB) para formato KML (AABBGGRR).
    """
    hex_cor = hex_cor.lstrip('#')
    r, g, b = hex_cor[0:2], hex_cor[2:4], hex_cor[4:6]
    return f"ff{b}{g}{r}"  # KML usa AABBGGRR

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
    
    for bairro, coords in COORDS_FALLBACK.items():
        if bairro in endereco_lower:
            return {
                "lat": coords[0],
                "lon": coords[1],
                "nota": f"fallback_bairro_{bairro.replace(' ', '_')}"
            }
    
    return None


# ============================================================================
# FUNÇÕES KML
# ============================================================================

def criar_kml(nome_documento: str, nome_ubs: str, microareas: list) -> tuple:
    """
    Cria a estrutura base do KML com estilos dinâmicos baseados na UBS.
    Cada microárea terá uma variação de cor da UBS.
    """
    kml = Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    document = SubElement(kml, "Document")
    
    name = SubElement(document, "name")
    name.text = nome_documento
    
    # Gerar cor base para esta UBS
    hue_base = gerar_cor_ubs(nome_ubs)
    
    # Criar estilos para cada microárea
    estilos = {}
    for idx, micro_area in enumerate(microareas):
        # Usar string sanitizada para o ID do estilo
        ma_str = str(micro_area).replace(' ', '_').replace('/', '_')
        style_id = f"style_ma_{ma_str}"
        
        # Usar índice para variar a cor
        cor_hex = gerar_cor_microarea(hue_base, idx)
        cor_kml = hex_para_kml(cor_hex)
        
        style = SubElement(document, "Style", id=style_id)
        
        # Estilo do ícone
        icon_style = SubElement(style, "IconStyle")
        color = SubElement(icon_style, "color")
        color.text = cor_kml
        scale = SubElement(icon_style, "scale")
        scale.text = "1.2"
        icon = SubElement(icon_style, "Icon")
        href = SubElement(icon, "href")
        href.text = "http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png"
        
        # Estilo da label
        label_style = SubElement(style, "LabelStyle")
        label_color = SubElement(label_style, "color")
        label_color.text = cor_kml
        label_scale = SubElement(label_style, "scale")
        label_scale.text = "0.8"
        
        estilos[str(micro_area)] = style_id
    
    return kml, document, estilos


def adicionar_placemark(folder: Element, nome: str, descricao: str, 
                        lat: float, lon: float, style_id: str):
    """Adiciona um placemark a uma pasta do documento KML."""
    placemark = SubElement(folder, "Placemark")
    
    name = SubElement(placemark, "name")
    name.text = nome
    
    desc = SubElement(placemark, "description")
    desc.text = descricao
    
    # Usar estilo da microárea
    style_url = SubElement(placemark, "styleUrl")
    style_url.text = f"#{style_id}"
    
    point = SubElement(placemark, "Point")
    coordinates = SubElement(point, "coordinates")
    coordinates.text = f"{lon},{lat},0"


def salvar_kml(kml: Element, caminho: Path):
    """Salva o KML em arquivo."""
    tree = ElementTree(kml)
    ET.indent(tree, space="  ")
    
    with open(caminho, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)


# ============================================================================
# MAIN
# ============================================================================

def processar_csv(arquivo_csv: Path):
    """Processa um CSV e gera o KML correspondente."""
    
    print(f"\n{'='*70}")
    print(f"Processando: {arquivo_csv.name}")
    print("="*70)
    
    # Detectar separador (CSV ou TSV)
    separador = "\t" if arquivo_csv.suffix == ".tsv" else ","
    
    # Carregar CSV
    df = pd.read_csv(arquivo_csv, sep=separador)
    
    # Verificar se as colunas parecem ser "Unnamed" (linha em branco no início)
    if all('Unnamed' in str(col) or str(col).startswith('Unnamed') for col in df.columns):
        # Tentar encontrar a linha com os headers reais
        for skiprows in range(1, 5):
            try:
                df = pd.read_csv(arquivo_csv, sep=separador, skiprows=skiprows)
                if not all('Unnamed' in str(col) for col in df.columns):
                    print(f"   (pulando {skiprows} linha(s) em branco)")
                    break
            except:
                pass
    
    # Remover linhas completamente vazias
    df = df.dropna(how='all')
    
    # Normalizar nomes de colunas (case-insensitive e substituir variações)
    col_mapping = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        if col_lower in ['microarea', 'micro_area', 'microárea', 'micro area']:
            col_mapping[col] = 'micro_area'
        elif col_lower in ['endereco_completo', 'endereço_completo', 'endereco completo', 'endereço completo']:
            col_mapping[col] = 'endereco_completo'
        elif col_lower in ['ubs_referencia', 'ubs referencia', 'ubs_referência']:
            col_mapping[col] = 'ubs_referencia'
    
    df = df.rename(columns=col_mapping)
    
    print(f"Total de endereços: {len(df)}")
    
    # Verificar colunas necessárias
    colunas_necessarias = ['ubs_referencia', 'micro_area', 'endereco_completo']
    for col in colunas_necessarias:
        if col not in df.columns:
            print(f"❌ Coluna '{col}' não encontrada no CSV!")
            print(f"   Colunas disponíveis: {list(df.columns)}")
            return None
    
    # Criar KML com cores específicas da UBS
    nome_ubs = df['ubs_referencia'].iloc[0] if len(df) > 0 else "UBS"
    microareas = df['micro_area'].unique().tolist()
    kml, document, estilos = criar_kml(f"Ruas - {nome_ubs}", nome_ubs, microareas)
    
    # Criar pastas por microárea
    pastas = {}
    for micro_area in microareas:
        folder = SubElement(document, "Folder")
        folder_name = SubElement(folder, "name")
        folder_name.text = f"Microárea {micro_area}"
        pastas[str(micro_area)] = folder
    
    # Estatísticas
    stats = {"google_api": 0, "fallback": 0, "nao_encontrado": 0}
    
    # Processar cada endereço
    for idx, row in df.iterrows():
        endereco = row['endereco_completo']
        micro_area = row['micro_area']
        
        print(f"  [{idx+1}/{len(df)}] {endereco[:50]}...", end=" ")
        
        # Tentar geocodificar com Google
        google_result = geocode_google(endereco)
        
        lat, lon = None, None
        metodo = "nao_encontrado"
        
        if google_result["status"] == "OK":
            lat = google_result['lat']
            lon = google_result['lon']
            metodo = "google_api"
            stats["google_api"] += 1
            print(f"✅ Google")
        else:
            # Tentar fallback
            fallback = get_fallback_coord(endereco)
            if fallback:
                lat = fallback['lat']
                lon = fallback['lon']
                metodo = "fallback"
                stats["fallback"] += 1
                print(f"📍 Fallback")
            else:
                stats["nao_encontrado"] += 1
                print(f"❌ Não encontrado")
        
        # Adicionar ao KML se tiver coordenadas
        if lat and lon:
            # Extrair nome da rua do endereço
            nome_rua = endereco.split(",")[0] if "," in endereco else endereco
            
            descricao = f"""
UBS: {row['ubs_referencia']}
Microárea: {micro_area}
Endereço: {endereco}
Método: {metodo}
"""
            
            adicionar_placemark(
                pastas[str(micro_area)], 
                nome_rua, 
                descricao, 
                lat, lon, 
                estilos[str(micro_area)]
            )
        
        # Rate limiting
        time.sleep(0.05)
    
    # Criar diretório de saída se não existir
    SAIDAS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Salvar KML
    nome_saida = arquivo_csv.stem + ".kml"
    caminho_saida = SAIDAS_DIR / nome_saida
    salvar_kml(kml, caminho_saida)
    
    print(f"\n{'='*70}")
    print("RESUMO")
    print("="*70)
    print(f"✅ Google API:      {stats['google_api']}")
    print(f"📍 Fallback:        {stats['fallback']}")
    print(f"❌ Não encontrado:  {stats['nao_encontrado']}")
    print(f"\n📁 KML salvo em: {caminho_saida}")
    
    return caminho_saida


def main():
    if len(sys.argv) < 2:
        print("Uso: python gerar_kml.py <arquivo_csv>")
        print("Exemplo: python gerar_kml.py 'UBS_Ruas - Alcides_Alves.csv'")
        sys.exit(1)
    
    arquivo_csv = Path(sys.argv[1])
    
    # Se for caminho relativo, converter para absoluto a partir do diretório atual
    if not arquivo_csv.is_absolute():
        arquivo_csv = Path.cwd() / arquivo_csv
    
    if not arquivo_csv.exists():
        print(f"❌ Arquivo não encontrado: {arquivo_csv}")
        sys.exit(1)
    
    processar_csv(arquivo_csv)


if __name__ == "__main__":
    main()
