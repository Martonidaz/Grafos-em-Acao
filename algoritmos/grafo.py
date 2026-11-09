# funcoes de apoio: ler os json, lista de adjacencia, distancia, etc

import json
import math
import os
from collections import Counter, deque

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
        por_id[v.get("id")] = v
        # aeroportos tem lat/lon, transforma em x/y pra desenhar
        if "lat" in v and "x" not in v:
            v["x"] = round((v["lon"] + 47) * 50)
            v["y"] = round(-(v["lat"] + 15) * 50)

    for a in grafo["arestas"]:
        # no grafo da latam o peso nao vem no arquivo, calcula pela distancia
        p1 = por_id.get(a.get("origem"), {})
        p2 = por_id.get(a.get("destino"), {})
        if "peso" not in a and "lat" in p1 and "lat" in p2:
            a["peso"] = round(haversine_km(p1["lat"], p1["lon"], p2["lat"], p2["lon"]))
            a["fonte"] = "calculado (Haversine)"

    validar_grafo(grafo)
    for a in grafo["arestas"]:
        a["id"] = id_aresta(a["origem"], a["destino"])
    return grafo


def validar_grafo(grafo):
    # barra o dado ruim na entrada, antes de qualquer algoritmo rodar em cima dele
    titulo = grafo.get("titulo", "grafo")

    def erro(msg):
        return ValueError(f"{titulo}: {msg}")

    ids = [v.get("id") for v in grafo["vertices"]]
    if not ids:
        raise erro("grafo sem vértices.")
    repetidos = [i for i, n in Counter(ids).items() if n > 1]
    if repetidos:
        raise erro(f"id de vértice duplicado: {repetidos}.")

    existentes = set(ids)
    vistas = set()
    for a in grafo["arestas"]:
        o, d, peso = a.get("origem"), a.get("destino"), a.get("peso")
        via = f"aresta {o}-{d}"
        if o not in existentes or d not in existentes:
            raise erro(f"{via} usa vértice inexistente.")
        if o == d:
            raise erro(f"{via} é um laço (origem = destino).")
        # bool é subclasse de int em Python, por isso a checagem explícita
        if isinstance(peso, bool) or not isinstance(peso, (int, float)) or not math.isfinite(peso) or peso <= 0:
            raise erro(f"{via} tem peso inválido ({peso!r}); precisa ser um número maior que zero.")
        par = id_aresta(o, d)
        if par in vistas:
            raise erro(f"{via} duplicada (arestas paralelas não são suportadas; mantenha a menor).")
        vistas.add(par)


def remover_arestas(grafo, removidas):
    # tira as arestas que o usuario desativou clicando no grafo
    if removidas is None:
        removidas = []
    # string passaria aqui e o "in" viraria busca de substring
    if not isinstance(removidas, list):
        raise ValueError("'removidas' precisa ser uma lista de ids de arestas.")
    removidas = set(removidas)
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
        fila = deque([inicio])
        visitado.add(inicio)
        comp = []
        while fila:
            v = fila.popleft()  # O(1); list.pop(0) desloca a lista toda, O(n)
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
