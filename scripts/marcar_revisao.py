"""
Marca coordenadas suspeitas para revisão manual
- Coordenadas genéricas → metodo: manual
- Coordenadas APPROXIMATE → revisão
"""

import pandas as pd
from pathlib import Path

# Diretórios
BASE_DIR = Path(__file__).parent.parent
DADOS_DIR = BASE_DIR / "dados"

# Coordenadas genéricas conhecidas (bairros/cidade)
COORDENADAS_GENERICAS = [
    # Guajará
    (-10.8989307, -37.1556814),  # Centróide Guajará
    (-10.8987421, -37.1568506),  # Avenida Principal Guajará
    (-10.898298, -37.1568661),   # Padre Cícero
    (-10.8979698, -37.156876),   # Travessa Padre Cícero  
    (-10.8983495, -37.1564517),  # São Luiz
    (-10.8989331, -37.155646),   # Rua 11
    # São Braz
    (-10.8494823, -37.0521895),  # Centróide São Braz (Caeté, Rua 09)
    (-10.850387, -37.050555),    # Espírito Santo
    (-10.8505205, -37.0513121),  # Florianópolis
    (-10.8504033, -37.0523887),  # Travessa Mato Grosso
    (-10.8502863, -37.0513742),  # Curitiba
    (-10.8500167, -37.0518566),  # Travessa Curitiba
    (-10.8505377, -37.0521436),  # Eng. Galvão
    (-10.8505602, -37.0506611),  # Mato Grosso do Sul
]

TOLERANCIA = 0.0015  # ~150m


def is_coord_generica(lat, lon):
    """Verifica se uma coordenada é genérica."""
    for gen_lat, gen_lon in COORDENADAS_GENERICAS:
        if abs(lat - gen_lat) < TOLERANCIA and abs(lon - gen_lon) < TOLERANCIA:
            return True
    return False


def main():
    # Carregar CSV
    csv_path = DADOS_DIR / "UBS_Ruas_Coordenadas_Consolidado.csv"
    df = pd.read_csv(csv_path)
    
    print("Atualizando coordenadas suspeitas...")
    
    # Contar atualizações
    genericas_atualizadas = 0
    approximate_atualizadas = 0
    
    for idx, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        nota = row['nota'] if pd.notna(row['nota']) else ""
        
        # Verificar coordenadas genéricas
        if is_coord_generica(lat, lon):
            df.at[idx, 'metodo'] = 'manual'
            df.at[idx, 'nota'] = 'coordenada_bairro_verificar'
            genericas_atualizadas += 1
        
        # Verificar APPROXIMATE
        elif 'APPROXIMATE' in str(nota):
            df.at[idx, 'metodo'] = 'revisao'
            # Manter a nota original
            approximate_atualizadas += 1
    
    # Salvar
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ Coordenadas genéricas → manual: {genericas_atualizadas}")
    print(f"✅ Coordenadas APPROXIMATE → revisao: {approximate_atualizadas}")
    print(f"\n📁 CSV atualizado: {csv_path}")
    
    # Mostrar resumo final
    print("\n=== RESUMO POR MÉTODO ===")
    for metodo, count in df['metodo'].value_counts().items():
        print(f"  {metodo}: {count}")


if __name__ == "__main__":
    main()
