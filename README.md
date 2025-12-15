# 🗺️ Mapeamento SMS

Sistema de geocodificação e mapeamento de Unidades Básicas de Saúde (UBS) e suas microáreas de cobertura para a Secretaria Municipal de Saúde de Nossa Senhora do Socorro - SE.

---

## 📋 Índice

1. [Sobre o Projeto](#sobre-o-projeto)
2. [Tutorial Completo: Do Zero ao Mapa](#tutorial-completo-do-zero-ao-mapa)
   - [Passo 1: Clonar o Repositório](#passo-1-clonar-o-repositório)
   - [Passo 2: Configurar o Ambiente Python](#passo-2-configurar-o-ambiente-python)
   - [Passo 3: Configurar a API Key do Google](#passo-3-configurar-a-api-key-do-google)
   - [Passo 4: Preparar seus Dados CSV](#passo-4-preparar-seus-dados-csv)
   - [Passo 5: Gerar os Arquivos KML](#passo-5-gerar-os-arquivos-kml)
   - [Passo 6: Visualizar os Dados](#passo-6-visualizar-os-dados)
3. [Estrutura do Projeto](#estrutura-do-projeto)
4. [Scripts Disponíveis](#scripts-disponíveis)
5. [Solução de Problemas](#solução-de-problemas)

---

## 🎯 Sobre o Projeto

Este projeto automatiza o processo de:

- **Geocodificação de endereços** → Converte endereços de ruas em coordenadas geográficas (latitude/longitude)
- **Geração de arquivos KML** → Cria arquivos compatíveis com Google Earth, Google Maps e QGIS
- **Organização por microáreas** → Agrupa os pontos por UBS e microárea, com cores distintas
- **Mapeamento visual** → Permite visualizar as áreas de cobertura de cada UBS

---

## 🚀 Tutorial Completo: Do Zero ao Mapa

Este tutorial irá guiá-lo desde a instalação até a visualização dos mapas gerados. Siga cada passo cuidadosamente.

### Passo 1: Clonar o Repositório

Primeiro, você precisa baixar o código do projeto para o seu computador.

#### 1.1. Abra o Terminal

- **Windows**: Pressione `Win + R`, digite `cmd` e pressione Enter
- **Mac**: Pressione `Cmd + Espaço`, digite `Terminal` e pressione Enter
- **Linux**: Pressione `Ctrl + Alt + T`

#### 1.2. Navegue até a pasta onde quer salvar o projeto

```bash
# Exemplo: ir para a pasta Documentos
cd ~/Documentos
```

#### 1.3. Clone o repositório

```bash
git clone https://github.com/SEU_USUARIO/mapeamento_sms.git
```

> 💡 **Dica**: Substitua `SEU_USUARIO` pelo nome do usuário correto do repositório.

#### 1.4. Entre na pasta do projeto

```bash
cd mapeamento_sms
```

---

### Passo 2: Configurar o Ambiente Python

O projeto usa Python 3 e algumas bibliotecas. Vamos configurar um ambiente virtual para isolar as dependências.

#### 2.1. Verifique se o Python está instalado

```bash
python3 --version
```

Você deve ver algo como `Python 3.10.x` ou superior. Se não tiver Python instalado:

- **Windows**: Baixe em [python.org](https://www.python.org/downloads/)
- **Mac**: `brew install python3`
- **Linux**: `sudo apt install python3 python3-venv`

#### 2.2. Crie um ambiente virtual

```bash
python3 -m venv venv
```

Este comando cria uma pasta `venv` com um ambiente Python isolado.

#### 2.3. Ative o ambiente virtual

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

> ✅ Você saberá que está ativado quando ver `(venv)` no início da linha do terminal.

#### 2.4. Instale as dependências

```bash
pip install requests pandas python-dotenv
```

Este comando instala:
- `requests` → Para fazer requisições à API do Google
- `pandas` → Para manipular os arquivos CSV
- `python-dotenv` → Para carregar configurações do arquivo `.env`

---

### Passo 3: Configurar a API Key do Google

O script usa a API de Geocodificação do Google Maps para converter endereços em coordenadas. Você precisa de uma API Key.

#### 3.1. Obter uma API Key do Google (se ainda não tiver)

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Vá em **APIs e Serviços** → **Biblioteca**
4. Busque por "Geocoding API" e **ative-a**
5. Vá em **APIs e Serviços** → **Credenciais**
6. Clique em **Criar Credenciais** → **Chave de API**
7. Copie a chave gerada

> ⚠️ **Importante**: A API do Google tem custo após o limite gratuito (US$ 200/mês de crédito grátis). Monitore seu uso no Console.

#### 3.2. Criar o arquivo de configuração

Crie um arquivo chamado `.env` na raiz do projeto:

```bash
echo "GOOGLE_MAPS_API_KEY=SUA_CHAVE_AQUI" > .env
```

> 🔐 **Segurança**: O arquivo `.env` está no `.gitignore`, então sua chave não será enviada ao GitHub.

#### 3.3. Verificar se a configuração está correta

Para testar se a API Key está funcionando:

```bash
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
key = os.getenv('GOOGLE_MAPS_API_KEY')
if key:
    print('✅ API Key configurada:', key[:10] + '...')
else:
    print('❌ API Key não encontrada!')
"
```

---

### Passo 4: Preparar seus Dados CSV

O script espera arquivos CSV com um formato específico.

#### 4.1. Estrutura esperada do CSV

Seu arquivo CSV deve ter as seguintes colunas (os nomes podem variar um pouco):

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| `ubs_referencia` | Nome da UBS | "Alcides Alves dos Santos" |
| `localizacao_ubs` | Endereço da UBS | "R. Esmeraldo - Taboca" |
| `link_map_ubs` | Link do Google Maps da UBS | "https://maps.google.com/..." |
| `micro_area` | Número da microárea | 1, 2, 3, "01 e 02" |
| `endereco_completo` | Endereço da rua | "Rua Boa Nova, Taboca, Nossa Senhora do Socorro - SE" |

> 💡 **O script aceita variações nos nomes das colunas**, como:
> - `Microarea`, `micro_area`, `Micro Area` → todos funcionam
> - `Endereco_Completo`, `endereco_completo` → todos funcionam

#### 4.2. Onde colocar os arquivos CSV

Coloque seus arquivos CSV na pasta `dados/`:

```
mapeamento_sms/
└── dados/
    ├── UBS_Ruas - Alcides_Alves.csv
    ├── UBS_Ruas - Outra_UBS.csv
    └── ...
```

#### 4.3. Exemplo de CSV válido

```csv
ubs_referencia,localizacao_ubs,link_map_ubs,micro_area,endereco_completo
Alcides Alves,Rua X - Taboca,https://maps.google.com/...,1,"Rua Boa Nova, Taboca, Nossa Senhora do Socorro - SE"
Alcides Alves,Rua X - Taboca,https://maps.google.com/...,1,"Rua da Paz, Taboca, Nossa Senhora do Socorro - SE"
Alcides Alves,Rua X - Taboca,https://maps.google.com/...,2,"Av. Principal, Taboca, Nossa Senhora do Socorro - SE"
```

---

### Passo 5: Gerar os Arquivos KML

Agora vamos ao passo principal: converter os CSVs em arquivos KML!

#### 5.1. Gerar KML para um único arquivo

```bash
# Certifique-se de estar com o ambiente ativado
source venv/bin/activate

# Gere o KML para um CSV específico
python scripts/gerar_kml.py "dados/UBS_Ruas - Alcides_Alves.csv"
```

Você verá uma saída como:

```
======================================================================
Processando: UBS_Ruas - Alcides_Alves.csv
======================================================================
Total de endereços: 38
  [1/38] Av. Boa Nova, Taboca... ✅ Google
  [2/38] Rua da Paz, Taboca... ✅ Google
  ...

======================================================================
RESUMO
======================================================================
✅ Google API:      38
📍 Fallback:        0
❌ Não encontrado:  0

📁 KML salvo em: dados/saídas/UBS_Ruas - Alcides_Alves.kml
```

#### 5.2. Gerar KML para TODOS os arquivos CSV

Para processar todos os CSVs de uma vez:

```bash
source venv/bin/activate

for csv in dados/UBS_Ruas\ -\ *.csv dados/UBS_Ruas\ -\ *.tsv; do
  [ -f "$csv" ] && python scripts/gerar_kml.py "$csv"
done
```

#### 5.3. Verificar os arquivos gerados

Os KMLs são salvos na pasta `dados/saídas/`:

```bash
ls -la dados/saídas/
```

---

### Passo 6: Visualizar os Dados

Agora você tem arquivos KML! Veja como visualizá-los:

#### Opção A: Google Earth (Recomendado)

1. Acesse [Google Earth Web](https://earth.google.com/web/)
2. Clique no menu (☰) → **Projetos** → **Novo projeto**
3. Clique em **Importar arquivo KML**
4. Selecione um arquivo da pasta `dados/saídas/`
5. Os pontos aparecerão no mapa com as cores da UBS!

#### Opção B: Google My Maps

1. Acesse [Google My Maps](https://www.google.com/maps/d/)
2. Clique em **Criar um novo mapa**
3. Clique em **Importar** e selecione seu arquivo KML
4. Os pontos serão importados com suas propriedades

#### Opção C: QGIS (Para análise avançada)

1. Abra o QGIS
2. Vá em **Camada** → **Adicionar Camada** → **Adicionar Camada Vetorial**
3. Selecione o arquivo KML
4. Clique em **Adicionar**

#### 📍 Entendendo as cores

Cada UBS tem uma **cor base única**, e cada microárea dentro da UBS tem uma **variação de tom** dessa cor. Isso facilita identificar:
- Quais ruas pertencem à mesma UBS (cores similares)
- Quais ruas pertencem à mesma microárea (mesma cor exata)

---

## 📁 Estrutura do Projeto

```
mapeamento_sms/
├── dados/                         # Dados de entrada e saída
│   ├── UBS_Ruas - *.csv           # Arquivos CSV de entrada (um por UBS)
│   ├── saídas/                    # Arquivos KML gerados
│   │   └── UBS_Ruas - *.kml       # Um KML por CSV processado
│   └── *.geojson                  # Arquivos GeoJSON auxiliares
│
├── scripts/                       # Scripts Python
│   ├── gerar_kml.py               # 🌟 Script principal - gera KML a partir de CSV
│   ├── geocodificar_completo.py   # Geocodificação com Google API + fallbacks
│   ├── geocodificar_google.py     # Geocodificação apenas com Google API
│   ├── gerar_poligonos.py         # Gera polígonos das microáreas
│   └── ...                        # Outros scripts auxiliares
│
├── venv/                          # Ambiente virtual Python (não versionado)
├── .env                           # Configurações secretas (não versionado)
├── .gitignore                     # Arquivos ignorados pelo Git
└── README.md                      # Este arquivo
```

---

## 🔧 Scripts Disponíveis

| Script | Descrição |
|--------|-----------|
| `gerar_kml.py` | **Principal** - Converte CSV em KML com geocodificação |
| `geocodificar_completo.py` | Geocodifica usando Google API com fallbacks |
| `geocodificar_google.py` | Geocodifica usando apenas Google API |
| `gerar_poligonos.py` | Gera polígonos (convex hull) das microáreas |
| `gerar_csv_consolidado.py` | Consolida dados de várias fontes |

---

## 🔍 Solução de Problemas

### ❌ "API Key não encontrada"

**Sintoma**: O script mostra erro sobre API Key.

**Solução**:
1. Verifique se o arquivo `.env` existe na raiz do projeto
2. Verifique se o conteúdo está correto: `GOOGLE_MAPS_API_KEY=sua_chave_aqui`
3. Não use aspas ao redor da chave

### ❌ "Coluna X não encontrada no CSV"

**Sintoma**: O script não encontra as colunas necessárias.

**Solução**:
1. Verifique se seu CSV tem as colunas obrigatórias
2. O script aceita variações de nome (veja Passo 4.1)
3. Verifique se não há linhas em branco no início do arquivo

### ❌ "REQUEST_DENIED" ou "API Key expired"

**Sintoma**: A API do Google retorna erro.

**Solução**:
1. Verifique se a API Key está correta
2. Verifique se a "Geocoding API" está ativada no Google Cloud Console
3. Verifique se você não excedeu o limite de uso

### ❌ Todos os endereços usando "Fallback"

**Sintoma**: Nenhum endereço é encontrado pelo Google.

**Solução**:
1. Verifique se sua API Key está funcionando (teste no Passo 3.3)
2. Verifique se os endereços estão bem formatados
3. Adicione ", Nossa Senhora do Socorro - SE" ao final dos endereços

### ❌ KML não abre no Google Earth

**Sintoma**: Arquivo KML corrompido ou vazio.

**Solução**:
1. Verifique se o CSV tinha dados válidos
2. Verifique a saída do script por erros
3. Abra o KML em um editor de texto para verificar o conteúdo

---

## 👥 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto foi desenvolvido para a Secretaria Municipal de Saúde de Nossa Senhora do Socorro - SE.

---

## 🤖 Desenvolvido com

Assistência de **Antigravity AI** (Google DeepMind)

---

*Última atualização: Dezembro 2025*
