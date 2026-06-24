from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from domain.entities import (
    Endereco,
    Jogo,
    MetodoPagamento,
    Pedido,
    StatusPedido,
    Usuario,
)
from domain.services import PedidoNaoEncontradoError, PedidoService

router = APIRouter()

# Catálogo fixo do MVP.
JOGO_FIXO_CATALOGO = Jogo(
    id="jogo-001",
    nome="Xadrex",
    descricao=(
        "Um dos jogos de estratégia mais antigos e reverenciados do mundo. "
        "Dois jogadores movem suas peças em um tabuleiro quadriculado, "
        "buscando aplicar o xeque-mate no rei adversário por meio de "
        "planejamento, antecipação e boas decisões táticas."
    ),
    categoria="Estratégia",
    min_jogadores=2,
    max_jogadores=2,
    preco_diaria=15.90,
    imagem_url="",
    disponivel=True,
)

# Usuário fixo simulando uma sessão autenticada (não há login neste MVP).
USUARIO_FIXO = Usuario(id="user-001", nome="Convidado Doutor Ludo", email="convidado@doutorludo.com")

class EnderecoRequest(BaseModel):
    """Schema de validação do endereço enviado pelo formulário de checkout."""

    rua: str = Field(..., min_length=1, examples=["Avenida Padre Cletus Francis Cox"])
    numero: str = Field(..., min_length=1, examples=["1661"])
    bairro: str = Field(..., min_length=1, examples=["Country Club"])
    cidade: str = Field(..., min_length=1, examples=["Poços de Caldas"])
    estado: str = Field(..., min_length=2, max_length=2, examples=["MG"])
    cep: str = Field(..., min_length=8, max_length=9, examples=["37714-620"])


class CheckoutRequest(BaseModel):
    """Schema de validação do payload completo enviado pela tela de checkout."""

    jogo_id: str = Field(..., examples=["jogo-001"])
    data_inicio: date = Field(..., examples=["2026-06-23"])
    data_fim: date = Field(..., examples=["2026-06-25"])
    endereco: EnderecoRequest
    metodo_pagamento: MetodoPagamento


class JogoResponse(BaseModel):
    """Schema de saída representando um Jogo do catálogo."""

    id: str
    nome: str
    descricao: str
    categoria: str
    min_jogadores: int
    max_jogadores: int
    preco_diaria: float
    imagem_url: str
    disponivel: bool

    @staticmethod
    def from_entity(jogo: Jogo) -> "JogoResponse":
        """Converte a entidade de domínio Jogo no DTO de resposta HTTP."""
        return JogoResponse(
            id=jogo.id,
            nome=jogo.nome,
            descricao=jogo.descricao,
            categoria=jogo.categoria,
            min_jogadores=jogo.min_jogadores,
            max_jogadores=jogo.max_jogadores,
            preco_diaria=jogo.preco_diaria,
            imagem_url=jogo.imagem_url,
            disponivel=jogo.disponivel,
        )


class PedidoResponse(BaseModel):
    """Schema de saída representando o resultado de um Pedido processado."""

    id: str
    status: StatusPedido
    jogo_nome: str
    valor_total: float
    dias_aluguel: int
    transacao_id: str | None
    metodo_pagamento: MetodoPagamento
    endereco_entrega: str
    mensagem: str

    @staticmethod
    def from_entity(pedido: Pedido) -> "PedidoResponse":
        """Converte a entidade de domínio Pedido no DTO de resposta HTTP."""
        if pedido.status == StatusPedido.PAGAMENTO_APROVADO:
            mensagem = "Pagamento aprovado! Seu jogo está reservado."
        else:
            mensagem = "Não foi possível aprovar o pagamento. Tente novamente."

        return PedidoResponse(
            id=pedido.id,
            status=pedido.status,
            jogo_nome=pedido.jogo.nome,
            valor_total=pedido.valor_total,
            dias_aluguel=pedido.calcular_dias_aluguel(),
            transacao_id=pedido.transacao_id,
            metodo_pagamento=pedido.metodo_pagamento,
            endereco_entrega=pedido.endereco.formatado(),
            mensagem=mensagem,
        )

