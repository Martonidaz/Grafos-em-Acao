"""Monta o grafo do Prim com as rotas REAIS da LATAM a partir do VRA (Voo Regular Ativo) da ANAC.

    python -m dados.vra_latam CAMINHO_DO_ARQUIVO_VRA.csv   # grava dados/latam_vra.json para revisão

- vértices: aeroportos brasileiros onde a LATAM (ICAO "TAM") operou voos domésticos realizados;
- arestas: pares de aeroportos com voo realizado (em qualquer sentido), com pelo menos MIN_VOOS voos;
- peso: duração real do voo em minutos (chegada real - partida real). Usa a mediana de cada sentido e
  a média dos dois sentidos: se o arquivo usar hora local, a diferença de fuso entra com sinal oposto
  na ida e na volta e se cancela.
Não chama nenhuma API. Coordenadas: dados/aeroportos_br.csv (OurAirports, domínio público).
"""

import csv
import io
import json
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from algoritmos.grafo import PASTA_DADOS

LATAM = "TAM"
MIN_VOOS = 4
SAIDA = Path(PASTA_DADOS) / "latam_vra.json"
FORMATOS = ("%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")


def normal(texto):
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()


def ler(caminho):
    bruto = Path(caminho).read_bytes()
    for cod in ("utf-8-sig", "latin-1"):
        try:
            texto = bruto.decode(cod)
            break
        except UnicodeDecodeError:
            continue
    linhas = texto.splitlines()
    # alguns arquivos da ANAC têm linhas de aviso antes do cabeçalho: procura a linha com "icao"
    i = next(k for k, linha in enumerate(linhas[:20]) if "icao" in normal(linha))
    sep = ";" if linhas[i].count(";") > linhas[i].count(",") else ","
    leitor = csv.reader(io.StringIO("\n".join(linhas[i:])), delimiter=sep)
    cab = [normal(c) for c in next(leitor)]

    def coluna(*partes):
        achou = [k for k, c in enumerate(cab) if all(p in c for p in partes)]
        if not achou:
            raise SystemExit(f"Coluna com {partes} não encontrada. Cabeçalho: {cab}")
        return achou[0]

    col = {
        "empresa": coluna("empresa"),
        "origem": coluna("origem"),
        "destino": coluna("destino"),
        "partida": coluna("partida", "real"),
        "chegada": coluna("chegada", "real"),
        "situacao": coluna("situa"),
    }
    return [{k: (r[v].strip() if v < len(r) else "") for k, v in col.items()} for r in leitor if r]


def hora(texto):
    for f in FORMATOS:
        try:
            return datetime.strptime(texto, f)
        except ValueError:
            continue
    return None


def montar(linhas, aeroportos):
    print("empresas mais frequentes:", Counter(r["empresa"] for r in linhas).most_common(6))
    sentido = defaultdict(list)
    for r in linhas:
        if r["empresa"] != LATAM or "realizado" not in normal(r["situacao"]):
            continue
        o, d = r["origem"], r["destino"]
        if o not in aeroportos or d not in aeroportos or o == d:
            continue  # só voo doméstico entre aeroportos conhecidos
        p, c = hora(r["partida"]), hora(r["chegada"])
        if p and c and 0 < (minutos := (c - p).total_seconds() / 60) < 600:
            sentido[(o, d)].append(minutos)
    print(f"voos LATAM domésticos realizados: {sum(map(len, sentido.values()))}")

    arestas = []
    for a, b in {tuple(sorted(k)) for k in sentido}:
        ida, volta = sentido.get((a, b), []), sentido.get((b, a), [])
        if len(ida) + len(volta) < MIN_VOOS:
            continue
        medias = [statistics.median(x) for x in (ida, volta) if x]
        arestas.append({"origem": a, "destino": b, "peso": round(sum(medias) / len(medias)),
                        "voos": len(ida) + len(volta),
                        "fonte": "ANAC VRA (duração real, mediana por sentido)"})  # fmt: skip
    usados = sorted({x for a in arestas for x in (a["origem"], a["destino"])})
    vertices = [{"id": aeroportos[i]["iata"] or i, "icao": i,
                 "nome": f"{aeroportos[i]['cidade']} ({aeroportos[i]['iata'] or i})",
                 "lat": float(aeroportos[i]["lat"]), "lon": float(aeroportos[i]["lon"])} for i in usados]  # fmt: skip
    ids = {v["icao"]: v["id"] for v in vertices}
    for a in arestas:
        a["origem"], a["destino"] = ids[a["origem"]], ids[a["destino"]]
    return vertices, sorted(arestas, key=lambda a: (a["origem"], a["destino"]))


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    with (Path(PASTA_DADOS) / "aeroportos_br.csv").open(encoding="utf-8") as f:
        aeroportos = {r["icao"]: r for r in csv.DictReader(f)}
    vertices, arestas = montar(ler(sys.argv[1]), aeroportos)
    SAIDA.write_text(json.dumps({"vertices": vertices, "arestas": arestas, "arquivo_vra": Path(sys.argv[1]).name},
                                ensure_ascii=False, indent=2) + "\n", encoding="utf-8")  # fmt: skip
    print(f"{len(vertices)} aeroportos e {len(arestas)} rotas LATAM. Gravado em {SAIDA.name}.")
    print('Envie com:  git add dados && git commit -m "Prim: rotas reais VRA" && git push')


if __name__ == "__main__":
    main()
