# CONTEXTO — memória entre sessões

## Sessão 1 (09/11/2026) — repositório e v1

- Repositório criado (público). Trabalho **em grupo**: Daniel + colega.
- A v1 da colega foi importada sem alterações (commit "Importa a v1 do grupo") e integrada ao
  andaime no commit seguinte. Estratégia: **corrigir a v1, não reescrever**.
- Estado medido após a integração: `pytest` → 8/8 passando (Dijkstra igual à NetworkX nos 210
  pares; Prim igual partindo dos 14 aeroportos; Kruskal; desconexos; Prim = Kruskal).
  `ruff check .` → 40 avisos (16 E501, 6 PLR2004, 6 F401 em `algoritmos/__init__.py`, que são
  re-exports intencionais e se resolvem com `__all__`, além de complexidade em `app.py`/algoritmos).
- O BoscoGraph segue como inspiração e oráculo, sem código copiado.

## O que já foi estudado (aulas)

DFS (tempos d/f, cores), BFS (distância em arestas), Dijkstra (tabela do conjunto S), Prim (corte,
conjunto S), Kruskal (floresta, ordenação de arestas, detecção de ciclo).

## Defeitos abertos na v1 (corrigir um por vez, nesta ordem)

| # | Defeito | Nome técnico | Onde | Por que importa |
|---|---|---|---|---|
| 1 | Pesos sem fonte: 25/27 do Dijkstra "demonstrativo", LATAM e bairros sem `fonte` | falta de linhagem de dados (*data lineage*) | `dados/*.json` | o enunciado manda usar o Google Maps; é a pergunta mais provável na defesa |
| 2 | Nenhuma validação ao carregar o JSON: aresta para id inexistente vira `KeyError`; peso ≤ 0 e aresta duplicada passam | ausência de validação de esquema na ingestão | `algoritmos/grafo.py` (`carregar_grafo`) | o Dijkstra só é correto com pesos não negativos |
| 3 | Rede de ônibus não direcionada e sem linhas/baldeações | simplificação de modelagem | `dados/lorena_transporte.json` | "melhor rota de transporte público" com 3 baldeações talvez não seja a melhor |
| 4 | `fila.pop(0)` numa lista | lista usada como fila, O(n) por remoção | `grafo.py` (`componentes_conexas`) | a stdlib tem `collections.deque` |
| 5 | Comentário diz "compressão de caminho", mas `pai[v] = pai[pai[v]]` é outra técnica | nomenclatura incorreta (*path halving*) | `kruskal.py` (`UnionFind.encontrar`) | pergunta de defesa: saber o nome certo |
| 6 | `app.run(debug=True)` | depurador do Werkzeug exposto (execução remota de código) | `app.py` | hábito inseguro, mesmo em 127.0.0.1 |
| 7 | `remover_arestas` aceita string: `"A\|B" in "CEN\|ALD"` vira busca de substring | confusão de tipos na fronteira de confiança | `grafo.py` + `app.py` | entrada da API não é validada |

Defeitos já corrigidos: (nenhum ainda)

## Decisões em aberto

- ADR 0002: decidida de fato (Flask + vis-network); falta a justificativa, que será cobrada na defesa.
- ADR 0003: origem dos pesos e onde validar (ligado aos defeitos 1 e 2).

## Próximos passos

1. Defeito 2 (validação na carga), porque protege todos os outros: escrever primeiro o teste que falha.
2. Defeito 1 (pesos reais com `fonte`), começando pelo Kruskal (12 bairros, 20 vias).
3. Pedir o nome da colega para registrar a coautoria (`Co-authored-by`) nos próximos commits.
