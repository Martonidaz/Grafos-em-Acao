"""Monta o grafo do Kruskal com todos os bairros de Lorena (lista dos Correios) usando a Routes API.

    $env:GOOGLE_MAPS_API_KEY = "..."
    python -m dados.bairros_api        # grava dados/lorena_bairros_todos.json (não mexe no grafo atual)

Passos: (1) localiza cada bairro (início da rota bairro -> Centro); (2) descarta pontos fora de Lorena;
(3) liga cada bairro aos 3 vizinhos mais próximos em linha reta e garante que o grafo seja conexo;
(4) mede a rota de carro de cada ligação. Mesmas travas do rotas_api: teto de chamadas, confirmação,
só SKU Essentials (sem trânsito), para no primeiro erro, chave só em variável de ambiente.
"""

import json
import os
import re
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from datetime import date
from itertools import combinations
from pathlib import Path

from algoritmos.grafo import PASTA_DADOS, haversine_km

URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
LIMITE_CHAMADAS = 200
VIZINHOS = 3
CENTRO = "Praça Arnolfo de Azevedo, Lorena - SP"
# caixa em volta de Lorena: ponto fora dela = bairro localizado em outra cidade
LAT, LON = (-22.82, -22.62), (-45.25, -45.00)
SAIDA = Path(PASTA_DADOS) / "lorena_bairros_todos.json"
PONTOS = Path(PASTA_DADOS) / "lorena_bairros_pontos.json"

# cepsdobrasil.com.br (base de CEPs dos Correios), consultado em 09/11/2026; sem "Área Rural de Lorena"
BAIRROS = [
    "Aterrado", "Cabelinha", "Campinho", "Cecap", "Centro", "Cidade Industrial",
    "Conjunto Habitacional de Interesse Social", "Cruz", "Jardim Margarida", "Jardim Novo Horizonte",
    "Loteamento Colinas de Lorena", "Loteamento Jardim Primavera", "Loteamento Lorena Village",
    "Loteamento Residencial Campos dos Ipês", "Loteamento Village das Palmeiras", "Madre Mazzarelo",
    "Matadouro Velho", "Nova Lorena", "Olaria", "Parque das Rodovias", "Parque Mondesir",
    "Parque Tabatinga", "Ponte Nova", "Portal das Palmeiras", "Residencial Brisas do Campo",
    "Residencial Doutor João Aldo Nassif", "Residencial Vila Rica", "Santa Lucrécia", "Santo Antônio",
    "Sapé", "Vila Brito", "Vila Buck", "Vila Cida", "Vila Cristina", "Vila dos Comerciários I",
    "Vila dos Comerciários II", "Vila Esperança", "Vila Fabiano", "Vila Geny", "Vila Hepacaré",
    "Vila Maria de Lourdes", "Vila Neide", "Vila Nunes", "Vila Passos", "Vila Portugal",
    "Vila Santa Edwiges", "Vila São Roque", "Vila Simão", "Vila Zélia",
]  # fmt: skip


def sigla(nome, usadas):
    base = re.sub(
        r"[^A-Z0-9]",
        "",
        unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode().upper(),
    )
    base = base.removeprefix("LOTEAMENTO").removeprefix("RESIDENCIAL").removeprefix("VILA") or base
    s, n = base[:4], 2
    while s in usadas:
        s, n = base[:3] + str(n), n + 1
    usadas.add(s)
    return s


def chamador(chave):
    contador = {"n": 0}

    def rota(origem, destino, campos):
        if contador["n"] >= LIMITE_CHAMADAS:
            raise SystemExit(f"Teto de {LIMITE_CHAMADAS} chamadas atingido. Parei.")
        contador["n"] += 1
        corpo = {"origin": origem, "destination": destino, "travelMode": "DRIVE",
                 "routingPreference": "TRAFFIC_UNAWARE"}  # fmt: skip
        pedido = urllib.request.Request(URL, data=json.dumps(corpo).encode(), headers={
            "Content-Type": "application/json", "X-Goog-Api-Key": chave, "X-Goog-FieldMask": campos})  # fmt: skip
        with urllib.request.urlopen(pedido, timeout=20) as r:
            rotas = json.load(r).get("routes", [])
        return rotas[0] if rotas else None

    return rota, contador


