# Algoritmo de Dijkstra
# acha o menor caminho entre a origem e o destino
# (todos os pesos sao positivos, entao funciona)

from .grafo import formatar, id_aresta, lista_adjacencia

INF = float("inf")


def validar_entrada(vertices, origem, destino): # valida se a origem e o destino existem no grafo
    if not origem or not destino:
        raise ValueError("Selecione a origem e o destino.")
    if origem not in vertices: 
        raise ValueError(f"A origem '{origem}' não existe no grafo.") 
    if destino not in vertices:
        raise ValueError(f"O destino '{destino}' não existe no grafo.")
    if origem == destino:
        raise ValueError("A origem e o destino devem ser pontos diferentes.")


def validar_pesos(arestas): # valida se existem pesos negativos nas arestas, pois o algoritmo de Dijkstra não funciona com pesos negativos
    # com peso negativo a escolha gulosa deixa de ser definitiva e o resultado sai errado
    for a in arestas:
        if a["peso"] < 0:
            raise ValueError(
                f"Aresta {a['origem']}-{a['destino']} com peso negativo: "
                "o Dijkstra exige pesos >= 0."
            )


def montar_tabela(vertices, dist, anterior, visitados): 
    # copia da tabela de distancias pra mostrar no passo a passo
    tabela = []
    for v in vertices:
        d = None if dist[v] == INF else round(dist[v], 2)
        tabela.append(
            {"vertice": v, "distancia": d, "anterior": anterior[v], "visitado": v in visitados}
        )
    return tabela


def dijkstra(vertices, arestas, origem, destino, nomes=None, unidade=""):
    # valida a entrada e os pesos das arestas
    validar_entrada(vertices, origem, destino)
    validar_pesos(arestas)
    if nomes is None:
        nomes = {v: v for v in vertices}

    adj = lista_adjacencia(vertices, arestas) # cria a lista de adjacencia do grafo a partir das arestas

    # comeca tudo com infinito, so a origem com 0
    dist = {}
    anterior = {}
    for v in vertices:
        dist[v] = INF
        anterior[v] = None
    dist[origem] = 0
    visitados = set()

    passos = []
    passos.append(
        {
            "texto": f"Início: distância de {nomes[origem]} = 0, os outros pontos começam com ∞.",
            "atual": origem,
            "visitados": [],
            "arestas_analisadas": [],
            "arvore": [],
            "tabela": montar_tabela(vertices, dist, anterior, visitados),
        }
    )

    while len(visitados) < len(vertices):
        # pega o vertice nao visitado com a menor distancia
        atual = None
        for v in vertices:
            if v in visitados:
                continue
            if atual is None or dist[v] < dist[atual]:
                atual = v

        # se o menor ainda eh infinito, nao da pra chegar nos que sobraram
        if dist[atual] == INF:
            break

        visitados.add(atual)
        detalhes = []
        analisadas = []

        # relaxamento: ve se passando pelo atual fica mais perto
        for vizinho, peso in adj[atual]:
            if vizinho in visitados:
                continue
            analisadas.append(id_aresta(atual, vizinho))
            nova = dist[atual] + peso # calcula a nova distancia do vizinho passando pelo atual
            conta = (
                f"{nomes[vizinho]}: {formatar(dist[atual], unidade)} + {formatar(peso, unidade)}"
                f" = {formatar(nova, unidade)}"
            )

            if nova < dist[vizinho]: # se a nova distancia for menor que a antiga, atualiza
                antiga = "∞" if dist[vizinho] == INF else formatar(dist[vizinho], unidade)
                dist[vizinho] = nova
                anterior[vizinho] = atual
                detalhes.append(f"{conta} < {antiga}, atualiza (anterior = {nomes[atual]})")
            else:
                detalhes.append(f"{conta} >= {formatar(dist[vizinho], unidade)}, mantém")

        if len(detalhes) == 0:
            detalhes.append("Nenhum vizinho para atualizar.")

        arvore = []
        for v in vertices: # monta a arvore de caminhos mais curtos a partir do anterior
            if anterior[v] is not None:
                arvore.append(id_aresta(anterior[v], v))

        passos.append(
            {
                # texto do passo a passo, mostrando o vertice atual, a distancia e os detalhes das atualizacoes
                "texto": f"Visita {nomes[atual]} (menor distância ainda não visitada: "
                f"{formatar(dist[atual], unidade)}).",
                "detalhes": detalhes,
                "atual": atual,
                "visitados": sorted(visitados),
                "arestas_analisadas": analisadas,
                "arvore": arvore,
                "tabela": montar_tabela(vertices, dist, anterior, visitados),
            }
        )

        # quando visita o destino a distancia dele nao muda mais, entao pode parar
        if atual == destino:
            break

    if dist[destino] == INF:
        return {
            "ok": False,
            "erro": f"Não existe caminho entre {nomes[origem]} e {nomes[destino]} "
            "(grafo desconexo para esses pontos).",
            "passos": passos,
        }

    # monta o caminho voltando pelo anterior
    caminho = []
    v = destino
    while v is not None: 
        caminho.append(v)
        v = anterior[v]
    caminho.reverse()

    arestas_caminho = []
    for i in range(len(caminho) - 1): # monta a lista de arestas do caminho a partir dos vertices do caminho
        arestas_caminho.append(id_aresta(caminho[i], caminho[i + 1]))

    nomes_caminho = [nomes[c] for c in caminho]

    passos.append(
        {
            "texto": f"Fim: {nomes[destino]} foi visitado com distância "
            f"{formatar(dist[destino], unidade)}. Voltando pelo 'anterior': "
            + " -> ".join(nomes_caminho),
            "atual": destino,
            "visitados": sorted(visitados),
            "arestas_analisadas": [],
            "arvore": arestas_caminho,
            "caminho": arestas_caminho,
            "tabela": montar_tabela(vertices, dist, anterior, visitados),
        }
    )

    return {
        "ok": True,
        "caminho": caminho,
        "caminho_nomes": nomes_caminho,
        "arestas_caminho": arestas_caminho,
        "custo": round(dist[destino], 2),
        "custo_formatado": formatar(dist[destino], unidade),
        "passos": passos,
    }
