# ADR 0001 — Relação com o BoscoGraph

- **Status:** aceita (09/11/2026)

## Contexto

O BoscoGraph (repo público do Daniel, ~24 mil linhas, Tkinter) já resolve Dijkstra, Prim e Kruskal
passo a passo, com grafos em JSON. O Trabalho Final pede três softwares "claros e objetivos", cada um
para um problema real.

## Alternativas

1. **Repo novo, só inspirado** — reescreve os três algoritmos do zero; leva as ideias, não o código.
2. **Repo novo reutilizando o núcleo** — copia `algoritmos.py`/`classes/` e foca na modelagem.
3. **Sem repo novo** — os três grafos viram modelos JSON dentro do BoscoGraph.

## Decisão

Alternativa 1.

## Consequências

- (+) Reescrever é o exercício: cada linha precisa ser defendida na apresentação.
- (+) Código pequeno e focado, mais fácil de explicar que 24 mil linhas genéricas.
- (−) Mais trabalho. Mitigação: o BoscoGraph serve de **oráculo** — se os dois discordarem num grafo,
  um deles tem defeito.

Ideias herdadas: algoritmo anota passos e a interface só reproduz; grafo em arquivo de dados.
