# Referências dos dados

Consultadas em outubro de 2026.

## Dijkstra — transporte público de Lorena/SP (`lorena_transporte.json`)

- Diário do Transporte — *Lorena (SP) altera itinerários de três linhas de ônibus* (16/03/2022). Operadora ABC Transportes; pontos Aldo Nassif, USP II, Shopping, Centro, USP I, Campinho, Novo Horizonte, Bairro da Cruz, Parque das Rodovias. https://diariodotransporte.com.br/2022/03/16/lorena-sp-altera-itinerarios-de-tres-linhas-de-onibus/
- Mobilidade Sampa — *Itinerários de três linhas de ônibus são atualizados em Lorena* (03/2022). https://mobilidadesampa.com.br/2022/03/lorena-itinerarios-linhas-de-onibus-atualizacao/
- Buser — Estação Ferroviária de Lorena e pontos próximos (Praça Arnolfo de Azevedo a 0,4 km; Terminal Rodoviário a 0,7 km). https://www.buser.com.br/destinos/pontos-turisticos/sp/lorena/estacao-ferroviaria-de-lorena
- Prefeitura de Lorena — Horário de ônibus. http://www.lorena.sp.gov.br/wordpress/index.php/horario-de-onibus-lorena-2/
- CEPs Brasil — Bairros de Lorena/SP. https://cepsbrasil.com.br/sp/lorena

**Limitação:** os itinerários completos (ruas) das linhas não estavam disponíveis nas fontes consultadas. Por isso as ligações e distâncias (exceto as duas da Buser) são demonstrativas.

## Prim — LATAM (`latam_aeroportos.json`)

- Wikipedia — *LATAM Airlines Brasil*: hubs Brasília, Fortaleza, São Paulo–Congonhas e São Paulo–Guarulhos; cidades-foco Porto Alegre, Rio de Janeiro–Galeão, Belo Horizonte–Confins, Florianópolis e Recife; lista de destinos domésticos. https://en.wikipedia.org/wiki/LATAM_Airlines_Brasil
- Poder360 — *Latam amplia voos e consolida Brasília como hub doméstico*. https://www.poder360.com.br/poder-infra/latam-amplia-voos-e-consolida-brasilia-como-hub-domestico/
- Mercado & Eventos — *Expansão da Latam impulsiona oferta de voos em Brasília, Guarulhos, Porto Alegre e Curitiba*. https://www.mercadoeeventos.com.br/noticias/aviacao/expansao-da-latam-impulsiona-oferta-de-voos-em-brasilia-guarulhos-porto-alegre-e-curitiba/
- Coordenadas dos aeroportos: valores aproximados (Google Maps). Pesos = distância ortodrômica por Haversine, calculada em `algoritmos/grafo.py`.

**Limitação:** São Paulo foi representada só por Guarulhos (GRU) para simplificar. As arestas são as ligações hub/base ↔ destino do modelo, e não uma lista verificada de voos operados.

## Kruskal — bairros de Lorena/SP (`lorena_bairros.json`)

- CEPs Brasil — Bairros de Lorena/SP. https://cepsbrasil.com.br/sp/lorena
- Google Maps — referência para medir as vias. https://www.google.com/maps/place/Lorena,+SP

**Limitação:** vias e comprimentos demonstrativos.

## Teoria

- CORMEN, T. H.; LEISERSON, C. E.; RIVEST, R. L.; STEIN, C. *Algoritmos: teoria e prática*. 3. ed. Rio de Janeiro: Elsevier, 2012.
