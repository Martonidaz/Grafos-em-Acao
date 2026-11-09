"""Medição dos pesos no Google Maps, de graça (sem API, sem chave, sem cobrança).

O fluxo usa só links do Maps (Maps URLs), que abrem a rota no navegador; quem mede lê a distância
na tela e anota na planilha. Nada aqui chama API paga do Google.

    python -m dados.medicoes gerar     # cria dados/medicoes_<grafo>.csv (não sobrescreve)
    (abrir o CSV no Excel/Sheets, clicar em cada link, preencher peso_medido, medido_por, data)
    python -m dados.medicoes aplicar   # grava os pesos medidos nos JSON, com a fonte, e valida
"""

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlencode

from algoritmos.grafo import ARQUIVOS, PASTA_DADOS, id_aresta, validar_grafo

GRAFOS = ["dijkstra", "kruskal"]  # LATAM fica fora: voo é linha reta, Haversine já resolve
CIDADE = ", Lorena - SP"
SEP = ";"  # Excel em português abre CSV com ";" e vírgula decimal


def caminhos(nome):
    return Path(PASTA_DADOS) / ARQUIVOS[nome], Path(PASTA_DADOS) / f"medicoes_{nome}.csv"


def busca(nome_vertice):
    # "Centro (Praça X)" / "Estação / Basílica" -> só a primeira parte, mais a cidade
    return re.split(r" \(| /", nome_vertice)[0] + CIDADE


def link_maps(origem, destino):
    params = {"api": 1, "origin": origem, "destination": destino, "travelmode": "driving"}
    return "https://www.google.com/maps/dir/?" + urlencode(params)


def numero(texto, unidade):
    # aceita o jeito brasileiro: "1,7" (km) e "1.250" ou "1250" (m); recusa texto como "1,7 km"
    if not re.fullmatch(r"\d[\d.]*(,\d+)?", texto):
        raise ValueError(f"{texto!r} não é número (digite só o valor, em {unidade}).")
    if "," in texto or unidade == "m":
        texto = texto.replace(".", "").replace(",", ".")
    return float(texto)


def gerar(caminho_json, caminho_csv):
    if caminho_csv.exists():
        raise SystemExit(f"{caminho_csv.name} já existe; apague-o se quiser recomeçar do zero.")
    grafo = json.loads(caminho_json.read_text(encoding="utf-8"))
    nomes = {v["id"]: v["nome"] for v in grafo["vertices"]}
    unidade = grafo["unidade"]
    with caminho_csv.open("w", newline="", encoding="utf-8-sig") as f:  # BOM: acentos no Excel
        w = csv.writer(f, delimiter=SEP)
        w.writerow(["id", "origem", "destino", "peso_atual", f"peso_medido_{unidade}",
                    "medido_por", "data", "link_google_maps"])  # fmt: skip
        for a in grafo["arestas"]:
            o, d = a["origem"], a["destino"]
            w.writerow([id_aresta(o, d), nomes[o], nomes[d], a["peso"], "", "", "",
                        link_maps(busca(nomes[o]), busca(nomes[d]))])  # fmt: skip
    return len(grafo["arestas"])


def aplicar(caminho_json, caminho_csv):
    grafo = json.loads(caminho_json.read_text(encoding="utf-8"))
    unidade = grafo["unidade"]
    por_id = {id_aresta(a["origem"], a["destino"]): a for a in grafo["arestas"]}
    with caminho_csv.open(newline="", encoding="utf-8-sig") as f:
        linhas = list(csv.DictReader(f, delimiter=SEP))

    aplicadas = 0
    for n, linha in enumerate(linhas, start=2):  # linha 1 é o cabeçalho
        bruto = linha[f"peso_medido_{unidade}"].strip()
        if not bruto:
            continue
        if linha["id"] not in por_id:
            raise ValueError(
                f"{caminho_csv.name}, linha {n}: aresta {linha['id']} não existe no grafo."
            )
        try:
            peso = numero(bruto, unidade)
        except ValueError as e:
            raise ValueError(f"{caminho_csv.name}, linha {n}: {e}") from None
        quem = linha["medido_por"].strip() or "?"
        quando = linha["data"].strip() or "?"
        a = por_id[linha["id"]]
        a["peso"] = int(peso) if peso.is_integer() else peso
        a["fonte"] = f"Google Maps, rota de carro (medido por {quem} em {quando})"
        aplicadas += 1

    if aplicadas == 0:
        return 0, None  # nada novo: não reescreve o JSON
    faltam = sum(1 for a in grafo["arestas"] if a.get("fonte", "demonstrativo") == "demonstrativo")
    grafo["tipo_dado"] = "medido" if faltam == 0 else f"parcial ({faltam} arestas sem medida)"
    validar_grafo(json.loads(json.dumps(grafo)))  # valida uma cópia: só grava se estiver tudo certo
    caminho_json.write_text(
        json.dumps(grafo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return aplicadas, faltam


if __name__ == "__main__":
    comando = sys.argv[1] if len(sys.argv) > 1 else ""
    if comando not in ("gerar", "aplicar"):
        raise SystemExit(__doc__)
    for nome in GRAFOS:
        js, cs = caminhos(nome)
        if comando == "gerar":
            print(f"{cs.name}: {gerar(js, cs)} arestas para medir")
        else:
            feitas, faltam = aplicar(js, cs)
            if feitas:
                print(f"{js.name}: {feitas} pesos aplicados, {faltam} arestas ainda sem medida")
            else:
                print(f"{js.name}: nenhuma medida preenchida em {cs.name}")
