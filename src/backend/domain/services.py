from __future__ import annotations

from domain.entities import (
    Endereco,
    Jogo,
    MetodoPagamento,
    Pedido,
    StatusPedido,
    Usuario,
)
from ports.outputs import INotificador, IPagamento, IPedidoRepository


class PedidoNaoEncontradoError(Exception):
    """Levantada quando um pedido buscado por ID não existe no repositório."""


class PedidoService:
    """
    Serviço de domínio que concentra as regras de negócio do checkout de
    aluguel do Doutor Ludo.

    Esta classe é o "caso de uso" central do MVP: cria o Pedido, calcula o
    valor total com base nas diárias, solicita o processamento do
    pagamento através da porta IPagamento, persiste o resultado via
    IPedidoRepository e notifica o usuário via INotificador.
    """

    def __init__(
        self,
        pagamento_port: IPagamento,
        pedido_repository: IPedidoRepository,
        notificador_port: INotificador,
    ) -> None:
        """
        Injeção de dependência via construtor.

        Args:
            pagamento_port: implementação concreta da porta IPagamento
            pedido_repository: implementação concreta da porta IPedidoRepository
            notificador_port: implementação concreta da porta INotificador
        """
        self._pagamento_port = pagamento_port
        self._pedido_repository = pedido_repository
        self._notificador_port = notificador_port

    def realizar_checkout(
        self,
        usuario: Usuario,
        jogo: Jogo,
        endereco: Endereco,
        data_inicio,
        data_fim,
        metodo_pagamento: MetodoPagamento,
    ) -> Pedido:
        """
        Caso de uso principal: executa o fluxo completo de checkout.

        Passos da regra de negócio:
            1. Validar a janela de datas do aluguel.
            2. Criar a entidade Pedido com status inicial CRIADO.
            3. Calcular o valor total (diária x dias de aluguel).
            4. Acionar a porta de pagamento (IPagamento).
            5. Atualizar o status do pedido conforme o resultado do pagamento.
            6. Persistir o pedido através da porta de repositório.
            7. Notificar o usuário (sucesso ou falha) através da porta de
               notificação.

        Args:
            usuario: Usuário que está realizando o aluguel.
            jogo: Jogo de tabuleiro escolhido no catálogo.
            endereco: Endereço de entrega informado no checkout.
            data_inicio: Data de início do período de aluguel.
            data_fim: Data de término do período de aluguel.
            metodo_pagamento: PIX ou CARTAO.

        Returns:
            O Pedido já processado, com status final definido
            (PAGAMENTO_APROVADO ou PAGAMENTO_RECUSADO).

        Raises:
            ValueError: se a data de fim não for posterior à data de início,
                ou se o jogo não estiver disponível para aluguel.
        """
        if data_fim <= data_inicio:
            raise ValueError("A data de término deve ser posterior à data de início do aluguel.")

        if not jogo.disponivel:
            raise ValueError(f"O jogo '{jogo.nome}' não está disponível para aluguel no momento.")

        pedido = Pedido(
            usuario=usuario,
            jogo=jogo,
            endereco=endereco,
            data_inicio=data_inicio,
            data_fim=data_fim,
            metodo_pagamento=metodo_pagamento,
        )

        # Regra de negócio: valor total = diária do jogo x quantidade de dias.
        dias = pedido.calcular_dias_aluguel()
        pedido.valor_total = round(jogo.preco_diaria * dias, 2)

        # Aciona a porta de pagamento.
        pagamento_aprovado, transacao_id = self._pagamento_port.processar_pagamento(pedido)

        if pagamento_aprovado:
            pedido.aprovar_pagamento(transacao_id)
        else:
            pedido.recusar_pagamento()

        # Persiste o estado final do pedido através da porta de repositório.
        self._pedido_repository.salvar(pedido)

        # Notifica o usuário através da porta de notificação, de acordo com
        # o resultado do pagamento.
        if pedido.status == StatusPedido.PAGAMENTO_APROVADO:
            self._notificador_port.notificar_confirmacao(pedido)
        else:
            self._notificador_port.notificar_falha(pedido)

        return pedido

    def buscar_pedido(self, pedido_id: str) -> Pedido:
        """
        Busca um Pedido existente pelo seu ID.

        Args:
            pedido_id: identificador único do Pedido.

        Returns:
            O Pedido encontrado.

        Raises:
            PedidoNaoEncontradoError: se nenhum Pedido com esse ID existir.
        """
        pedido = self._pedido_repository.buscar_por_id(pedido_id)
        if pedido is None:
            raise PedidoNaoEncontradoError(f"Pedido com id '{pedido_id}' não encontrado.")
        return pedido

    def listar_pedidos(self) -> list[Pedido]:
        """Retorna todos os Pedidos já registrados no sistema."""
        return self._pedido_repository.listar_todos()
