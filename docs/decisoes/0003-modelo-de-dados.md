# ADR 0003 — Formato e origem dos dados dos grafos

- **Status:** aceita (09/11/2026)

## Contexto

Os três grafos (paradas de ônibus de Lorena, aeroportos da LATAM, bairros e vias da cidade) precisam
sair do Google Maps e de pesquisa na web. O peso de cada aresta é o que o algoritmo otimiza, então a
**qualidade do dado é a qualidade da resposta**.

## Ponto de partida (v1)

JSON, um arquivo por grafo, com metadados (`criterio_peso`, `unidade`, `tipo_dado`, `aviso`,
`referencias`). Pesos: Dijkstra 25 de 27 `demonstrativo`; LATAM por Haversine; bairros sem fonte.
Não há validação na carga (aresta com id inexistente vira `KeyError`; peso negativo passa).

## Alternativas de formato

- **JSON** (um arquivo por grafo: vértices com nome/coordenadas, arestas com peso e fonte).
- **CSV** (dois arquivos por grafo: `vertices.csv`, `arestas.csv`) — fácil de editar em planilha e de
  carregar como tabela, como numa camada bronze.

## Alternativas de origem do peso

- **Medido no Google Maps** (distância de rota real) — fiel, mas manual e difícil de auditar.
- **Calculado por Haversine** a partir de latitude/longitude — reprodutível, mas é linha reta.
- **Misto**: Haversine para voos (avião voa quase em linha reta), Google Maps para ruas e ônibus.

## Perguntas antes de decidir

- P1. Para um voo, a distância em linha reta é uma boa aproximação? E para uma rua? Por quê?
- P2. Como alguém (o professor) confere de onde veio cada peso? Que coluna isso exige?
- P3. O Dijkstra exige pesos não negativos. Onde essa regra deve ser verificada: no carregamento dos
  dados ou dentro do algoritmo? (Pense em "validação na ingestão" de um pipeline.)
- P4. Grafo não direcionado: a aresta A–B é guardada uma vez ou duas? Quem garante que não haja
  duplicata?

## Decisão

JSON (um arquivo por grafo) com `fonte` por aresta; validação na carga (`validar_grafo`, camada de
ingestão) e de novo no Dijkstra para peso negativo. Pesos: voos por Haversine (avião voa quase em
linha reta); ônibus e vias pela rota de carro do Google Maps (rua não é linha reta), vale a menor
rota encontrada. Aresta não direcionada guardada uma vez; duplicata é recusada na carga.

