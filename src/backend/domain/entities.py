from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from uuid import uuid4


class MetodoPagamento(str, Enum):
    """Métodos de pagamento aceitos pela plataforma."""

    PIX = "PIX"
    CARTAO = "CARTAO"


class StatusPedido(str, Enum):
    """Ciclo de vida possível de um pedido de aluguel."""

    CRIADO = "CRIADO"
    PAGAMENTO_APROVADO = "PAGAMENTO_APROVADO"
    PAGAMENTO_RECUSADO = "PAGAMENTO_RECUSADO"
    CANCELADO = "CANCELADO"


@dataclass(frozen=True)
class Jogo:
    """Representa um jogo de tabuleiro disponível para aluguel."""

    id: str
    nome: str
    descricao: str
    categoria: str
    min_jogadores: int
    max_jogadores: int
    preco_diaria: float
    imagem_url: str
    disponivel: bool = True


@dataclass(frozen=True)
class Endereco:
    """Representa o endereço de entrega do pedido."""

    rua: str
    numero: str
    bairro: str
    cidade: str
    estado: str
    cep: str

    def formatado(self) -> str:
        """Retorna uma representação textual única do endereço."""
        return f"{self.rua}, {self.numero} - {self.bairro}, {self.cidade}/{self.estado} - CEP: {self.cep}"


@dataclass(frozen=True)
class Usuario:
    """Representa o cliente que está alugando."""

    id: str
    nome: str
    email: str


@dataclass
class Pedido:
    """Representa o pedido de aluguel."""

    usuario: Usuario
    jogo: Jogo
    endereco: Endereco
    data_inicio: date
    data_fim: date
    metodo_pagamento: MetodoPagamento
    id: str = field(default_factory=lambda: str(uuid4()))
    status: StatusPedido = StatusPedido.CRIADO
    valor_total: float = 0.0
    transacao_id: str | None = None

    def calcular_dias_aluguel(self) -> int:
        """Calcula a quantidade de dias entre o início e o fim do aluguel."""
        dias = (self.data_fim - self.data_inicio).days
        # Garante que, no mínimo, 1 diária seja cobrada.
        return max(dias, 1)

    def aprovar_pagamento(self, transacao_id: str) -> None:
        """Aplica a transição de estado de pedido com pagamento aprovado."""
        self.status = StatusPedido.PAGAMENTO_APROVADO
        self.transacao_id = transacao_id

    def recusar_pagamento(self) -> None:
        """Aplica a transição de estado de pedido com pagamento recusado."""
        self.status = StatusPedido.PAGAMENTO_RECUSADO
