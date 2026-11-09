"""Preenche as planilhas de medição com a Routes API do Google (Compute Routes Essentials).

ATENÇÃO: a API é paga. Fica de graça só enquanto o uso do mês está abaixo da cota gratuita do
Google (10.000 chamadas de Compute Routes Essentials). Antes de rodar, siga o roteiro de travas
do README (cota de 100 chamadas/dia no Cloud Console, chave restrita à Routes API).

Travas deste script:
  * teto fixo de LIMITE_CHAMADAS por execução; acima disso nem começa;
  * pede confirmação antes da primeira chamada;
  * só pede distanceMeters, sem trânsito, sem paradas intermediárias -> sempre o SKU Essentials;
  * para na primeira resposta de erro (não fica tentando de novo);
  * a chave vem da variável de ambiente GOOGLE_MAPS_API_KEY e nunca é gravada em arquivo;
  * só preenche linhas em branco: não repete chamada para aresta já medida.

    python -m dados.medicoes gerar        # se as planilhas ainda não existirem
    python -m dados.rotas_api             # preenche as linhas vazias das planilhas
    (conferir as planilhas)
    python -m dados.medicoes aplicar      # grava nos JSON e valida
"""

import csv
import json
import os
import urllib.error
import urllib.request
from datetime import date

from dados.medicoes import GRAFOS, SEP, busca, caminhos

URL = "https://routes.googleapis.com/directions/v2:computeRoutes"
LIMITE_CHAMADAS = 60  # o projeto precisa de 47; folga pequena de propósito
FONTE = "Google Routes API"


def chamador(chave):
    """Devolve f(origem, destino) -> metros (int) ou None se o Google não achar rota."""

    def chamar(origem, destino):
        corpo = {
            "origin": {"address": origem},
            "destination": {"address": destino},
            "travelMode": "DRIVE",
            "routingPreference": "TRAFFIC_UNAWARE",  # TRAFFIC_AWARE mudaria para o SKU Pro
        }
        pedido = urllib.request.Request(
            URL,
            data=json.dumps(corpo).encode(),
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": chave,
                "X-Goog-FieldMask": "routes.distanceMeters",  # só o que precisamos
            },
        )
        with urllib.request.urlopen(pedido, timeout=20) as r:
            rotas = json.load(r).get("routes", [])
        return rotas[0]["distanceMeters"] if rotas else None

    return chamar


def pendentes(caminho_csv):
    with caminho_csv.open(newline="", encoding="utf-8-sig") as f:
        linhas = list(csv.reader(f, delimiter=SEP))
    col = next(i for i, c in enumerate(linhas[0]) if c.startswith("peso_medido_"))
    return linhas, col, [k for k in range(1, len(linhas)) if not linhas[k][col].strip()]


def preencher(caminho_csv, chamar, hoje):
    """Chama a API para cada linha vazia e grava o resultado na planilha. Devolve (ok, sem_rota)."""
    linhas, col, faltam = pendentes(caminho_csv)
    unidade = linhas[0][col].removeprefix("peso_medido_")
    ok, sem_rota = 0, []
    try:
        for k in faltam:
            metros = chamar(busca(linhas[k][1]), busca(linhas[k][2]))
            if metros is None:
                sem_rota.append(linhas[k][0])
                continue
            linhas[k][col] = (
                str(metros) if unidade == "m" else f"{metros / 1000:.2f}".replace(".", ",")
            )
            linhas[k][col + 1], linhas[k][col + 2] = FONTE, hoje
            ok += 1
    finally:  # mesmo se der erro no meio, o que já foi medido fica salvo (não paga duas vezes)
        with caminho_csv.open("w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f, delimiter=SEP).writerows(linhas)
    return ok, sem_rota


def main():
    chave = os.environ.get("GOOGLE_MAPS_API_KEY", "").strip()
    if not chave:
        raise SystemExit("Defina a variável de ambiente GOOGLE_MAPS_API_KEY (veja o README).")
    planilhas = [caminhos(n)[1] for n in GRAFOS]
    if not all(p.exists() for p in planilhas):
        raise SystemExit("Planilhas não encontradas: rode antes  python -m dados.medicoes gerar")

    total = sum(len(pendentes(p)[2]) for p in planilhas)
    if total == 0:
        raise SystemExit("Nenhuma linha vazia: nada para medir.")
    if total > LIMITE_CHAMADAS:
        raise SystemExit(
            f"{total} chamadas passariam do teto de {LIMITE_CHAMADAS}. Nada foi feito."
        )
    try:
        resposta = input(f"Vou fazer {total} chamadas à Routes API (Essentials). Continuar? [s/N] ")
    except EOFError:
        resposta = ""
    if resposta.strip().lower() != "s":
        raise SystemExit("Cancelado. Nenhuma chamada feita.")

    chamar, hoje = chamador(chave), date.today().strftime("%d/%m/%Y")
    for p in planilhas:
        try:
            ok, sem_rota = preencher(p, chamar, hoje)
        except urllib.error.HTTPError as e:
            raise SystemExit(
                f"Google respondeu {e.code}: {e.read().decode()[:500]}\nParei."
            ) from None
        print(
            f"{p.name}: {ok} medidas" + (f"; sem rota: {', '.join(sem_rota)}" if sem_rota else "")
        )
    print("Confira as planilhas e rode:  python -m dados.medicoes aplicar")


if __name__ == "__main__":
    main()