def vizinhancas(pontos):
    """Cada bairro com os VIZINHOS mais próximos; depois liga componentes soltos pelo par mais próximo."""
    ids = list(pontos)
    dist = {(a, b): haversine_km(*pontos[a], *pontos[b]) for a, b in combinations(ids, 2)}
    d = lambda a, b: dist[(a, b)] if (a, b) in dist else dist[(b, a)]  # noqa: E731 (0 km é válido)
    pares = set()
    for a in ids:
        for b in sorted((x for x in ids if x != a), key=lambda x: d(a, x))[:VIZINHOS]:
            pares.add(tuple(sorted((a, b))))
    grupo = {v: v for v in ids}

    def raiz(v):
        while grupo[v] != v:
            v = grupo[v]
        return v

    for a, b in pares:
        grupo[raiz(a)] = raiz(b)
    while len({raiz(v) for v in ids}) > 1:
        a, b = min(
            ((a, b) for a, b in combinations(ids, 2) if raiz(a) != raiz(b)), key=lambda p: d(*p)
        )
        pares.add(tuple(sorted((a, b))))
        grupo[raiz(a)] = raiz(b)
    return sorted(pares)


def main():
    chave = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not chave:
        raise SystemExit("Defina a variável de ambiente GOOGLE_MAPS_API_KEY.")
    estimativa = len(BAIRROS) + len(BAIRROS) * VIZINHOS // 2 + 10
    try:
        ok = input(
            f"Até ~{estimativa} chamadas (teto {LIMITE_CHAMADAS}), SKU Essentials. Continuar? [s/N] "
        )
    except EOFError:
        ok = ""
    if ok.strip().lower() != "s":
        raise SystemExit("Cancelado. Nenhuma chamada feita.")
    rota, contador = chamador(chave)
    centro = {"address": CENTRO}

    try:
        if PONTOS.exists():  # cache: não paga a localização duas vezes
            achados = json.loads(PONTOS.read_text(encoding="utf-8"))
        else:
            achados = {}
            for nome in BAIRROS:
                r = rota({"address": f"{nome}, Lorena - SP"}, centro, "routes.legs.startLocation")
                ll = r["legs"][0]["startLocation"]["latLng"] if r else None
                achados[nome] = [ll["latitude"], ll["longitude"]] if ll else None
            PONTOS.write_text(json.dumps(achados, ensure_ascii=False, indent=2), encoding="utf-8")

        usadas, vertices, pontos, fora = set(), [], {}, []
        mesmo_ponto = Counter(tuple(round(c, 5) for c in ll) for ll in achados.values() if ll)
        for nome, ll in achados.items():
            if not ll:
                fora.append(f"{nome} (não localizado)")
                continue
            lat, lon = ll
            if not (LAT[0] <= lat <= LAT[1] and LON[0] <= lon <= LON[1]):
                fora.append(f"{nome} (fora de Lorena: {lat:.4f}, {lon:.4f})")
                continue
            if mesmo_ponto[(round(lat, 5), round(lon, 5))] > 1:
                # o Google devolve um ponto genérico quando não acha o bairro: mesmo ponto = não achado
                fora.append(f"{nome} (impreciso: mesmo ponto de outro bairro)")
                continue
            vid = sigla(nome, usadas)
            pontos[vid] = (lat, lon)
            vertices.append({"id": vid, "nome": nome, "lat": round(lat, 6), "lon": round(lon, 6)})
        print(
            f"{len(vertices)} bairros localizados em Lorena; fora/descartados: {fora or 'nenhum'}"
        )

        hoje = date.today().strftime("%d/%m/%Y")
        arestas = []
        for a, b in vizinhancas(pontos):
            r = rota({"location": {"latLng": dict(zip(("latitude", "longitude"), pontos[a], strict=True))}},
                     {"location": {"latLng": dict(zip(("latitude", "longitude"), pontos[b], strict=True))}},
                     "routes.distanceMeters")  # fmt: skip
            if r and r.get("distanceMeters"):
                arestas.append({"origem": a, "destino": b, "peso": r["distanceMeters"],
                                "fonte": f"Google Routes API, rota de carro ({hoje})"})  # fmt: skip
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Google respondeu {e.code}: {e.read().decode()[:500]}\nParei.") from None

    # posições para desenhar: graus -> pixels, centradas na média
    mlat = sum(p[0] for p in pontos.values()) / len(pontos)
    mlon = sum(p[1] for p in pontos.values()) / len(pontos)
    for v in vertices:
        v["x"], v["y"] = round((v["lon"] - mlon) * 9000), round(-(v["lat"] - mlat) * 9000)
    SAIDA.write_text(json.dumps({"vertices": vertices, "arestas": arestas, "descartados": fora},
                                ensure_ascii=False, indent=2) + "\n", encoding="utf-8")  # fmt: skip
    print(f"{len(arestas)} vias medidas; {contador['n']} chamadas. Gravado em {SAIDA.name}.")
    print('Envie com:  git add dados && git commit -m "Bairros: todos" && git push')


if __name__ == "__main__":
    main()
