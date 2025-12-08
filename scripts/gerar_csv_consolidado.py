"""
Gera CSV consolidado com todas as coordenadas e método de obtenção
"""

import pandas as pd
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DADOS_DIR = BASE_DIR / "dados"

# Coordenada genérica que indica falha na geocodificação
COORD_GENERICA = (-10.8531544, -37.1270097)
TOLERANCIA = 0.001

def is_coord_generica(lat, lon):
    """Verifica se a coordenada é o centróide genérico da cidade"""
    if pd.isna(lat) or pd.isna(lon):
        return True
    return (abs(lat - COORD_GENERICA[0]) < TOLERANCIA and 
            abs(lon - COORD_GENERICA[1]) < TOLERANCIA)

def main():
    # 1. Carregar arquivo original
    df_original = pd.read_csv(DADOS_DIR / "UBS_Ruas - Unificada.csv")
    print(f"Total de endereços no arquivo original: {len(df_original)}")
    
    # 2. Carregar resultados do Nominatim
    df_nominatim_ok = pd.read_csv(DADOS_DIR / "UBS_Ruas_Nominatim_OK.csv")
    df_nominatim_falhas = pd.read_csv(DADOS_DIR / "UBS_Ruas_Nominatim_FALHAS.csv")
    
    print(f"Nominatim OK: {len(df_nominatim_ok)}")
    print(f"Nominatim Falhas: {len(df_nominatim_falhas)}")
    
    # 3. Criar dicionário de coordenadas do Nominatim
    nominatim_coords = {}
    for _, row in df_nominatim_ok.iterrows():
        key = row['endereco_completo']
        nominatim_coords[key] = {
            'latitude': row['latitude'],
            'longitude': row['longitude'],
            'metodo': 'nominatim'
        }
    
    # 4. Coordenadas obtidas via busca IA (web search)
    # Usando coordenadas do bairro para ruas que não foram encontradas precisamente
    COORD_GUAJARA = (-10.89845, -37.15609)  # Bairro Guajará
    COORD_SAO_BRAZ = (-10.84992, -37.05153)  # Bairro São Braz
    
    busca_ia_coords = {
        # --- UBS Muciano Guajara - Microárea 32 ---
        "Rua 12 de Fevereiro, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Travessa Quissamã, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.9007348, "lon": -37.1540443, "nota": "encontrado"},
        "Rua 1 de Fevereiro, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Avenida Chesf 01, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.8952247, "lon": -37.1172331, "nota": "encontrado"},
        "Avenida Quissamã, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.9007348, "lon": -37.1540443, "nota": "encontrado"},
        "Avenida Chesf, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.8952247, "lon": -37.1172331, "nota": "encontrado"},
        "Rua do Tanque, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.893889, "lon": -37.1575, "nota": "coord_bairro"},
        "Rua da Fazenda, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.893889, "lon": -37.1575, "nota": "coord_bairro"},
        "Rua C (São Benedito), Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua D (São Benedito), Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua E (São Benedito), Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua 10 de Janeiro, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.9013800, "lon": -37.1526070, "nota": "encontrado"},
        "Rua 11 de Janeiro, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.8999782, "lon": -37.1555614, "nota": "encontrado"},
        "Rua 12 de Janeiro, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua 13 de Janeiro, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.9007348, "lon": -37.1540443, "nota": "encontrado"},
        "Rua 14 de Janeiro, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Praça 16 de Janeiro, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        
        # --- UBS Muciano Guajara - Microárea 9 ---
        "Rua Existente, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Travessa Padre Cícero, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.8983621, "lon": -37.1568275, "nota": "encontrado"},
        "Rua Otto, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua Profeta Eliseu, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua Jorge Amado, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua J. Emílio de Carvalho, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.9010741, "lon": -37.1514073, "nota": "encontrado"},
        "Rua Joze Aloisio da Silva, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua Antonio Torres, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Travessa Jucelino Emilio, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua Ezequiel Cardoso, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua Projetada, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Travessa Agepino, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua Almeida Fraga, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Travessa Santa Bárbara, Guajará, Nossa Senhora do Socorro - SE": {"lat": -10.8988931, "lon": -37.1449513, "nota": "encontrado"},
        "Rua Colonial, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua Odálio Golveia, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        "Rua Bela Vista, Guajará, Nossa Senhora do Socorro - SE": {"lat": COORD_GUAJARA[0], "lon": COORD_GUAJARA[1], "nota": "coord_bairro"},
        
        # --- UBS Valter Rocha - Microárea 1 ---
        "Rua Aramuru, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Caete, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Caxico, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Karapato, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Pataco, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Av. Tomoio, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8491378, "lon": -37.0541272, "nota": "encontrado"},
        "Rua Tapuia, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8484291, "lon": -37.0545519, "nota": "encontrado"},
        "Rua Tupinamba, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8485457, "lon": -37.0534716, "nota": "encontrado"},
        "Rua Xoco Guara, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Xingú, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8489299, "lon": -37.0523701, "nota": "encontrado"},
        "Rua Espirito Santo, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Av. Florionopolis, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8494277, "lon": -37.0710716, "nota": "encontrado"},
        "Rua Mato Grosso, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8601494, "lon": -37.0496621, "nota": "encontrado"},
        "Travessa Mato Grosso, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8601494, "lon": -37.0496621, "nota": "encontrado"},
        "Rua Santa Catarina, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Av. Curitiba, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8514372, "lon": -37.0727555, "nota": "encontrado"},
        "Travessa Curitiba, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8514372, "lon": -37.0727555, "nota": "encontrado"},
        "Av. Eng. Galvão, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        
        # --- UBS Valter Rocha - Microárea 2 ---
        "Rua Parana, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Porto Alegre, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Rio de Janeiro, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8529, "lon": -37.0515, "nota": "coord_bairro"},
        "Rua Sao Paulo, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8599071, "lon": -37.0914183, "nota": "encontrado"},
        "Av. Engenheiro Luciano Santana Gaalvão, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 05, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Travessa 19, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Travessa 17, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Goias, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8484291, "lon": -37.0545519, "nota": "encontrado"},
        "Travessa 16, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Travessa Maria Freire, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Travessa 20, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua A (Jardim Esperança), Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua B (Jardim Esperança), Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        
        # --- UBS Valter Rocha - Microárea 3 ---
        "Rua 09, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 03, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 02, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 01, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8601494, "lon": -37.0496621, "nota": "encontrado"},
        "Rua Distrito Federal, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Minas Gerais, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Mato Grosso do Sul, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8532965, "lon": -37.0550138, "nota": "encontrado"},
        
        # --- UBS Valter Rocha - Microárea 4 ---
        "Rua Kariri-Xoco, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8503197, "lon": -37.0545200, "nota": "encontrado"},
        "Rua Novo Acesso, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Av. Tupiniquins, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8500450, "lon": -37.0552734, "nota": "encontrado"},
        "Av. Tamoio, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8491378, "lon": -37.0541272, "nota": "encontrado"},
        "Rua Potiguara, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": -10.8495149, "lon": -37.0551425, "nota": "encontrado"},
        "Rua 07, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 08, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 10, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 11, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 12, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 13, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 14, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua 15, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Bras, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua Diego Emerson, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Av. Eng. Luciano Galvão, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
        "Rua D3, Sao Braz, Nossa Senhora do Socorro - SE": {"lat": COORD_SAO_BRAZ[0], "lon": COORD_SAO_BRAZ[1], "nota": "coord_bairro"},
    }
    
    # 5. Construir DataFrame consolidado
    resultados = []
    
    for _, row in df_original.iterrows():
        endereco = row['endereco_completo']
        
        resultado = {
            'ubs_referencia': row['ubs_referencia'],
            'localizacao_ubs': row['localizacao_ubs'],
            'link_map_ubs': row['link_map_ubs'],
            'micro_area': row['micro_area'],
            'endereco_completo': endereco,
            'latitude': None,
            'longitude': None,
            'metodo': 'manual',
            'nota': 'nao_encontrado'
        }
        
        # Verificar se está no Nominatim OK
        if endereco in nominatim_coords:
            coord = nominatim_coords[endereco]
            # Verificar se não é coordenada genérica
            if not is_coord_generica(coord['latitude'], coord['longitude']):
                resultado['latitude'] = coord['latitude']
                resultado['longitude'] = coord['longitude']
                resultado['metodo'] = 'nominatim'
                resultado['nota'] = 'encontrado'
            else:
                resultado['metodo'] = 'manual'
                resultado['nota'] = 'nominatim_retornou_generico'
        
        # Se não encontrou no Nominatim, verificar busca IA
        elif endereco in busca_ia_coords:
            coord = busca_ia_coords[endereco]
            # Se for coordenada de bairro, marcar como manual para verificação
            if coord['nota'] == 'coord_bairro':
                resultado['latitude'] = coord['lat']
                resultado['longitude'] = coord['lon']
                resultado['metodo'] = 'manual'
                resultado['nota'] = 'coord_bairro_verificar'
            else:
                resultado['latitude'] = coord['lat']
                resultado['longitude'] = coord['lon']
                resultado['metodo'] = 'busca_ia'
                resultado['nota'] = coord['nota']
        
        resultados.append(resultado)
    
    # 6. Criar DataFrame e salvar
    df_consolidado = pd.DataFrame(resultados)
    
    # Contar por método
    contagem = df_consolidado['metodo'].value_counts()
    print("\n=== RESUMO POR MÉTODO ===")
    for metodo, count in contagem.items():
        print(f"  {metodo}: {count}")
    
    # Contar por nota
    contagem_nota = df_consolidado['nota'].value_counts()
    print("\n=== RESUMO POR NOTA ===")
    for nota, count in contagem_nota.items():
        print(f"  {nota}: {count}")
    
    # Salvar CSV
    output_path = DADOS_DIR / "UBS_Ruas_Coordenadas_Consolidado.csv"
    df_consolidado.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n✅ CSV consolidado salvo em: {output_path}")
    
    # 7. Listar endereços que precisam de preenchimento manual
    manuais = df_consolidado[df_consolidado['metodo'] == 'manual']
    if len(manuais) > 0:
        print(f"\n⚠️  {len(manuais)} endereços precisam de coordenadas MANUAIS:")
        for _, row in manuais.iterrows():
            print(f"   - {row['endereco_completo']}")
    
    return df_consolidado


if __name__ == "__main__":
    main()
