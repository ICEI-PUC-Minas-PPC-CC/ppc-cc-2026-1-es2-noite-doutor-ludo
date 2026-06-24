// Ajuste a URL caso o backend FastAPI esteja rodando em outro host/porta.
const API_BASE_URL = "http://127.0.0.1:8000/api";

const estado = {
  jogo: null,
};

const elementos = {
  conteudoCatalogo: document.getElementById("conteudo-catalogo"),
  formCheckout: document.getElementById("form-checkout"),
  btnVoltar: document.getElementById("btn-voltar"),
  dataInicio: document.getElementById("data-inicio"),
  dataFim: document.getElementById("data-fim"),
  resumoPedido: document.getElementById("resumo-pedido"),
  erroCheckout: document.getElementById("erro-checkout"),
  conteudoResultado: document.getElementById("conteudo-resultado"),
};

/* ================================================================
   NAVEGAÇÃO ENTRE TELAS E TRILHO DE PROGRESSO
   ================================================================ */
function mostrarTela(idTela) {
  document.querySelectorAll(".tela").forEach((el) => el.classList.remove("visivel"));
  document.getElementById(idTela).classList.add("visivel");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function atualizarTrilho(passo) {
  document.querySelectorAll(".trilho .etapa").forEach((etapaEl) => {
    const n = parseInt(etapaEl.dataset.passo, 10);
    etapaEl.classList.remove("ativa", "concluida");
    if (n < passo) etapaEl.classList.add("concluida");
    if (n === passo) etapaEl.classList.add("ativa");
  });

  const linha1 = document.getElementById("linha-1");
  const linha2 = document.getElementById("linha-2");
  if (linha1) linha1.style.width = passo >= 2 ? "100%" : "0%";
  if (linha2) linha2.style.width = passo >= 3 ? "100%" : "0%";
}

function voltarParaCatalogo() {
  atualizarTrilho(1);
  mostrarTela("tela-catalogo");
}

/* ================================================================
   TELA 1 — CARREGAR CATÁLOGO (GET /api/catalogo)
   ================================================================ */
async function carregarCatalogo() {
  try {
    const resp = await fetch(`${API_BASE_URL}/catalogo`);
    if (!resp.ok) throw new Error("Falha ao carregar catálogo.");
    const jogos = await resp.json();
    const jogo = jogos[0]; // MVP: catálogo fixo com um único jogo.
    estado.jogo = jogo;

    elementos.conteudoCatalogo.innerHTML = `
      <img class="capa-jogo" src="${jogo.imagem_url}" alt="Capa do jogo ${jogo.nome}">
      <div>
        <span class="selo-categoria">${jogo.categoria}</span>
        <h2 class="titulo-jogo">${jogo.nome}</h2>
        <p class="descricao-jogo">${jogo.descricao}</p>
        <div class="meta-jogo">
          <div class="meta-item">Jogadores<strong>${jogo.min_jogadores}–${jogo.max_jogadores}</strong></div>
          <div class="meta-item">Disponibilidade<strong>${jogo.disponivel ? "Em estoque" : "Indisponível"}</strong></div>
        </div>
        <div class="preco-destaque">R$ ${jogo.preco_diaria.toFixed(2).replace(".", ",")} <span>/ diária</span></div>
        <div class="acoes-rodape" style="justify-content:flex-end;">
          <button class="botao botao-primario" id="btn-alugar" ${jogo.disponivel ? "" : "disabled"}>
            Alugar este jogo
          </button>
        </div>
      </div>
    `;

    const imgCapa = elementos.conteudoCatalogo.querySelector(".capa-jogo");
    imgCapa.addEventListener("error", () => {
      imgCapa.style.background = "var(--cinza-100)";
      imgCapa.removeAttribute("src");
    });

    const btnAlugar = document.getElementById("btn-alugar");
    if (btnAlugar) {
      btnAlugar.addEventListener("click", irParaCheckout);
    }
  } catch (erro) {
    elementos.conteudoCatalogo.innerHTML = `
      <p style="color:var(--erro)">
        Não foi possível carregar o catálogo. Verifique se o backend está em execução em ${API_BASE_URL}. (${erro.message})
      </p>`;
  }
}

/* ================================================================
   TELA 2 — CHECKOUT
   ================================================================ */
function irParaCheckout() {
  const hoje = new Date();
  const futuro = new Date();
  futuro.setDate(hoje.getDate() + 3);

  elementos.dataInicio.value = formatarDataInput(hoje);
  elementos.dataFim.value = formatarDataInput(futuro);

  atualizarResumo();
  atualizarTrilho(2);
  mostrarTela("tela-checkout");
}

function formatarDataInput(d) {
  return d.toISOString().split("T")[0];
}

function calcularDias() {
  const ini = new Date(elementos.dataInicio.value);
  const fim = new Date(elementos.dataFim.value);
  const diffMs = fim - ini;
  const dias = Math.round(diffMs / (1000 * 60 * 60 * 24));
  return dias > 0 ? dias : 0;
}

function atualizarResumo() {
  if (!estado.jogo) return;
  const dias = calcularDias();
  const total = dias * estado.jogo.preco_diaria;

  elementos.resumoPedido.innerHTML = `
    <div class="resumo-linha"><span>Jogo</span><span>${estado.jogo.nome}</span></div>
    <div class="resumo-linha"><span>Diária</span><span>R$ ${estado.jogo.preco_diaria.toFixed(2).replace(".", ",")}</span></div>
    <div class="resumo-linha"><span>Duração</span><span>${dias > 0 ? dias : "—"} dia(s)</span></div>
    <div class="resumo-linha total"><span>Total estimado</span><span>R$ ${total.toFixed(2).replace(".", ",")}</span></div>
  `;
}

elementos.dataInicio.addEventListener("change", atualizarResumo);
elementos.dataFim.addEventListener("change", atualizarResumo);

elementos.btnVoltar.addEventListener("click", voltarParaCatalogo);

// Destacar visualmente a "carta" de método de pagamento selecionada.
document.querySelectorAll('input[name="metodo_pagamento"]').forEach((radio) => {
  radio.addEventListener("change", () => {
    document.querySelectorAll(".metodo-carta").forEach((c) => c.classList.remove("selecionado"));
    radio.closest(".metodo-carta").classList.add("selecionado");
  });
});

function mostrarErroCheckout(mensagem) {
  elementos.erroCheckout.textContent = mensagem;
  elementos.erroCheckout.classList.add("visivel");
}

function ocultarErroCheckout() {
  elementos.erroCheckout.classList.remove("visivel");
}

/* ================================================================
   SUBMIT DO CHECKOUT — POST /api/checkout
   ================================================================ */
elementos.formCheckout.addEventListener("submit", async function (evento) {
  evento.preventDefault();
  ocultarErroCheckout();

  const payload = {
    jogo_id: estado.jogo.id,
    data_inicio: elementos.dataInicio.value,
    data_fim: elementos.dataFim.value,
    endereco: {
      rua: document.getElementById("rua").value,
      numero: document.getElementById("numero").value,
      bairro: document.getElementById("bairro").value,
      cidade: document.getElementById("cidade").value,
      estado: document.getElementById("estado").value.toUpperCase(),
      cep: document.getElementById("cep").value,
    },
    metodo_pagamento: document.querySelector('input[name="metodo_pagamento"]:checked').value,
  };

  mostrarTela("tela-processando");

  try {
    const resp = await fetch(`${API_BASE_URL}/checkout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const dados = await resp.json();

    if (!resp.ok) {
      // Erro de validação de regra de negócio (ex.: datas inválidas) -> volta pro form.
      mostrarTela("tela-checkout");
      mostrarErroCheckout(dados.detail || "Não foi possível concluir o checkout.");
      return;
    }

    exibirResultado(dados);
  } catch (erro) {
    mostrarTela("tela-checkout");
    mostrarErroCheckout(`Erro de comunicação com o servidor: ${erro.message}`);
  }
});

/* ================================================================
   TELA 4 — RESULTADO DO PAGAMENTO
   ================================================================ */
const ICONE_SUCESSO = `
  <svg viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <polyline points="20 6 9 17 4 12"></polyline>
  </svg>`;

const ICONE_FALHA = `
  <svg viewBox="0 0 24 24" fill="none" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>`;

function exibirResultado(pedido) {
  atualizarTrilho(3);
  const aprovado = pedido.status === "PAGAMENTO_APROVADO";

  elementos.conteudoResultado.innerHTML = `
    <div class="selo-resultado ${aprovado ? "sucesso" : "falha"}">${aprovado ? ICONE_SUCESSO : ICONE_FALHA}</div>
    <h2>${aprovado ? "Pedido confirmado" : "Pagamento não aprovado"}</h2>
    <p style="color:var(--grafite-700)">${pedido.mensagem}</p>

    <div class="ticket">
      <div class="resumo-linha"><span>Nº do pedido</span><strong>${pedido.id.slice(0, 8).toUpperCase()}</strong></div>
      <div class="resumo-linha"><span>Jogo</span><strong>${pedido.jogo_nome}</strong></div>
      <div class="resumo-linha"><span>Duração</span><strong>${pedido.dias_aluguel} dia(s)</strong></div>
      <div class="resumo-linha"><span>Método</span><strong>${pedido.metodo_pagamento}</strong></div>
      ${pedido.transacao_id ? `<div class="resumo-linha"><span>Transação</span><strong>${pedido.transacao_id}</strong></div>` : ""}
      <div class="resumo-linha"><span>Entrega em</span><strong style="font-weight:600; font-family:inherit;">${pedido.endereco_entrega}</strong></div>
      <div class="resumo-linha total"><span>Total pago</span><strong>R$ ${pedido.valor_total.toFixed(2).replace(".", ",")}</strong></div>
    </div>

    <div class="acoes-rodape" style="justify-content:center;">
      <button class="botao ${aprovado ? "botao-destaque" : "botao-primario"}" id="btn-acao-final">
        ${aprovado ? "Alugar outro jogo" : "Tentar novamente"}
      </button>
    </div>
  `;

  document.getElementById("btn-acao-final").addEventListener("click", reiniciarFluxo);

  mostrarTela("tela-resultado");
}

function reiniciarFluxo() {
  atualizarTrilho(1);
  mostrarTela("tela-catalogo");
}

/* ================================================================
   INICIALIZAÇÃO
   ================================================================ */
carregarCatalogo();
