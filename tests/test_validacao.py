# Defeitos 2 e 7 do docs/CONTEXTO.md: entrada inválida falha cedo, com ValueError e mensagem clara.

import pytest

import app as servidor
from algoritmos import dijkstra, remover_arestas
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
