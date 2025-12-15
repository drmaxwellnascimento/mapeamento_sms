"""
Integra os resultados da API do Google Maps ao CSV consolidado
"""

import pandas as pd
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DADOS_DIR = BASE_DIR / "dados"


def main():
    # 1. Carregar CSV consolidado atual
    csv_consolidado = DADOS_DIR / "UBS_Ruas_Coordenadas_Consolidado.csv"
    df = pd.read_csv(csv_consolidado)
    print(f"CSV consolidado: {len(df)} endereços")
    
    # 2. Carregar resultados do Google API
    csv_google = DADOS_DIR / "UBS_Ruas_GoogleAPI_Resultados.csv"
    df_google = pd.read_csv(csv_google)
    print(f"Resultados Google API: {len(df_google)} endereços")
    
    # 3. Criar dicionário de coordenadas do Google
    google_coords = {}
    for _, row in df_google.iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            google_coords[row['endereco_original']] = {
                'latitude': row['latitude'],
                'longitude': row['longitude'],
                'location_type': row['location_type'],
                'formatted_address': row['formatted_address']
            }
    
    print(f"Coordenadas Google válidas: {len(google_coords)}")
    
    # 4. Atualizar CSV consolidado
    atualizados = 0
    for idx, row in df.iterrows():
        endereco = row['endereco_completo']
        
        # Solo atualizar se estava como 'manual' e temos coordenada do Google
        if row['metodo'] == 'manual' and endereco in google_coords:
            google_data = google_coords[endereco]
            
            # Verificar se a coordenada parece razoável (dentro do bounding box)
            lat = google_data['latitude']
            lon = google_data['longitude']
            
            if (-11.05 <= lat <= -10.75) and (-37.25 <= lon <= -37.00):
                df.at[idx, 'latitude'] = lat
                df.at[idx, 'longitude'] = lon
                df.at[idx, 'metodo'] = 'google_api'
                df.at[idx, 'nota'] = f"encontrado_{google_data['location_type']}"
                atualizados += 1
            else:
                # Fora do bounding box - manter como manual
                df.at[idx, 'nota'] = f"google_fora_bbox"
    
    print(f"\nEndereços atualizados com Google API: {atualizados}")
    
    # 5. Salvar CSV atualizado
    df.to_csv(csv_consolidado, index=False, encoding='utf-8-sig')
    print(f"✅ CSV consolidado atualizado: {csv_consolidado}")
    
    # 6. Resumo
    print("\n=== RESUMO FINAL ===")
    for metodo, count in df['metodo'].value_counts().items():
        print(f"  {metodo}: {count}")


if __name__ == "__main__":
    main()