def get_pedido_service() -> PedidoService:
    """
    Placeholder de dependência do FastAPI.

    A implementação real é injetada em main.py através de
    `app.dependency_overrides[get_pedido_service] = lambda: pedido_service`.
    """
    raise NotImplementedError("Dependência não configurada. Veja a injeção em main.py.")


# ROTAS HTTP

@router.get("/catalogo", response_model=list[JogoResponse], tags=["Catálogo"])
def listar_catalogo() -> list[JogoResponse]:
    """Retorna o catálogo de jogos disponíveis."""
    return [JogoResponse.from_entity(JOGO_FIXO_CATALOGO)]


@router.get("/catalogo/{jogo_id}", response_model=JogoResponse, tags=["Catálogo"])
def obter_jogo(jogo_id: str) -> JogoResponse:
    """Retorna os detalhes de um jogo específico do catálogo pelo seu id."""
    if jogo_id != JOGO_FIXO_CATALOGO.id:
        raise HTTPException(status_code=404, detail="Jogo não encontrado no catálogo.")
    return JogoResponse.from_entity(JOGO_FIXO_CATALOGO)


@router.post("/checkout", response_model=PedidoResponse, tags=["Checkout"])
def realizar_checkout(
    payload: CheckoutRequest,
    pedido_service: PedidoService = Depends(get_pedido_service),
) -> PedidoResponse:
    """
    Recebe os dados de checkout (datas, endereço e método de pagamento),
    traduz para os tipos nativos do domínio e delega a execução da regra
    de negócio ao PedidoService.
    """
    if payload.jogo_id != JOGO_FIXO_CATALOGO.id:
        raise HTTPException(status_code=404, detail="Jogo não encontrado no catálogo.")

    endereco = Endereco(
        rua=payload.endereco.rua,
        numero=payload.endereco.numero,
        bairro=payload.endereco.bairro,
        cidade=payload.endereco.cidade,
        estado=payload.endereco.estado,
        cep=payload.endereco.cep,
    )

    try:
        pedido = pedido_service.realizar_checkout(
            usuario=USUARIO_FIXO,
            jogo=JOGO_FIXO_CATALOGO,
            endereco=endereco,
            data_inicio=payload.data_inicio,
            data_fim=payload.data_fim,
            metodo_pagamento=payload.metodo_pagamento,
        )
    except ValueError as erro:
        # Regras de negócio violadas (ex.: datas inválidas) viram HTTP 422.
        raise HTTPException(status_code=422, detail=str(erro)) from erro

    resposta = PedidoResponse.from_entity(pedido)

    if pedido.status == StatusPedido.PAGAMENTO_RECUSADO:
        # Mesmo com pagamento recusado, devolvemos 200 com o status no
        # corpo, pois a requisição HTTP em si foi processada com sucesso.
        return resposta

    return resposta


@router.get("/pedidos/{pedido_id}", response_model=PedidoResponse, tags=["Pedidos"])
def consultar_pedido(
    pedido_id: str,
    pedido_service: PedidoService = Depends(get_pedido_service),
) -> PedidoResponse:
    """Consulta um pedido já processado pelo seu identificador."""
    try:
        pedido = pedido_service.buscar_pedido(pedido_id)
    except PedidoNaoEncontradoError as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro

    return PedidoResponse.from_entity(pedido)


@router.get("/pedidos", response_model=list[PedidoResponse], tags=["Pedidos"])
def listar_pedidos(
    pedido_service: PedidoService = Depends(get_pedido_service),
) -> list[PedidoResponse]:
    """Lista todos os Pedidos já processados (útil para depuração/demo)."""
    pedidos = pedido_service.listar_pedidos()
    return [PedidoResponse.from_entity(p) for p in pedidos]
