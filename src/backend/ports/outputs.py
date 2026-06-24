from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities import Pedido


class IPagamento(ABC):
    """Porta de saída para processamento de pagamento."""

    @abstractmethod
    def processar_pagamento(self, pedido: Pedido) -> tuple[bool, str]:
        """
        Processa o pagamento referente a um Pedido.

        Args:
            pedido: O Pedido contendo valor total e método de pagamento.

        Returns:
            Uma tupla (sucesso, identificador_transacao):
                - sucesso: True se o pagamento foi aprovado, False caso contrário.
                - identificador_transacao: ID da transação gerado pelo gateway
                  (string vazia em caso de falha).
        """
        raise NotImplementedError


class IPedidoRepository(ABC):
    """Porta de saída para persistência de pedidos."""

    @abstractmethod
    def salvar(self, pedido: Pedido) -> Pedido:
        """Persiste (cria ou atualiza) um pedido e o retorna."""
        raise NotImplementedError

    @abstractmethod
    def buscar_por_id(self, pedido_id: str) -> Pedido | None:
        """Busca um pedido pelo seu ID. Retorna None se não existir."""
        raise NotImplementedError

    @abstractmethod
    def listar_todos(self) -> list[Pedido]:
        """Retorna todos os pedidos persistidos."""
        raise NotImplementedError


class INotificador(ABC):
    """Porta de saída para envio de notificações ao usuário."""

    @abstractmethod
    def notificar_confirmacao(self, pedido: Pedido) -> None:
        """Notifica o usuário sobre a confirmação (sucesso) do seu Pedido."""
        raise NotImplementedError

    @abstractmethod
    def notificar_falha(self, pedido: Pedido) -> None:
        """Notifica o usuário sobre a falha no processamento do seu Pedido."""
        raise NotImplementedError
