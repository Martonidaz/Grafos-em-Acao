// pagina do prim

const g = criarGrafo("grafo", DADOS, {
  rotuloCurto: true, // mostra so a sigla (GRU, BSB...)
  escala: 2.2,
  aoAlterarArestas: removidas => {
    limparResultado();
    mostrarMensagem(`${removidas.size} aresta(s) desativada(s). Execute novamente para recalcular.`, "ok");
  },
});

document.getElementById("inicio").value = "GRU";
document.getElementById("btn-executar").onclick = executar;
document.getElementById("btn-restaurar").onclick = () => {
  g.restaurar();
  limparResultado();
  mostrarMensagem("");
};

function limparResultado() {
  g.limpar();
  desativarPlayer();
  document.getElementById("resultado").innerHTML = '<p class="vazio">Nenhuma árvore calculada ainda.</p>';
}

async function executar() {
  const inicio = document.getElementById("inicio").value;
  if (!inicio) return mostrarMensagem("Selecione o aeroporto inicial.", "erro");

  limparResultado();
  const r = await chamarAPI("/api/prim", { inicio, removidas: [...g.removidas] });

  if (!r.ok) {
    mostrarMensagem(r.erro, "erro");
    if (r.passos) criarPlayer(r.passos, desenharPasso).ultimo();
    return;
  }
  mostrarMensagem(`Árvore geradora mínima com ${r.escolhidas.length} conexões ligando ${DADOS.vertices.length} aeroportos.`, "ok");
  mostrarResultado(r);
  criarPlayer(r.passos, desenharPasso).ultimo();
}

function mostrarResultado(r) {
  // passo i+1 = aresta i escolhida
  const linhas = r.arestas_escolhidas.map((a, i) => {
    const passo = r.passos[i + 1];
    return `<tr><td>${i + 1}</td><td style="white-space:nowrap"><b>${a.origem}–${a.destino}</b></td><td>${formatarPeso(a.peso, DADOS.unidade)}</td>
      <td class="vazio">menor de ${passo.candidatas.length}</td></tr>`;
  }).join("");
  document.getElementById("resultado").innerHTML = `
    <div class="custo-rotulo">Custo total da árvore (soma das distâncias)</div>
    <div class="custo">${formatarPeso(r.custo, DADOS.unidade)}</div>
    <div class="custo-rotulo" style="margin-top:6px">Início em ${g.nomes[r.inicio]}</div>
    <div class="tabela-wrap"><table><tr><th>#</th><th>Conexão</th><th>Distância</th><th>Candidatas</th></tr>${linhas}</table></div>`;
}

function desenharPasso(p) {
  g.limpar();
  (p.candidatas || []).forEach(id => g.aresta(id, "candidata"));
  (p.escolhidas || []).forEach(id => g.aresta(id, "escolhida"));
  if (p.atual) g.aresta(p.atual, "atual");
  (p.na_arvore || []).forEach(v => g.vertice(v, "arvore"));
}
