from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from domain.entities import Pedido
from ports.outputs import INotificador, IPagamento

logger = logging.getLogger("doutor_ludo")


class PagamentoMockAdapter(IPagamento):
    """
    Implementação MOCK da porta IPagamento.

    Simula o comportamento de um Gateway de pagamento real (como o Mercado
    Pago): recebe os dados do pedido (valor e método de pagamento) e
    retorna sucesso, gerando um identificador de transação fictício.

    Para fins do MVP, o Mock sempre aprova o pagamento, desde que
    os dados mínimos estejam presentes no pedido (valor > 0 e método de
    pagamento definido).
    """

    def processar_pagamento(self, pedido: Pedido) -> tuple[bool, str]:
        """
        Simula o processamento do pagamento de um Pedido.

        Args:
            pedido: Pedido contendo `valor_total` e `metodo_pagamento`.

        Returns:
            (True, transacao_id) se os dados mínimos do pedido forem
            válidos, simulando a aprovação do gateway. (False, "") caso
            contrário, simulando uma recusa.
        """
        dados_validos = pedido.valor_total > 0 and pedido.metodo_pagamento is not None

        if not dados_validos:
            logger.warning("[PagamentoMockAdapter] Pagamento recusado: dados inválidos para o pedido %s", pedido.id)
            return False, ""

        # Gera um identificador de transação fictício (ex.: "MP-xxxxxxxx" para simular o Mercado Pago).
        transacao_id = f"MOCK-{pedido.metodo_pagamento.value}-{uuid.uuid4().hex[:10].upper()}"

        logger.info(
            "[PagamentoMockAdapter] Pagamento APROVADO | pedido=%s | valor=R$%.2f | metodo=%s | transacao=%s",
            pedido.id,
            pedido.valor_total,
            pedido.metodo_pagamento.value,
            transacao_id,
        )

        return True, transacao_id


class NotificadorMockAdapter(INotificador):
    """
    Implementação MOCK da porta INotificador.

    Simula o envio de uma notificação (e-mail, SMS, push) ao usuário,
    apenas registrando a mensagem via logging/print.
    """

    def notificar_confirmacao(self, pedido: Pedido) -> None:
        """Simula o envio de uma notificação de sucesso ao usuário."""
        timestamp = datetime.now(timezone.utc).isoformat()
        mensagem = (
            f"[{timestamp}] Olá {pedido.usuario.nome}, seu pedido de aluguel do jogo "
            f"'{pedido.jogo.nome}' foi CONFIRMADO! Valor total: R$ {pedido.valor_total:.2f}. "
            f"Transação: {pedido.transacao_id}. Entrega em: {pedido.endereco.formatado()}."
        )
        logger.info("[NotificadorMockAdapter] %s", mensagem)
        print(f"EMAIL PARA {pedido.usuario.email}: {mensagem}")

    def notificar_falha(self, pedido: Pedido) -> None:
        """Simula o envio de uma notificação de falha no pagamento ao usuário."""
        timestamp = datetime.now(timezone.utc).isoformat()
        mensagem = (
            f"[{timestamp}] Olá {pedido.usuario.nome}, infelizmente não conseguimos processar "
            f"o pagamento do seu pedido para o jogo '{pedido.jogo.nome}'. Tente novamente."
        )
        logger.info("[NotificadorMockAdapter] %s", mensagem)
        print(f"EMAIL PARA {pedido.usuario.email}: {mensagem}")
