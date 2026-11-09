# Grafos em Ação

Trabalho Final (P2) de **Teoria dos Grafos e suas Aplicações**: três problemas reais modelados como
grafos e resolvidos com o algoritmo guloso adequado, num sistema web que mostra o resultado e o passo
a passo da execução.

| # | Problema | Algoritmo | Pergunta que o software responde |
|---|----------|-----------|----------------------------------|
| 1 | Transporte público de Lorena/SP | **Dijkstra** | Qual é o melhor caminho entre a origem e o destino escolhidos? |
| 2 | Rede de voos da LATAM no Brasil | **Prim** | Quais conexões ligam todos os aeroportos com uma única via, ao menor custo total? |
| 3 | Pavimentação dos bairros de Lorena/SP | **Kruskal** | Quais vias, de menor comprimento total, interligam todos os bairros? |

O enunciado completo está em [`docs/ENUNCIADO.md`](docs/ENUNCIADO.md).

![Dijkstra](docs/capturas/dijkstra.png)

## Como rodar

Precisa do Python 3.11+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py          # abre em http://127.0.0.1:5000
pytest                 # testes (NetworkX só como gabarito)
ruff check .
```

## O que dá pra fazer

- escolher origem/destino (Dijkstra) ou aeroporto inicial (Prim) e executar
- ver o resultado destacado no grafo e o custo total
- ver o passo a passo da execução (anterior, próximo, reproduzir)
- clicar numa aresta para desativá-la e ver o que acontece (outra rota ou grafo desconexo)
- restaurar o grafo original

## Organização

```
app.py               servidor Flask e rotas da API
algoritmos/          dijkstra.py, prim.py, kruskal.py (puros) e grafo.py (leitura e apoio)
dados/               os 3 grafos em JSON + REFERENCIAS.md
templates/ static/   páginas HTML, CSS, JS e a biblioteca vis-network
tests/               testes (NetworkX só para comparar o resultado)
docs/                enunciado, apresentação, capturas, memória (CONTEXTO.md) e decisões (ADRs)
CLAUDE.md            regras de trabalho do projeto
```

## Sobre os dados

Os nomes dos pontos, bairros e aeroportos são reais (fontes em `dados/REFERENCIAS.md`), mas na v1:

- **Dijkstra**: ligações e distâncias estimadas para demonstração (só 2 têm fonte).
- **Prim**: conexões modeladas a partir dos hubs da LATAM, não a malha real; distância por Haversine.
- **Kruskal**: vias e comprimentos estimados para demonstração.

### Como medir os pesos no Google Maps (grátis)

Sem API e sem chave: só links que abrem a rota no navegador, então não há como gerar cobrança.

1. Abra `dados/medicoes_dijkstra.csv` ou `dados/medicoes_kruskal.csv` no Excel ou no Google Sheets.
2. Em cada linha, clique em `link_google_maps`, confira se os dois pontos caíram no lugar certo
   (corrija no próprio Maps se precisar) e anote a distância da rota em `peso_medido_km` ou
   `peso_medido_m`, só o número (`1,7` / `850`), mais `medido_por` e `data`.
3. Salve como CSV (separador `;`) e rode `python -m dados.medicoes aplicar`. O script grava o peso e
   a fonte em cada aresta, valida o grafo inteiro e não grava nada se algum valor estiver errado.

Linhas em branco são ignoradas, então dá para dividir as linhas entre o grupo e aplicar aos poucos.

## Tecnologias

Python, Flask, HTML, CSS, JavaScript, vis-network, NetworkX (só nos testes). Inspirado no
[BoscoGraph](https://github.com/Martonidaz/BoscoGraph).
