// funcoes usadas nas 3 paginas: desenhar o grafo (vis-network), pintar, passo a passo

const CORES = {
  vertice: "#4f8cff",
  verticeBorda: "#9cc0ff",
  roxo: "#9b6bff",
  verde: "#34d399",
  vermelho: "#f87171",
  amarelo: "#fbbf24",
  aresta: "#4a557e",
  texto: "#e7eaf6",
};

function formatarPeso(valor, unidade) {
  if (unidade === "m") return Math.round(valor).toLocaleString("pt-BR") + " m";
  return Number(valor).toLocaleString("pt-BR", { maximumFractionDigits: 2 }) + " " + unidade;
}

let ESCALA = 1; // no grafo da latam precisa aumentar as fontes

function criarGrafo(idContainer, dados, opcoes = {}) {
  ESCALA = opcoes.escala || 1;
  const nomes = {};
  dados.vertices.forEach(v => (nomes[v.id] = v.nome));

  const nodes = new vis.DataSet(dados.vertices.map(v => ({
    id: v.id,
    label: opcoes.rotuloCurto ? v.id : quebrarTexto(v.nome),
    title: v.nome,
    x: v.x, y: v.y,
  })));

  const edges = new vis.DataSet(dados.arestas.map(a => ({
    id: a.id,
    from: a.origem,
    to: a.destino,
    label: formatarPeso(a.peso, dados.unidade),
    title: `${nomes[a.origem]} - ${nomes[a.destino]}: ${formatarPeso(a.peso, dados.unidade)}`,
  })));

  const rede = new vis.Network(document.getElementById(idContainer), { nodes, edges }, {
    physics: false, // usa as posicoes x,y do json
    interaction: { hover: true, zoomView: true, dragView: true, dragNodes: true, tooltipDelay: 120 },
    nodes: {
      shape: "dot", size: 16 * ESCALA, borderWidth: 2 * ESCALA,
      font: { color: CORES.texto, size: 14 * ESCALA, face: "Inter, Segoe UI, sans-serif", strokeWidth: 4, strokeColor: "#0b1124" },
    },
    edges: {
      smooth: false,
      font: { color: "#cbd3f0", size: 12 * ESCALA, strokeWidth: 4, strokeColor: "#0b1124", align: "middle" },
    },
  });

  const removidas = new Set();

  const g = {
    rede, nodes, edges, nomes, dados, removidas,

    limpar() {
      nodes.update(dados.vertices.map(v => estiloVertice(v.id, "normal")));
      edges.update(dados.arestas.map(a => estiloAresta(a.id, removidas.has(a.id) ? "removida" : "normal")));
    },

    restaurar() {
      removidas.clear();
      nodes.update(dados.vertices.map(v => ({ id: v.id, x: v.x, y: v.y })));
      g.limpar();
      rede.fit({ animation: { duration: 400 } });
    },

    vertice(id, estilo) { nodes.update(estiloVertice(id, estilo)); },
    aresta(id, estilo) { if (!removidas.has(id)) edges.update(estiloAresta(id, estilo)); },
  };

  // clicar numa aresta desativa ela (tipo uma rua interditada)
  rede.on("click", params => {
    if (params.nodes.length || !params.edges.length || !opcoes.aoAlterarArestas) return;
    const id = params.edges[0];
    if (removidas.has(id)) removidas.delete(id); else removidas.add(id);
    g.limpar();
    opcoes.aoAlterarArestas(removidas);
  });

  g.limpar();
  setTimeout(() => rede.fit(), 50);
  return g;
}

function quebrarTexto(texto) {
  // nome grande quebra em 2 linhas
  if (texto.length <= 18) return texto;
  const meio = texto.lastIndexOf(" ", Math.ceil(texto.length / 2) + 4);
  return meio > 0 ? texto.slice(0, meio) + "\n" + texto.slice(meio + 1) : texto;
}

function estiloVertice(id, estilo) {
  const mapa = {
    normal:   { bg: CORES.vertice, borda: CORES.verticeBorda, size: 16 },
    visitado: { bg: CORES.roxo,    borda: "#d3c1ff", size: 17 },
    atual:    { bg: CORES.amarelo, borda: "#fff3c4", size: 21 },
    caminho:  { bg: CORES.verde,   borda: "#bbf7d0", size: 19 },
    extremo:  { bg: CORES.verde,   borda: "#ffffff", size: 23 },
    arvore:   { bg: CORES.verde,   borda: "#bbf7d0", size: 18 },
    apagado:  { bg: "#2a3358",     borda: "#3b4673", size: 14 },
  };
  const e = mapa[estilo] || mapa.normal;
  return { id, size: e.size * ESCALA, color: { background: e.bg, border: e.borda, highlight: { background: e.bg, border: "#fff" }, hover: { background: e.bg, border: "#fff" } } };
}

