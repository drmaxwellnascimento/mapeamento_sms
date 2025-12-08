# Mapeamento SMS

Projeto de geocodificação e mapeamento de Unidades Básicas de Saúde (UBS) e suas microáreas de cobertura.

## Estrutura do Projeto

```
mapeamento_sms/
├── dados/                     # Arquivos de dados CSV
│   ├── UBS_Ruas - Unificada.csv       # Dados unificados das UBS
│   ├── UBS_Ruas_Nominatim_OK.csv      # Endereços geocodificados com sucesso
│   └── UBS_Ruas_Nominatim_FALHAS.csv  # Endereços que falharam na geocodificação
├── scripts/                   # Scripts Python
│   ├── geocodificar_nominatim.py      # Geocodificação usando Nominatim/OpenStreetMap
│   ├── geocodificar_ubs.py            # Script principal de geocodificação das UBS
│   └── teste_google_geocoding.py      # Teste com API do Google Geocoding
└── .antigravity/              # Registros de desenvolvimento com Antigravity AI
```

## Objetivo

Este projeto visa:
1. **Geocodificar endereços** - Converter endereços das UBS em coordenadas geográficas (latitude/longitude)
2. **Mapear microáreas** - Criar representações visuais das áreas de cobertura das UBS
3. **Integração com QGIS** - Preparar dados para visualização e análise em sistemas GIS

## Tecnologias Utilizadas

- **Python** - Scripts de processamento
- **Pandas** - Manipulação de dados
- **Geopy** - Geocodificação (Nominatim/OpenStreetMap)
- **QGIS** - Visualização e análise geográfica

## Como Usar

### Pré-requisitos

```bash
pip install pandas openpyxl geopy fastkml lxml
```

### Executando a Geocodificação

```bash
python scripts/geocodificar_nominatim.py
```

## Desenvolvido com

🤖 Assistência de **Antigravity AI** (Google DeepMind)

---
*Projeto de mapeamento para a Secretaria Municipal de Saúde*
