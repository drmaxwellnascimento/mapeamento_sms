# Guia de Configuração QGIS - Mapeamento UBS

Este guia explica como configurar as cores e legendas no QGIS para os arquivos GeoJSON gerados.

---

## 📁 Arquivos Disponíveis

| Arquivo | Descrição |
|---------|-----------|
| `ubs_pontos.geojson` | Pontos das UBS (marcadores) |
| `microareas_ubs_linhas.geojson` | Apenas arestas dos polígonos |
| `microareas_ubs.geojson` | Polígonos com preenchimento |
| `ubs_areas.geojson` | Polígonos agregados por UBS |

---

## 🎨 Cores das UBS

| UBS | Cor | Código Hex |
|-----|-----|------------|
| Muciano Guajara | 🔴 Vermelho | `#E63946` |
| Valter Rocha | 🔵 Azul escuro | `#1D3557` |

---

## 📍 Passo 1: Adicionar os Pontos das UBS

1. **Arrastar** `ubs_pontos.geojson` para o QGIS
2. Clique com **botão direito** na camada → **Propriedades**
3. Vá em **Simbologia**
4. Altere o tipo para **Categorizado**
5. Coluna: `ubs_referencia`
6. Clique em **Classificar**
7. Para cada UBS:
   - **Muciano Guajara**: duplo-clique → cor `#E63946` (vermelho)
   - **Valter Rocha**: duplo-clique → cor `#1D3557` (azul)
8. Opcionalmente, aumente o tamanho do marcador para 8-10 px
9. Clique **OK**

---

## 📐 Passo 2: Adicionar as Linhas (Arestas)

1. **Arrastar** `microareas_ubs_linhas.geojson` para o QGIS
2. Clique com **botão direito** na camada → **Propriedades**
3. Vá em **Simbologia**
4. Altere o tipo para **Categorizado**
5. Coluna: `ubs_referencia`
6. Clique em **Classificar**
7. Para cada UBS, configure:
   - **Muciano Guajara**: cor `#E63946`, espessura 1.5 px
   - **Valter Rocha**: cor `#1D3557`, espessura 1.5 px
8. Clique **OK**

---

## 🔤 Passo 3: Adicionar Legendas (Rótulos)

### Para os Pontos das UBS:

1. Clique com **botão direito** na camada `ubs_pontos` → **Propriedades**
2. Vá em **Rótulos**
3. Selecione **Rótulos Simples**
4. Valor: `nome`
5. Configure:
   - **Fonte**: Arial ou Roboto, tamanho 10
   - **Cor**: Branco com fundo preto (buffer)
   - **Posição**: Acima do ponto
6. Na aba **Buffer**, marque **Desenhar buffer de texto**
   - Tamanho: 1 mm
   - Cor: Preta
7. Clique **OK**

### Para as Microáreas:

1. Clique com **botão direito** na camada `microareas_ubs_linhas` → **Propriedades**
2. Vá em **Rótulos**
3. Selecione **Rótulos Simples**
4. Valor: `micro_area`
5. Configure:
   - **Fonte**: tamanho 8
   - **Posição**: No centróide do polígono
6. Clique **OK**

---

## 🗺️ Passo 4: Adicionar Mapa Base (Opcional)

1. No painel **Navegador** (à esquerda)
2. Expanda **XYZ Tiles**
3. **Arraste** `OpenStreetMap` para o mapa
4. Mova esta camada para **baixo** das outras na lista de camadas

---

## 📊 Resumo Visual Final

A ordem das camadas deve ser (de cima para baixo):
1. `ubs_pontos` (pontos das UBS com rótulos)
2. `microareas_ubs_linhas` (arestas coloridas)
3. `OpenStreetMap` (mapa base)

---

## 💾 Salvando o Projeto

1. **Arquivo** → **Salvar Projeto Como...**
2. Escolha um nome (ex: `mapeamento_ubs.qgz`)
3. Salve na pasta do projeto

Assim, da próxima vez que abrir, todas as configurações estarão preservadas.
