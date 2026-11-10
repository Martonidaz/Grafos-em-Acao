// pagina do dijkstra

const g = criarGrafo("grafo", DADOS, {
  aoAlterarArestas: removidas => {
    limparResultado();
    mostrarMensagem(`${removidas.size} aresta(s) desativada(s). Execute novamente para recalcular.`, "ok");
  },
});

const pesoDe = {};
const linhasDe = {};
DADOS.arestas.forEach(a => { pesoDe[a.id] = a.peso; linhasDe[a.id] = a.linhas || []; });
const idAresta = (a, b) => [a, b].sort().join("|");

let origemAtual = null, destinoAtual = null;

document.getElementById("btn-executar").onclick = executar;
document.getElementById("btn-restaurar").onclick = () => {
  g.restaurar();
  limparResultado();
  document.getElementById("origem").value = "";
  document.getElementById("destino").value = "";
  mostrarMensagem("");
};

function limparResultado() {
  g.limpar();
  desativarPlayer();
  document.getElementById("extra-passo").innerHTML = "";
  document.getElementById("resultado").innerHTML = '<p class="vazio">Nenhuma rota calculada ainda.</p>';
}

async function executar() {
  const origem = document.getElementById("origem").value;
  const destino = document.getElementById("destino").value;

  // valida aqui tambem (o python valida de novo)
  if (!origem || !destino) return mostrarMensagem("Selecione a origem e o destino.", "erro");
  if (origem === destino) return mostrarMensagem("A origem e o destino devem ser pontos diferentes.", "erro");

  limparResultado();
  origemAtual = origem; destinoAtual = destino;
  const r = await chamarAPI("/api/dijkstra", { origem, destino, removidas: [...g.removidas] });

  if (!r.ok) {
    mostrarMensagem(r.erro, "erro");
    if (r.passos) criarPlayer(r.passos, desenharPasso).ultimo();
    return;
  }
  mostrarMensagem(`Rota encontrada com ${r.caminho.length - 1} trecho(s).`, "ok");
  mostrarResultado(r);
  criarPlayer(r.passos, desenharPasso).ultimo();
}

function mostrarResultado(r) {
  const trechos = [];
  let linhaAtual = null, trocas = 0, modeladas = 0;
  for (let i = 0; i < r.caminho.length - 1; i++) {
    const a = r.caminho[i], b = r.caminho[i + 1], id = idAresta(a, b);
    const linhas = linhasDe[id];
    // troca de linha: o trecho tem linha real, mas nenhuma em comum com a linha que o passageiro já está
    if (!linhas.length) { modeladas++; linhaAtual = null; }
    else {
      if (linhaAtual && !linhas.some(l => linhaAtual.includes(l))) trocas++;
      linhaAtual = linhaAtual && linhas.some(l => linhaAtual.includes(l)) ? linhas.filter(l => linhaAtual.includes(l)) : linhas;
    }
    const rotulo = linhas.length ? `Linha ${linhas.join("/")}` : '<span class="vazio">ligação modelada</span>';
    trechos.push(`<tr><td>${i + 1}</td><td>${g.nomes[a]} → ${g.nomes[b]}</td><td>${rotulo}</td><td>${formatarPeso(pesoDe[id], DADOS.unidade)}</td></tr>`);
  }
  const resumoLinhas = `${r.caminho.length - 1 - modeladas} trecho(s) em linha real, ${modeladas} ligação(ões) modelada(s), ${trocas} troca(s) de linha`;
  document.getElementById("resultado").innerHTML = `
    <div class="custo-rotulo">Distância total</div>
    <div class="custo">${formatarPeso(r.custo, DADOS.unidade)}</div>
    <div class="custo-rotulo" style="margin-top:10px">Sequência de pontos</div>
    <div class="sequencia">${r.caminho_nomes.map(n => `<span class="ponto">${n}</span>`).join('<span class="seta">→</span>')}</div>
    <div class="tabela-wrap"><table><tr><th>#</th><th>Trecho</th><th>Linha</th><th>Distância</th></tr>${trechos.join("")}</table></div>
    <p class="dica">${resumoLinhas}</p>`;
}


function desenharPasso(p) {
  g.limpar();
  (p.arvore || []).forEach(id => g.aresta(id, "arvore"));
  (p.arestas_analisadas || []).forEach(id => g.aresta(id, "analisada"));
  (p.visitados || []).forEach(v => g.vertice(v, "visitado"));

  if (p.caminho) {
    p.caminho.forEach(id => g.aresta(id, "caminho"));
    p.caminho.forEach(id => id.split("|").forEach(v => g.vertice(v, "caminho")));
  }
  g.vertice(origemAtual, "extremo");
  g.vertice(destinoAtual, "extremo");
  if (p.atual && !p.caminho) g.vertice(p.atual, "atual");

  // tabela de distancias
  const linhas = p.tabela.map(t => `
    <tr class="${t.visitado ? "visitado" : "nao-visitado"} ${t.vertice === p.atual ? "destaque" : ""}">
      <td>${g.nomes[t.vertice]}</td>
      <td>${t.distancia === null ? "∞" : formatarPeso(t.distancia, DADOS.unidade)}</td>
      <td>${t.anterior ? g.nomes[t.anterior] : "-"}</td>
      <td>${t.visitado ? '<span class="selo verde">visitado</span>' : '<span class="selo cinza">aberto</span>'}</td>
    </tr>`).join("");
  document.getElementById("extra-passo").innerHTML = `
    <h3>Tabela de distâncias neste passo</h3>
    <div class="tabela-wrap"><table><tr><th>Ponto</th><th>Distância desde a origem</th><th>Anterior</th><th>Situação</th></tr>${linhas}</table></div>`;
}
