# Nenhum teste chama o Google: a função que chamaria a API é trocada por uma falsa.

import shutil

import pytest

from dados.medicoes import caminhos, gerar
from dados.rotas_api import FONTE, pendentes, preencher


def planilha(tmp_path, nome):
    js, cs = tmp_path / "g.json", tmp_path / "m.csv"
    shutil.copy(caminhos(nome)[0], js)
    gerar(js, cs)
    return cs


@pytest.mark.parametrize(("nome", "esperado"), [("kruskal", "1234"), ("dijkstra", "1,23")])
def test_preenche_em_metros_e_em_km(tmp_path, nome, esperado):
    cs = planilha(tmp_path, nome)
    chamadas = []
    ok, sem_rota = preencher(cs, lambda o, d: chamadas.append((o, d)) or 1234, "09/11/2026")
    linhas, col, faltam = pendentes(cs)
    assert ok == len(chamadas) == len(linhas) - 1 and sem_rota == [] and faltam == []
    assert linhas[1][col : col + 3] == [esperado, FONTE, "09/11/2026"]
    assert all(o.endswith(", Lorena - SP") for o, _ in chamadas)


def test_nao_chama_de_novo_linha_ja_medida(tmp_path):
    cs = planilha(tmp_path, "kruskal")
    preencher(cs, lambda o, d: 1000, "hoje")
    chamadas = []
    assert preencher(cs, lambda o, d: chamadas.append(1) or 1, "hoje") == (0, [])
    assert chamadas == []


def test_sem_rota_fica_em_branco(tmp_path):
    cs = planilha(tmp_path, "kruskal")
    ok, sem_rota = preencher(cs, lambda o, d: None, "hoje")
    assert ok == 0 and len(sem_rota) == 20 and len(pendentes(cs)[2]) == 20


def test_erro_no_meio_salva_o_que_ja_foi_medido(tmp_path):
    cs = planilha(tmp_path, "kruskal")
    respostas = iter([500, 600])

    def falha_na_terceira(o, d):
        return next(respostas)  # StopIteration na 3ª chamada simula a API caindo

    with pytest.raises(StopIteration):
        preencher(cs, falha_na_terceira, "hoje")
    assert len(pendentes(cs)[2]) == 18
