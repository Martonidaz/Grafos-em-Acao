# Referências dos dados

Consultadas em outubro de 2026; distâncias de Lorena medidas em 09/11/2026.

## Dijkstra — transporte público de Lorena/SP (`lorena_transporte.json`)

- Diário do Transporte — *Lorena (SP) altera itinerários de três linhas de ônibus* (16/03/2022). Operadora ABC Transportes; pontos Aldo Nassif, USP II, Shopping, Centro, USP I, Campinho, Novo Horizonte, Bairro da Cruz, Parque das Rodovias. https://diariodotransporte.com.br/2022/03/16/lorena-sp-altera-itinerarios-de-tres-linhas-de-onibus/
- Mobilidade Sampa — *Itinerários de três linhas de ônibus são atualizados em Lorena* (03/2022). https://mobilidadesampa.com.br/2022/03/lorena-itinerarios-linhas-de-onibus-atualizacao/
- Prefeitura de Lorena — Horário de ônibus. http://www.lorena.sp.gov.br/wordpress/index.php/horario-de-onibus-lorena-2/
- CEPs Brasil — Bairros de Lorena/SP. https://cepsbrasil.com.br/sp/lorena

- Google Maps — distância da rota de carro de cada ligação (27), pela Routes API (sem trânsito) e conferida no site; vale a menor rota encontrada. Fonte de cada aresta no campo `fonte` do JSON e em `dados/medicoes_dijkstra.csv`.

**Limitação:** os itinerários completos (ruas) das linhas não estavam disponíveis nas fontes consultadas. As **distâncias são reais**, mas **quais pontos se ligam** é um modelo do grupo. A versão anterior usava 0,4 e 0,7 km da Buser para Estação–Praça e Estação–Rodoviária; foram trocadas pela rota de carro para todas as arestas seguirem o mesmo critério.

## Prim — LATAM (`latam_aeroportos.json`)

- Wikipedia — *LATAM Airlines Brasil*: hubs Brasília, Fortaleza, São Paulo–Congonhas e São Paulo–Guarulhos; cidades-foco Porto Alegre, Rio de Janeiro–Galeão, Belo Horizonte–Confins, Florianópolis e Recife; lista de destinos domésticos. https://en.wikipedia.org/wiki/LATAM_Airlines_Brasil
- Poder360 — *Latam amplia voos e consolida Brasília como hub doméstico*. https://www.poder360.com.br/poder-infra/latam-amplia-voos-e-consolida-brasilia-como-hub-domestico/
- Mercado & Eventos — *Expansão da Latam impulsiona oferta de voos em Brasília, Guarulhos, Porto Alegre e Curitiba*. https://www.mercadoeeventos.com.br/noticias/aviacao/expansao-da-latam-impulsiona-oferta-de-voos-em-brasilia-guarulhos-porto-alegre-e-curitiba/
- Coordenadas dos aeroportos: valores aproximados (Google Maps). Pesos = distância ortodrômica por Haversine, calculada em `algoritmos/grafo.py`.

**Limitação:** São Paulo foi representada só por Guarulhos (GRU) para simplificar. As arestas são as ligações hub/base ↔ destino do modelo, e não uma lista verificada de voos operados.

## Kruskal — bairros de Lorena/SP (`lorena_bairros.json`)

- CEPs do Brasil — Bairros de Lorena/SP (base de CEPs dos Correios, 50 bairros). https://www.cepsdobrasil.com.br/cep/sp/lorena/bairros
- Google Maps (Routes API), 09/11/2026 — localização de cada bairro e distância da rota de carro de cada via (65 vias).
  Gerado por `python -m dados.bairros_api`; localizações em `dados/lorena_bairros_pontos.json`.

**Recorte:** 35 dos 50 bairros. Fora: Área Rural (não é um ponto), 13 bairros que o Google não localizou com
precisão (vários caíram no mesmo ponto genérico; um caiu perto de São Paulo) e Vila dos Comerciários II
(localizada a ~17 km do centro). As vias candidatas ligam cada bairro aos 3 vizinhos mais próximos, com
conexidade garantida; o comprimento de cada via é real.

## Teoria

- CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C. *Algoritmos: teoria e prática*. 3. ed. Rio de Janeiro: Elsevier, 2012.
