// pagina do kruskal

const g = criarGrafo("grafo", DADOS, {
  pesoSoNoMouse: true,
  aoAlterarArestas: removidas => {
    limparResultado();
    mostrarMensagem(`${removidas.size} via(s) desativada(s). Execute novamente para recalcular.`, "ok");
  },
});

document.getElementById("btn-executar").onclick = executar;
document.getElementById("btn-restaurar").onclick = () => {
  g.restaurar();
  limparResultado();
  mostrarMensagem("");
};

function limparResultado() {
  g.limpar();
  desativarPlayer();
  document.getElementById("tabelas").style.display = "none";
  document.getElementById("resultado").innerHTML = '<p class="vazio">Nenhuma execução ainda.</p>';
}

async function executar() {
  limparResultado();
  const r = await chamarAPI("/api/kruskal", { removidas: [...g.removidas], vertices: g.visiveis && [...g.visiveis] });
  if (!r.passos) return mostrarMensagem(r.erro, "erro");

  if (r.ok) mostrarMensagem(`${r.aceitas.length} vias selecionadas conectam os ${(g.visiveis ? g.visiveis.size : DADOS.vertices.length)} bairros.`, "ok");
  else mostrarMensagem(r.erro + " Grupos: " + r.grupos.map(x => "{" + x.join(", ") + "}").join(" "), "erro");

  mostrarResultado(r);
  criarPlayer(r.passos, desenharPasso, p => p.decisao || "").ultimo();
}

function mostrarResultado(r) {
  const ve = id => !g.visiveis || g.visiveis.has(id);
  const totalGrafo = DADOS.arestas.filter(a => !g.removidas.has(a.id) && ve(a.origem) && ve(a.destino)).reduce((s, a) => s + a.peso, 0);
  const economia = totalGrafo - r.custo;
  document.getElementById("resultado").innerHTML = `
    <div class="custo-rotulo">Comprimento total a pavimentar</div>
    <div class="custo">${formatarPeso(r.custo, DADOS.unidade)}</div>
    <table style="margin-top:10px">
      <tr><td>Vias aceitas</td><td><span class="selo verde">${r.aceitas.length}</span></td></tr>
      <tr><td>Vias descartadas</td><td><span class="selo vermelho">${r.rejeitadas.length}</span></td></tr>
      <tr><td>Se pavimentasse todas</td><td>${formatarPeso(totalGrafo, DADOS.unidade)}</td></tr>
      <tr><td>Economia</td><td><b>${formatarPeso(economia, DADOS.unidade)}</b> (${Math.round(100 * economia / totalGrafo)}%)</td></tr>
    </table>`;

  const nome = id => g.nomes[id];
  document.getElementById("tab-aceitas").innerHTML = "<table><tr><th>#</th><th>Via</th><th>Comprimento</th></tr>" +
    r.arestas_aceitas.map((a, i) => `<tr><td>${i + 1}</td><td>${nome(a.origem)} – ${nome(a.destino)}</td><td>${formatarPeso(a.peso, DADOS.unidade)}</td></tr>`).join("") +
    "</table>";
  document.getElementById("tab-descartadas").innerHTML = "<table><tr><th>Via</th><th>Comprimento</th><th>Motivo</th></tr>" +
    r.descartadas.map(a => `<tr><td>${nome(a.origem)} – ${nome(a.destino)}</td><td>${formatarPeso(a.peso, DADOS.unidade)}</td><td class="vazio">${a.motivo}</td></tr>`).join("") +
    "</table>";
  document.getElementById("tabelas").style.display = "block";
}

function desenharPasso(p) {
  g.limpar();
  (p.aceitas || []).forEach(id => g.aresta(id, "escolhida"));
  (p.rejeitadas || []).forEach(id => g.aresta(id, "rejeitada"));
  if (p.atual) g.aresta(p.atual, p.decisao === "rejeitada" ? "rejeitada" : "atual");
  if (p.atual) p.atual.split("|").forEach(v => g.vertice(v, "atual"));
}
