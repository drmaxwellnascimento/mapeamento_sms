…
import pandas as pd

try:
    # Attempt to read only the first few rows to get the header
    df = pd.read_csv('Valter_Rocha (1).csv', nrows=1, sep=';', encoding='latin1')  # Adding encoding just in case, typical for BR files
    print("Colunas encontradas:")
    for col in df.columns:
        print(f"- {col}")
except Exception as e:
    print(f"Erro ao ler o arquivo: {e}")
” *cascade08”°*cascade08°± *cascade08±ç*cascade08ç… *cascade082Hfile:///c:/Users/drmax/Documents/SECRETARIA/mapeamento/inspect_header.py