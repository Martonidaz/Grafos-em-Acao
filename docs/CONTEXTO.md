# CONTEXTO — memória entre sessões

## Sessão 1 (09/11/2026) — repositório e v1

- Repositório criado (público). Trabalho **em grupo**: Daniel + colega.
- A v1 da colega foi importada sem alterações (commit "Importa a v1 do grupo") e integrada ao
  andaime no commit seguinte. Estratégia: **corrigir a v1, não reescrever**.
- Estado medido após a integração: `pytest` → 8/8 passando (Dijkstra igual à NetworkX nos 210
  pares; Prim igual partindo dos 14 aeroportos; Kruskal; desconexos; Prim = Kruskal).
  `ruff check .` → 40 avisos na v1, zerados no commit "Deixa o ruff limpo" (ruff format, `__all__`,
  strings quebradas; PLR09xx e PLR2004 desligados por serem ruído em código didático).
- O BoscoGraph segue como inspiração e oráculo, sem código copiado.

## O que já foi estudado (aulas)

DFS (tempos d/f, cores), BFS (distância em arestas), Dijkstra (tabela do conjunto S), Prim (corte,
conjunto S), Kruskal (floresta, ordenação de arestas, detecção de ciclo).

## Defeitos da v1

| # | Defeito | Nome técnico | Onde | Por que importa |
|---|---|---|---|---|
| 1 | Pesos sem fonte: 25/27 do Dijkstra "demonstrativo", LATAM e bairros sem `fonte` | falta de linhagem de dados (*data lineage*) | `dados/*.json` | o enunciado manda usar o Google Maps; é a pergunta mais provável na defesa |
| 2 | Nenhuma validação ao carregar o JSON: aresta para id inexistente vira `KeyError`; peso ≤ 0 e aresta duplicada passam | ausência de validação de esquema na ingestão | `algoritmos/grafo.py` (`carregar_grafo`) | o Dijkstra só é correto com pesos não negativos |
| 3 | Rede de ônibus não direcionada e sem linhas/baldeações | simplificação de modelagem | `dados/lorena_transporte.json` | "melhor rota de transporte público" com 3 baldeações talvez não seja a melhor |
| 4 | `fila.pop(0)` numa lista | lista usada como fila, O(n) por remoção | `grafo.py` (`componentes_conexas`) | a stdlib tem `collections.deque` |
| 5 | Comentário diz "compressão de caminho", mas `pai[v] = pai[pai[v]]` é outra técnica | nomenclatura incorreta (*path halving*) | `kruskal.py` (`UnionFind.encontrar`) | pergunta de defesa: saber o nome certo |
| 6 | `app.run(debug=True)` | depurador do Werkzeug exposto (execução remota de código) | `app.py` | hábito inseguro, mesmo em 127.0.0.1 |
| 7 | `remover_arestas` aceita string: `"A\|B" in "CEN\|ALD"` vira busca de substring | confusão de tipos na fronteira de confiança | `grafo.py` + `app.py` | entrada da API não é validada |

Corrigidos em 09/11/2026 (modo desenvolvimento): **2** (`validar_grafo` na carga + `validar_pesos`
no Dijkstra), **4** (`deque`), **5** (comentário: *path halving*), **6** (`app.run()` sem debug) e **7**
(`remover_arestas` exige lista; `@app.errorhandler(ValueError)` → 400 no lugar de 3 `try/except`).
Testes: `tests/test_validacao.py`.

**1 resolvido (09/11):** 47 distâncias reais (Routes API + conferência no site; vale a menor rota).
**3 resolvido no que as fontes permitem (09/11):** 7 das 27 ligações levam `linhas` reais da ABC
Transportes (Diário do Transporte, 16/03/2022: linha 8 Aldo Nassif–USP II–Shopping; linha 6
Shopping–Centro–USP I–Campinho; linhas 3/5 Novo Horizonte–Cruz–Parque das Rodovias). O resultado do
Dijkstra mostra a linha de cada trecho e conta as trocas de linha. Limites assumidos: rede não
direcionada (as linhas fazem ida e volta) e a troca de linha não entra no peso (o Dijkstra minimiza
distância). Itinerário completo das linhas não está publicado nas fontes consultadas.

Kruskal ampliado (09/11, 22h): 35 dos 50 bairros dos Correios, 65 vias medidas pela Routes API
(`dados/bairros_api.py`); resultado 38.026 m, 34 aceitas, economia de 61%.

Prim com dados reais (09/11, 22h30): ANAC VRA set/2026, 64 aeroportos, 155 rotas LATAM, peso = duração
real em minutos (`dados/vra_latam.py`); árvore mínima 6.064 min.

Grupo: Breno Ryan de Andrade Fernandes, Daniel Marton Barbosa, João Vitor Ferreira Azevedo Pereira,
Mariana Gonçalves de Freitas Ribeiro. Professor: Prof. Me. Warner Brezolin. Entrega: 09/11/2026, 23h.

## Decisões em aberto

- ADR 0002: decidida de fato (Flask + vis-network); falta a justificativa, que será cobrada na defesa.
- ADR 0003: origem dos pesos e onde validar (ligado aos defeitos 1 e 2).

## Pedido registrado (09/11/2026)

Depois de terminar as correções (defeitos 1 e 3), o Daniel vai listar pontos de design para mudar.
Cada ponto deve vir em **duas variantes de visual/comportamento** para ele escolher qual fica.
Pendente: a lista dos pontos.

## Próximos passos

1. Defeito 1 (pesos reais com `fonte`): planilhas `dados/medicoes_*.csv` geradas (27 + 20 arestas,
   link do Maps em cada uma). Falta o grupo medir e rodar `python -m dados.medicoes aplicar`.
   Google Maps só via links (Maps URLs, sem chave): o Daniel já pagou R$ 350 com API do Maps;
   Alternativa a pedido do Daniel (09/11): `dados/rotas_api.py` (Routes API Essentials, 47
   chamadas, dentro da cota grátis) com travas no script e roteiro de travas no Cloud no README.
   Nunca usar outra API do Maps (Distance Matrix, Places, Geocoding) neste projeto.
2. Defeito 3 (modelagem do ônibus: direção e baldeação).
3. Integrantes do grupo convidados como colaboradores no GitHub (09/11).
