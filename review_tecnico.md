# Review Técnico: Projeto Mapeamento SMS

## 1. Visão Geral
O projeto **Mapeamento SMS** tem como objetivo geocodificar endereços de Unidades Básicas de Saúde (UBS) e suas microáreas, focando no município de Nossa Senhora do Socorro (SE). A solução utiliza uma abordagem híbrida interessante, combinando dados abertos (OpenStreetMap/Nominatim) com inteligência artificial (Perplexity) e testes com Google Maps.

**Stack Tecnológico:**
*   **Linguagem:** Python
*   **Bibliotecas:** pandas, geopy, requests
*   **Serviços:** Nominatim (OSM), Perplexity API, Google Geocoding API (teste)

## 2. Análise do Código

### Pontos Fortes
*   **Estratégia Híbrida:** A ideia de usar o Nominatim como primeira opção (gratuita) e o Perplexity como fallback é criativa e potencializa a taxa de sucesso.
*   **Validação Geográfica:** A função `validar_coordenadas` usando um Bounding Box (BBOX) é excelente. Ela impede que endereços homônimos em outras cidades/estados poluam os dados.
*   **Respeito às APIs:** Os scripts incluem `time.sleep` e backoff exponencial, o que é fundamental para respeitar os limites de requisição do Nominatim e evitar bloqueios.
*   **Documentação:** O `README.md` é claro e explica bem o propósito e como rodar o básico.

### Pontos de Atenção (Melhorias)

#### A. Caminhos Hardcoded (Crítico)
Os scripts utilizam caminhos absolutos fixos, ex:
`r"c:\Users\drmax\mapeamento_sms\dados\..."`
Isso quebra a portabilidade. Se você mover a pasta do projeto ou se outro desenvolvedor tentar rodar, o código falhará.
**Recomendação:** Use caminhos relativos ou a biblioteca `pathlib`.

#### B. Gerenciamento de Dependências
O projeto não possui um arquivo `requirements.txt`. O script `geocodificar_ubs.py` tenta instalar dependências dinamicamente com `os.system("pip install requests")`, o que não é uma boa prática.
**Recomendação:** Criar um arquivo `requirements.txt` listando `pandas`, `geopy`, `requests`, etc.

#### C. Variáveis de Ambiente e Segredos
As chaves de API (Perplexity, Google) são passadas via argumento ou tentadas via ambiente, o que é bom. Mas para facilitar o desenvolvimento local, o uso de um arquivo `.env` seria ideal.

#### D. Duplicidade de Código
O script `geocodificar_nominatim.py` parece ser uma versão anterior ou simplificada de `geocodificar_ubs.py`. Manter dois scripts com lógica de normalização e validação duplicada aumenta o esforço de manutenção.

## 3. Recomendações de Ação

### Imediato
1.  **Refatorar Caminhos:** Substituir strings de caminho absoluto por caminhos relativos.
2.  **Criar `requirements.txt`:** Listar todas as bibliotecas necessárias.
3.  **Remover instalação automática:** Retirar o `os.system("pip install...")` do código.

### Médio Prazo
1.  **Unificar Scripts:** Transformar `geocodificar_ubs.py` no único script principal, talvez aceitando argumentos (`--nominatim-only`, `--use-perplexity`) para controlar o comportamento.
2.  **Logging:** Substituir `print` por `logging` para ter registros mais controlados (info, warning, error) e salvar logs em arquivo para auditoria.

## 4. Conclusão
O projeto está funcional e resolve bem o problema proposto com uma abordagem inteligente. As melhorias sugeridas são focadas em **boas práticas de engenharia de software** para tornar o código mais robusto, portátil e fácil de manter.