function estiloAresta(id, estilo) {
  const mapa = {
    normal:     { cor: CORES.aresta,   largura: 2,   tracejado: false },
    analisada:  { cor: CORES.amarelo,  largura: 3.5, tracejado: false },
    candidata:  { cor: CORES.amarelo,  largura: 2,   tracejado: [6, 6] },
    arvore:     { cor: CORES.roxo,     largura: 3.5, tracejado: false },
    caminho:    { cor: CORES.verde,    largura: 6,   tracejado: false },
    escolhida:  { cor: CORES.verde,    largura: 5,   tracejado: false },
    atual:      { cor: CORES.amarelo,  largura: 6,   tracejado: false },
    rejeitada:  { cor: CORES.vermelho, largura: 2.5, tracejado: [8, 6] },
    removida:   { cor: "#2b3460",      largura: 1.5, tracejado: [3, 6] },
  };
  const e = mapa[estilo] || mapa.normal;
  return { id, width: e.largura * ESCALA, dashes: e.tracejado, color: { color: e.cor, highlight: e.cor, hover: e.cor } };
}

// controles do passo a passo (os passos vem do python)
function criarPlayer(passos, desenhar, classeDoPasso) {
  let i = 0, timer = null;
  const el = id => document.getElementById(id);
  const lista = el("lista-passos");

  lista.innerHTML = "";
  passos.forEach((p, k) => {
    const li = document.createElement("li");
    li.className = classeDoPasso ? classeDoPasso(p) : "";
    li.innerHTML = `<b>${k === 0 ? "Início" : k}</b>${escapar(p.texto)}`;
    li.onclick = () => { parar(); ir(k); };
    lista.appendChild(li);
  });

  function ir(k) {
    i = Math.max(0, Math.min(passos.length - 1, k));
    const p = passos[i];
    el("passo-texto").innerHTML = `<p>${escapar(p.texto)}</p>` +
      (p.detalhes && p.detalhes.length ? "<ul>" + p.detalhes.map(d => `<li>${escapar(d)}</li>`).join("") + "</ul>" : "");
    el("contador").textContent = `Passo ${i + 1} de ${passos.length}`;
    [...lista.children].forEach((li, k2) => li.classList.toggle("ativo", k2 === i));
    lista.children[i].scrollIntoView({ block: "nearest" });
    el("btn-anterior").disabled = i === 0;
    el("btn-proximo").disabled = i === passos.length - 1;
    desenhar(p, i);
  }
  function parar() { clearInterval(timer); timer = null; el("btn-play").textContent = "Reproduzir"; }
  function play() {
    if (timer) return parar();
    if (i === passos.length - 1) ir(0);
    el("btn-play").textContent = "Pausar";
    timer = setInterval(() => { if (i >= passos.length - 1) parar(); else ir(i + 1); }, 1300);
  }

  el("btn-anterior").onclick = () => { parar(); ir(i - 1); };
  el("btn-proximo").onclick = () => { parar(); ir(i + 1); };
  el("btn-play").onclick = play;
  el("btn-final").onclick = () => { parar(); ir(passos.length - 1); };
  ["btn-anterior", "btn-proximo", "btn-play", "btn-final"].forEach(b => (el(b).disabled = false));

  return { ir, parar, ultimo: () => ir(passos.length - 1) };
}

function desativarPlayer() {
  ["btn-anterior", "btn-proximo", "btn-play", "btn-final"].forEach(b => (document.getElementById(b).disabled = true));
  document.getElementById("btn-play").textContent = "Reproduzir";
  document.getElementById("lista-passos").innerHTML = "";
  document.getElementById("contador").textContent = "";
  document.getElementById("passo-texto").innerHTML = '<p class="vazio">Execute o algoritmo para ver as etapas.</p>';
}

async function chamarAPI(url, corpo) {
  const resp = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
  return resp.json();
}

function mostrarMensagem(texto, tipo) {
  const m = document.getElementById("mensagem");
  m.className = "mensagem " + (tipo || "");
  m.textContent = texto || "";
}

function escapar(t) {
  return String(t).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}
