from __future__ import annotations

from domain.entities import Pedido
from ports.outputs import IPedidoRepository


class PedidoMemoryRepository(IPedidoRepository):
    """
    Implementação em memória da porta IPedidoRepository.

    Utiliza um dicionário Python como "tabela" de pedidos (não persiste de verdade).
    """

    def __init__(self) -> None:
        self._pedidos: dict[str, Pedido] = {}

    def salvar(self, pedido: Pedido) -> Pedido:
        """Insere ou atualiza o pedido no dicionário em memória, usando seu id como chave."""
        self._pedidos[pedido.id] = pedido
        return pedido

    def buscar_por_id(self, pedido_id: str) -> Pedido | None:
        """Retorna o pedido correspondente ao id, ou None se não existir."""
        return self._pedidos.get(pedido_id)

    def listar_todos(self) -> list[Pedido]:
        """Retorna uma lista com todos os pedidos armazenados."""
        return list(self._pedidos.values())
