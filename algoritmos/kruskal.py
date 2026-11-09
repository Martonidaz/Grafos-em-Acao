# Algoritmo de Kruskal (arvore geradora minima)
# ordena as arestas pelo peso e vai pegando da menor pra maior,
# pulando as que formariam ciclo

from .grafo import formatar


# Union-Find pra saber se dois vertices ja estao no mesmo grupo
class UnionFind:
    def __init__(self, vertices):
        self.pai = {}
        for v in vertices:
            self.pai[v] = v  # cada um comeca sendo o proprio grupo

    def encontrar(self, v):
        # sobe ate achar o representante do grupo
        while self.pai[v] != v:
            self.pai[v] = self.pai[
                self.pai[v]
            ]  # path halving: aponta pro avo, encurta o caminho pela metade
            v = self.pai[v]
        return v

    def unir(self, a, b):
        ra = self.encontrar(a)
        rb = self.encontrar(b)
        if ra == rb:
            return False  # ja estavam juntos -> ciclo
        self.pai[rb] = ra
        return True

    def grupos(self):
        g = {}
        for v in self.pai:
            r = self.encontrar(v)
            if r not in g:
                g[r] = []
            g[r].append(v)
        return list(g.values())


def kruskal(vertices, arestas, nomes=None, unidade=""):
    if len(vertices) == 0:
        raise ValueError("O grafo não possui vértices.")
    if nomes is None:
        nomes = {v: v for v in vertices}

    ordenadas = sorted(arestas, key=lambda a: a["peso"])

    uf = UnionFind(vertices)
    aceitas = []
    rejeitadas = []
    custo = 0

    ordem = ", ".join(
        f"{a['origem']}-{a['destino']} ({formatar(a['peso'], unidade)})" for a in ordenadas
    )
    passos = [
        {
            "texto": "Início: cada bairro é um grupo separado. Arestas em ordem crescente: "
            + ordem,
            "aceitas": [],
            "rejeitadas": [],
            "atual": None,
            "decisao": None,
        }
    ]

    for i, a in enumerate(ordenadas):
        u = a["origem"]
        v = a["destino"]
        via = f"{nomes[u]} - {nomes[v]} ({formatar(a['peso'], unidade)})"

        if uf.unir(u, v):
            aceitas.append(a)
            custo += a["peso"]
            decisao = "aceita"
            texto = (
                f"ACEITA {via}: estavam em grupos diferentes. Total: {formatar(custo, unidade)}."
            )
        else:
            rejeitadas.append(a)
            decisao = "rejeitada"
            texto = f"REJEITA {via}: {nomes[u]} e {nomes[v]} já estão ligados, ia formar ciclo."

        grupos = []
        for g in uf.grupos():
            grupos.append("{" + ", ".join(sorted(nomes[x] for x in g)) + "}")

        passos.append(
            {
                "texto": texto,
                "detalhes": ["Grupos: " + " | ".join(grupos)],
                "aceitas": [x["id"] for x in aceitas],
                "rejeitadas": [x["id"] for x in rejeitadas],
                "atual": a["id"],
                "decisao": decisao,
            }
        )

        # com V-1 arestas ja ta tudo ligado
        if len(aceitas) == len(vertices) - 1:
            resto = ordenadas[i + 1 :]
            if len(resto) > 0:
                rejeitadas.extend(resto)
                passos.append(
                    {
                        "texto": f"Já tem V - 1 = {len(vertices) - 1} vias, todos os bairros "
                        f"ligados. As {len(resto)} vias que sobraram são descartadas "
                        "(todas formariam ciclo).",
                        "aceitas": [x["id"] for x in aceitas],
                        "rejeitadas": [x["id"] for x in rejeitadas],
                        "atual": None,
                        "decisao": None,
                    }
                )
            break

    descartadas = []
    for r in rejeitadas:
        descartadas.append(
            {
                "origem": r["origem"],
                "destino": r["destino"],
                "peso": r["peso"],
                "motivo": "formaria ciclo (os bairros já estavam ligados por vias menores)",
            }
        )

    resultado = {
        "aceitas": [x["id"] for x in aceitas],
        "rejeitadas": [x["id"] for x in rejeitadas],
        "arestas_aceitas": [
            {"origem": x["origem"], "destino": x["destino"], "peso": x["peso"]} for x in aceitas
        ],
        "descartadas": descartadas,
        "custo": round(custo, 2),
        "custo_formatado": formatar(custo, unidade),
        "passos": passos,
        "ok": True,
    }

    # se nao conseguiu V-1 arestas o grafo eh desconexo (vira uma floresta)
    if len(aceitas) < len(vertices) - 1:
        grupos = [[nomes[x] for x in g] for g in uf.grupos()]
        resultado["ok"] = False
        resultado["erro"] = (
            f"Grafo desconexo: ficaram {len(grupos)} partes separadas, "
            "não dá pra ligar todos os bairros."
        )
        resultado["grupos"] = grupos

    return resultado
