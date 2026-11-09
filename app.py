# Grafos em Acao - trabalho final de Grafos
# rodar: python app.py  e abrir http://127.0.0.1:5000

from flask import Flask, jsonify, render_template, request

from algoritmos import carregar_grafo, remover_arestas, dijkstra, prim, kruskal

app = Flask(__name__)
app.json.ensure_ascii = False


@app.route("/")
def inicio():
    return render_template("index.html", pagina="inicio")


@app.route("/dijkstra")
def pagina_dijkstra():
    return render_template("dijkstra.html", pagina="dijkstra", grafo=carregar_grafo("dijkstra"))


@app.route("/prim")
def pagina_prim():
    return render_template("prim.html", pagina="prim", grafo=carregar_grafo("prim"))


@app.route("/kruskal")
def pagina_kruskal():
    return render_template("kruskal.html", pagina="kruskal", grafo=carregar_grafo("kruskal"))


@app.route("/dados")
def pagina_dados():
    grafos = {}
    for nome in ["dijkstra", "prim", "kruskal"]:
        grafos[nome] = carregar_grafo(nome)
    return render_template("dados.html", pagina="dados", grafos=grafos)


# ---- API (o javascript chama essas rotas com fetch) ----

@app.route("/api/grafo/<nome>")
def api_grafo(nome):
    if nome not in ["dijkstra", "prim", "kruskal"]:
        return jsonify({"ok": False, "erro": "Grafo inexistente."}), 404
    return jsonify(carregar_grafo(nome))


def ler_pedido(nome):
    dados = request.get_json(silent=True) or {}
    grafo = carregar_grafo(nome)
    vertices = [v["id"] for v in grafo["vertices"]]
    nomes = {v["id"]: v["nome"] for v in grafo["vertices"]}
    arestas = remover_arestas(grafo, dados.get("removidas", []))
    return dados, grafo, vertices, nomes, arestas


@app.route("/api/dijkstra", methods=["POST"])
def api_dijkstra():
    dados, grafo, vertices, nomes, arestas = ler_pedido("dijkstra")
    try:
        r = dijkstra(vertices, arestas, dados.get("origem"), dados.get("destino"), nomes, grafo["unidade"])
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    return jsonify(r)


@app.route("/api/prim", methods=["POST"])
def api_prim():
    dados, grafo, vertices, nomes, arestas = ler_pedido("prim")
    if not dados.get("inicio"):
        return jsonify({"ok": False, "erro": "Selecione o aeroporto inicial."}), 400
    try:
        r = prim(vertices, arestas, dados["inicio"], nomes, grafo["unidade"])
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    return jsonify(r)


@app.route("/api/kruskal", methods=["POST"])
def api_kruskal():
    dados, grafo, vertices, nomes, arestas = ler_pedido("kruskal")
    if len(arestas) == 0:
        return jsonify({"ok": False, "erro": "Não tem nenhuma via ativa no grafo."}), 400
    try:
        r = kruskal(vertices, arestas, nomes, grafo["unidade"])
    except ValueError as e:
        return jsonify({"ok": False, "erro": str(e)}), 400
    return jsonify(r)


if __name__ == "__main__":
    app.run(debug=True)
