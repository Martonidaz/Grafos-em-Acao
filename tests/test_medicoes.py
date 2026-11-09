import csv
import json
import shutil

import pytest

from dados.medicoes import SEP, aplicar, caminhos, gerar, numero


@pytest.mark.parametrize(("texto", "unidade", "esperado"), [
    ("1,7", "km", 1.7), ("0.4", "km", 0.4), ("12", "km", 12),
    ("850", "m", 850), ("1.250", "m", 1250), ("1250", "m", 1250), ("1.250,5", "m", 1250.5),
])  # fmt: skip
def test_numero_no_formato_brasileiro(texto, unidade, esperado):
    assert numero(texto, unidade) == esperado


@pytest.mark.parametrize("texto", ["1,7 km", "abc", "-3", ""])
def test_numero_recusa_texto(texto):
    with pytest.raises(ValueError, match="não é número"):
        numero(texto, "km")


def preparar(tmp_path):
    original, _ = caminhos("kruskal")
    js, cs = tmp_path / "g.json", tmp_path / "m.csv"
    shutil.copy(original, js)
    gerar(js, cs)
    with cs.open(newline="", encoding="utf-8-sig") as f:
        linhas = list(csv.reader(f, delimiter=SEP))
    return js, cs, linhas


def escrever(cs, linhas):
    with cs.open("w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f, delimiter=SEP).writerows(linhas)


def test_gerar_cria_um_link_do_maps_por_aresta(tmp_path):
    js, _, linhas = preparar(tmp_path)
    assert len(linhas) - 1 == len(json.loads(js.read_text(encoding="utf-8"))["arestas"])
    assert all(
        linha[-1].startswith("https://www.google.com/maps/dir/?api=1&") for linha in linhas[1:]
    )
    assert "key=" not in "".join(linha[-1] for linha in linhas[1:])  # sem chave = sem cobrança


def test_aplicar_grava_peso_e_fonte(tmp_path):
    js, cs, linhas = preparar(tmp_path)
    linhas[1][4:7] = ["1.432", "Daniel", "09/11/2026"]
    escrever(cs, linhas)

    assert aplicar(js, cs) == (1, 19)
    grafo = json.loads(js.read_text(encoding="utf-8"))
    medida = next(a for a in grafo["arestas"] if a.get("fonte", "").startswith("Google Maps"))
    assert medida["peso"] == 1432
    assert "Daniel" in medida["fonte"]
    assert grafo["tipo_dado"] == "parcial (19 arestas sem medida)"


def test_aplicar_nao_grava_nada_se_um_valor_for_invalido(tmp_path):
    js, cs, linhas = preparar(tmp_path)
    antes = js.read_text(encoding="utf-8")
    linhas[1][4] = "1,4 km"
    escrever(cs, linhas)
    with pytest.raises(ValueError, match="linha 2"):
        aplicar(js, cs)
    assert js.read_text(encoding="utf-8") == antes
