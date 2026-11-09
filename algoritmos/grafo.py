# funcoes de apoio: ler os json, lista de adjacencia, distancia, etc

import json
import math
import os

PASTA_DADOS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dados")

ARQUIVOS = {
    "dijkstra": "lorena_transporte.json",
    "prim": "latam_aeroportos.json",
    "kruskal": "lorena_bairros.json",
}


def id_aresta(a, b):
    # ordena pra A|B e B|A virarem a mesma coisa (grafo nao direcionado)
    if a > b:
        a, b = b, a
    return a + "|" + b


def haversine_km(lat1, lon1, lat2, lon2):
    # distancia entre dois pontos na terra em km
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def carregar_grafo(nome):
    caminho = os.path.join(PASTA_DADOS, ARQUIVOS[nome])
    with open(caminho, encoding="utf-8") as f:
        grafo = json.load(f)

    por_id = {}
    for v in grafo["vertices"]:
        por_id[v["id"]] = v
        # aeroportos tem lat/lon, transforma em x/y pra desenhar
        if "lat" in v and "x" not in v:
            v["x"] = round((v["lon"] + 47) * 50)
            v["y"] = round(-(v["lat"] + 15) * 50)

    for a in grafo["arestas"]:
        # no grafo da latam o peso nao vem no arquivo, calcula pela distancia
        if "peso" not in a:
            p1 = por_id[a["origem"]]
            p2 = por_id[a["destino"]]
            a["peso"] = round(haversine_km(p1["lat"], p1["lon"], p2["lat"], p2["lon"]))
            a["fonte"] = "calculado (Haversine)"
        a["id"] = id_aresta(a["origem"], a["destino"])

    return grafo


def remover_arestas(grafo, removidas):
    # tira as arestas que o usuario desativou clicando no grafo
    if removidas is None:
        removidas = []
    return [a for a in grafo["arestas"] if a["id"] not in removidas]


def lista_adjacencia(vertices, arestas):
    adj = {}
    for v in vertices:
        adj[v] = []
    for a in arestas:
        # coloca nos dois sentidos
        adj[a["origem"]].append((a["destino"], a["peso"]))
        adj[a["destino"]].append((a["origem"], a["peso"]))
    return adj


def componentes_conexas(vertices, arestas):
    # BFS pra ver quantos "pedacos" o grafo tem
    adj = lista_adjacencia(vertices, arestas)
    visitado = set()
    componentes = []
    for inicio in vertices:
        if inicio in visitado:
            continue
        fila = [inicio]
        visitado.add(inicio)
        comp = []
        while fila:
            v = fila.pop(0)
            comp.append(v)
            for viz, _ in adj[v]:
                if viz not in visitado:
                    visitado.add(viz)
                    fila.append(viz)
        componentes.append(comp)
    return componentes


def formatar(valor, unidade):
    # formata no padrao brasileiro: 1,5 km / 1.250 m / 9.013 km
    if unidade == "m" or valor >= 100:
        texto = f"{round(valor):,}".replace(",", ".")
    else:
        texto = f"{round(valor, 2):g}".replace(".", ",")
    return f"{texto} {unidade}".strip()
