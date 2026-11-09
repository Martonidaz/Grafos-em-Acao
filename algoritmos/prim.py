# Algoritmo de Prim (arvore geradora minima)
# comeca com 1 vertice e vai adicionando sempre a aresta mais barata
# que liga a arvore a um vertice que ainda esta fora dela

from .grafo import formatar


def prim(vertices, arestas, inicio=None, nomes=None, unidade=""):
    if len(vertices) == 0:
        raise ValueError("O grafo não possui vértices.")
    if inicio is None:
        inicio = vertices[0]
    if inicio not in vertices:
        raise ValueError(f"O vértice inicial '{inicio}' não existe no grafo.")
    if nomes is None:
        nomes = {v: v for v in vertices}

    na_arvore = set()
    na_arvore.add(inicio)
    escolhidas = []
    custo = 0

    passos = [{
        "texto": f"Início: a árvore tem só {nomes[inicio]}.",
        "na_arvore": [inicio],
        "escolhidas": [],
        "candidatas": [],
        "atual": None,
    }]

    while len(na_arvore) < len(vertices):
        # candidatas = arestas com uma ponta dentro e a outra fora da arvore
        candidatas = []
        for a in arestas:
            dentro_origem = a["origem"] in na_arvore
            dentro_destino = a["destino"] in na_arvore
            if dentro_origem != dentro_destino:
                candidatas.append(a)

        if len(candidatas) == 0:
            faltando = [nomes[v] for v in vertices if v not in na_arvore]
            return {
                "ok": False,
                "erro": "Grafo desconexo: não tem como chegar em " + ", ".join(faltando) + ".",
                "passos": passos,
                "escolhidas": [a["id"] for a in escolhidas],
            }

        # escolhe a de menor peso
        menor = candidatas[0]
        for a in candidatas:
            if a["peso"] < menor["peso"]:
                menor = a

        # descobre qual ponta eh a nova
        if menor["origem"] in na_arvore:
            velho, novo = menor["origem"], menor["destino"]
        else:
            velho, novo = menor["destino"], menor["origem"]

        na_arvore.add(novo)
        escolhidas.append(menor)
        custo += menor["peso"]

        # so pra mostrar as candidatas no passo a passo
        ordenadas = sorted(candidatas, key=lambda a: a["peso"])
        lista = []
        for a in ordenadas[:6]:
            lista.append(f"{a['origem']}-{a['destino']} ({formatar(a['peso'], unidade)})")
        texto_lista = ", ".join(lista)
        if len(ordenadas) > 6:
            texto_lista += f" ... (+{len(ordenadas) - 6})"

        passos.append({
            "texto": f"Escolhe {nomes[velho]} -> {nomes[novo]} ({formatar(menor['peso'], unidade)}), "
                     f"a aresta mais barata que sai da árvore. Total até agora: {formatar(custo, unidade)}.",
            "detalhes": [f"{len(candidatas)} candidatas: {texto_lista}"],
            "na_arvore": sorted(na_arvore),
            "escolhidas": [a["id"] for a in escolhidas],
            "candidatas": [a["id"] for a in candidatas],
            "atual": menor["id"],
        })

    passos.append({
        "texto": f"Fim: os {len(vertices)} vértices estão na árvore com {len(escolhidas)} arestas (V - 1). "
                 f"Custo total: {formatar(custo, unidade)}.",
        "na_arvore": sorted(na_arvore),
        "escolhidas": [a["id"] for a in escolhidas],
        "candidatas": [],
        "atual": None,
    })

    arestas_escolhidas = []
    for a in escolhidas:
        arestas_escolhidas.append({"origem": a["origem"], "destino": a["destino"], "peso": a["peso"]})

    return {
        "ok": True,
        "inicio": inicio,
        "escolhidas": [a["id"] for a in escolhidas],
        "arestas_escolhidas": arestas_escolhidas,
        "custo": round(custo, 2),
        "custo_formatado": formatar(custo, unidade),
        "passos": passos,
    }
