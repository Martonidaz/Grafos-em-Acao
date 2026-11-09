# Grafos em Ação

Trabalho final de Grafos (P2). Sistema web com os algoritmos de **Dijkstra**, **Prim** e **Kruskal**
feitos em Python, com interface em HTML/CSS/JS.

- **Dijkstra**: melhor rota entre dois pontos do transporte público de Lorena/SP
- **Prim**: rede mínima ligando os principais aeroportos da LATAM no Brasil
- **Kruskal**: quais vias pavimentar pra ligar todos os bairros gastando o mínimo

![Dijkstra](docs/capturas/dijkstra.png)

## Como rodar

Precisa do Python 3.9+.

```
pip install -r requirements.txt
python app.py
```

Depois abre http://127.0.0.1:5000 no navegador.

Testes:

```
python tests/test_algoritmos.py
```

## Organização

```
app.py               servidor flask e rotas da api
algoritmos/          dijkstra.py, prim.py, kruskal.py e grafo.py (funções de apoio)
dados/               os 3 grafos em json + referências
templates/           páginas html
static/              css, js e a biblioteca vis-network
tests/               testes (usa networkx só pra comparar o resultado)
docs/                apresentação e prints
```

## O que dá pra fazer

- escolher origem/destino (Dijkstra) ou aeroporto inicial (Prim) e executar
- ver o resultado destacado no grafo e o custo total
- ver o passo a passo da execução (anterior, próximo, reproduzir)
- clicar numa aresta pra desativar ela e ver o que acontece (outra rota ou grafo desconexo)
- restaurar o grafo original

## Sobre os dados

Os nomes dos pontos, bairros e aeroportos são reais (fontes em `dados/REFERENCIAS.md`), mas:

- **Dijkstra**: as ligações e distâncias são estimadas pra demonstração (só 2 têm fonte). Não é o itinerário oficial das linhas.
- **Prim**: as conexões são um modelo com os hubs da LATAM, não a malha real de voos. A distância é calculada pela fórmula de Haversine com as coordenadas dos aeroportos.
- **Kruskal**: as vias e os comprimentos são estimados pra demonstração.

Pra usar valores reais é só medir no Google Maps (botão direito > Medir distância) e trocar o `peso` no json da pasta `dados/`.

## Tecnologias

Python, Flask, HTML, CSS, JavaScript, vis-network, NetworkX (só nos testes)
