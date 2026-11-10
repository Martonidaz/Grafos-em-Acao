# testes dos algoritmos
# rodar: python tests/test_algoritmos.py
# uso a networkx so pra conferir se o resultado bate (gabarito)

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import networkx as nx

from algoritmos import carregar_grafo, dijkstra, kruskal, prim, remover_arestas


def grafo_nx(g):
    G = nx.Graph()
    for v in g["vertices"]:
        G.add_node(v["id"])
    for a in g["arestas"]:
        G.add_edge(a["origem"], a["destino"], weight=a["peso"])
    return G


def ids(g):
    return [v["id"] for v in g["vertices"]]


def test_dijkstra_igual_networkx():
    g = carregar_grafo("dijkstra")
    G = grafo_nx(g)
    for o in ids(g):
        for d in ids(g):
            if o == d:
                continue
            r = dijkstra(ids(g), g["arestas"], o, d)
            assert r["ok"]
            assert abs(r["custo"] - nx.dijkstra_path_length(G, o, d)) < 0.001, (o, d)
            assert r["caminho"][0] == o and r["caminho"][-1] == d


def test_dijkstra_entradas_invalidas():
    g = carregar_grafo("dijkstra")
    casos = [("", "CEN"), ("CEN", ""), ("XXX", "CEN"), ("CEN", "XXX"), ("CEN", "CEN")]
    for o, d in casos:
        deu_erro = False
        try:
            dijkstra(ids(g), g["arestas"], o, d)
        except ValueError:
            deu_erro = True
        assert deu_erro, (o, d)


def test_dijkstra_desconexo():
    g = carregar_grafo("dijkstra")
    # tirando essas 3 o Aldo Nassif fica isolado
    arestas = remover_arestas(g, ["ALD|USP2", "ALD|SHO", "ALD|CAM"])
    r = dijkstra(ids(g), arestas, "CEN", "ALD")
    assert not r["ok"]
    assert "desconexo" in r["erro"]


def test_prim_igual_networkx():
    g = carregar_grafo("prim")
    esperado = nx.minimum_spanning_tree(grafo_nx(g)).size(weight="weight")
    for inicio in ids(g):  # testa comecando de todos
        r = prim(ids(g), g["arestas"], inicio)
        assert r["ok"]
        assert len(r["escolhidas"]) == len(ids(g)) - 1
        assert abs(r["custo"] - esperado) < 0.001


def test_prim_desconexo():
    g = carregar_grafo("prim")
    isolado = "MAO"  # Manaus: tira todas as rotas dele
    arestas = remover_arestas(g, [a["id"] for a in g["arestas"] if isolado in a["id"].split("|")])
    r = prim(ids(g), arestas, "GRU")
    assert not r["ok"]
    assert "MAO" in r["erro"]


def test_kruskal_igual_networkx():
    g = carregar_grafo("kruskal")
    esperado = nx.minimum_spanning_tree(grafo_nx(g), algorithm="kruskal").size(weight="weight")
    r = kruskal(ids(g), g["arestas"])
    assert r["ok"]
    assert len(r["aceitas"]) == len(ids(g)) - 1
    assert len(r["aceitas"]) + len(r["rejeitadas"]) == len(g["arestas"])
    assert abs(r["custo"] - esperado) < 0.001


def test_kruskal_desconexo():
    g = carregar_grafo("kruskal")
    isolado = g["vertices"][0]["id"]  # tira todas as vias de um bairro: ele fica isolado
    arestas = remover_arestas(g, [a["id"] for a in g["arestas"] if isolado in a["id"].split("|")])
    r = kruskal(ids(g), arestas)
    assert not r["ok"]
    assert "desconexo" in r["erro"]


def test_prim_e_kruskal_mesmo_custo():
    for nome in ["prim", "kruskal"]:
        g = carregar_grafo(nome)
        c1 = prim(ids(g), g["arestas"])["custo"]
        c2 = kruskal(ids(g), g["arestas"])["custo"]
        assert abs(c1 - c2) < 0.001


if __name__ == "__main__":
    testes = [
        test_dijkstra_igual_networkx,
        test_dijkstra_entradas_invalidas,
        test_dijkstra_desconexo,
        test_prim_igual_networkx,
        test_prim_desconexo,
        test_kruskal_igual_networkx,
        test_kruskal_desconexo,
        test_prim_e_kruskal_mesmo_custo,
    ]
    for t in testes:
        t()
        print("ok -", t.__name__)
    print("todos os testes passaram")
