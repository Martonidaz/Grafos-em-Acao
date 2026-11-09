# CONTEXTO — memória entre sessões

## Sessão 1 (09/11/2026) — criação do repositório

- Repositório criado, público, inspirado no BoscoGraph (sem reaproveitar código).
- Material de referência recebido: o .zip de uma colega com a explicação e a apresentação do trabalho
  dela (Flask + vis-network; Dijkstra com 15 paradas, Prim com 14 aeroportos usando Haversine, Kruskal
  com 12 bairros de Lorena). **Não versionado aqui**: é trabalho dela; serve só para comparar ideias.
- O BoscoGraph já implementa Dijkstra, Prim e Kruskal com passo a passo (Tkinter). Aqui eles serão
  reescritos do zero, em versão enxuta, focada nos três problemas do enunciado.

## O que já foi provado / estudado (aulas)

- DFS (tempos d/f, cores), BFS (distância em arestas), Dijkstra (tabela do conjunto S), Prim (corte,
  conjunto S), Kruskal (floresta, ordenação de arestas, detecção de ciclo).

## Defeitos já diagnosticados no código do Daniel

| Defeito | Nome técnico | Onde apareceu |
|---|---|---|
| — | — | — |

## Decisões em aberto

- ADR 0002: interface (Tkinter, web com Flask ou CLI + imagem).
- ADR 0003: formato e origem dos dados (JSON/CSV; pesos medidos no Google Maps ou calculados).

## Próximos passos

1. Responder as perguntas dos ADRs 0002 e 0003.
2. Modelar o primeiro grafo (sugestão: Kruskal, o menor e sem origem/destino).
3. Escrever os esqueletos e os testes vermelhos do primeiro algoritmo.
