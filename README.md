# Grafos em Ação

Trabalho Final (P2) de **Teoria dos Grafos e suas Aplicações**: três problemas reais modelados como
grafos e resolvidos com o algoritmo guloso adequado, cada um com código em Python e apresentação.

| # | Problema | Algoritmo | Pergunta que o software responde |
|---|----------|-----------|----------------------------------|
| 1 | Transporte público de Lorena/SP | **Dijkstra** | Qual é o melhor caminho entre a origem e o destino escolhidos? |
| 2 | Rede de voos da LATAM no Brasil | **Prim** | Quais conexões ligam todos os aeroportos com uma única via, ao menor custo total? |
| 3 | Pavimentação de uma cidade | **Kruskal** | Quais vias, de menor comprimento total, interligam todos os bairros? |

O enunciado completo está em [`docs/ENUNCIADO.md`](docs/ENUNCIADO.md).

## Relação com o BoscoGraph

Este projeto é **inspirado** no [BoscoGraph](https://github.com/Martonidaz/BoscoGraph) (ideias como
"o algoritmo anota passos, a interface só reproduz" e "o grafo mora num arquivo de dados, não no
código"), mas **não importa nem copia código dele**. Os algoritmos são reescritos aqui do zero.
Veja [`docs/decisoes/0001-relacao-com-o-boscograph.md`](docs/decisoes/0001-relacao-com-o-boscograph.md).

## Estrutura

```
Grafos-em-Acao/
├── CLAUDE.md                contrato de estudo (lido em toda sessão do Claude Code)
├── src/grafos_em_acao/      domínio: grafo, Dijkstra, Prim, Kruskal
├── dados/                   os três grafos (Lorena, LATAM, cidade a pavimentar)
├── tests/                   a especificação, executável
├── apresentacao/            o PPT de entrega
└── docs/
    ├── ENUNCIADO.md         transcrição do enunciado
    ├── CONTEXTO.md          memória entre sessões
    └── decisoes/            ADRs: alternativas escritas, decisão justificada
```

## Como rodar

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install pytest ruff networkx
ruff check .
pytest
```

## Estado

Andaime criado. Próximo passo: decidir o modelo de dados e a interface (ADRs 0002 e 0003).
