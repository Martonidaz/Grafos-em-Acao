# Defeitos 2 e 7 do docs/CONTEXTO.md: entrada inválida falha cedo, com ValueError e mensagem clara.

import pytest

import app as servidor
from algoritmos import carregar_grafo, dijkstra, remover_arestas
from algoritmos.grafo import validar_grafo


def grafo(arestas, vertices=("A", "B", "C")):
    return {
        "titulo": "teste",
        "vertices": [{"id": v, "nome": v} for v in vertices],
        "arestas": arestas,
    }


def test_grafo_valido_passa():
    validar_grafo(
        grafo(
            [
                {"origem": "A", "destino": "B", "peso": 1},
                {"origem": "B", "destino": "C", "peso": 2.5},
            ]
        )
    )


@pytest.mark.parametrize(
    ("g", "trecho"),
    [
        (grafo([], vertices=()), "sem vértices"),
        (grafo([], vertices=("A", "A")), "duplicado"),
        (grafo([{"origem": "A", "destino": "X", "peso": 1}]), "inexistente"),
        (grafo([{"destino": "B", "peso": 1}]), "inexistente"),
        (grafo([{"origem": "A", "destino": "A", "peso": 1}]), "laço"),
        (grafo([{"origem": "A", "destino": "B", "peso": -3}]), "peso"),
        (grafo([{"origem": "A", "destino": "B", "peso": 0}]), "peso"),
        (grafo([{"origem": "A", "destino": "B", "peso": "5"}]), "peso"),
        (grafo([{"origem": "A", "destino": "B", "peso": True}]), "peso"),
        (grafo([{"origem": "A", "destino": "B", "peso": float("nan")}]), "peso"),
        (grafo([{"origem": "A", "destino": "B"}]), "peso"),
        (
            grafo(
                [
                    {"origem": "A", "destino": "B", "peso": 1},
                    {"origem": "B", "destino": "A", "peso": 2},
                ]
            ),
            "duplicada",
        ),
    ],
)
def test_grafo_invalido_falha_cedo(g, trecho):
    with pytest.raises(ValueError, match=trecho):
        validar_grafo(g)


def test_dijkstra_recusa_peso_negativo():
    arestas = [{"origem": "A", "destino": "B", "peso": -1}]
    with pytest.raises(ValueError, match="negativo"):
        dijkstra(["A", "B"], arestas, "A", "B")


def test_remover_arestas_recusa_string():
    # "A|B" in "CEN|ALD" seria busca de substring, não de pertencimento
    with pytest.raises(ValueError, match="lista"):
        remover_arestas({"arestas": []}, "CEN|ALD")


def test_api_responde_400_para_entrada_invalida():
    cliente = servidor.app.test_client()
    r = cliente.post(
        "/api/dijkstra", json={"origem": "CEN", "destino": "ALD", "removidas": "CEN|ALD"}
    )
    assert r.status_code == 400
    assert not r.get_json()["ok"]


def test_filtro_de_vertices_roda_no_subgrafo():
    cliente = servidor.app.test_client()
    poucos = ["GRU", "BSB", "CGH", "GIG"]
    r = cliente.post("/api/prim", json={"inicio": "GRU", "vertices": poucos}).get_json()
    assert r["ok"] and len(r["escolhidas"]) == len(poucos) - 1
    assert cliente.post("/api/kruskal", json={"vertices": "GRU"}).status_code == 400


def test_linhas_reais_estao_nas_arestas_certas():
    # Diário do Transporte (16/03/2022): linha 8, linha 6 e linhas 3/5 da ABC Transportes
    com_linha = {
        a["id"]: a["linhas"] for a in carregar_grafo("dijkstra")["arestas"] if "linhas" in a
    }
    assert com_linha == {
        "ALD|USP2": ["8"], "SHO|USP2": ["8"], "CEN|SHO": ["6"], "CEN|USP1": ["6"],
        "CAM|USP1": ["6"], "CRU|NOV": ["3", "5"], "CRU|PRO": ["3", "5"],
    }  # fmt: skip
