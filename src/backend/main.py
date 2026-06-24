from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from adapters.inbound.http_controller import get_pedido_service, router
from adapters.outbound.memory_repository import PedidoMemoryRepository
from adapters.outbound.mock_adapters import NotificadorMockAdapter, PagamentoMockAdapter
from domain.services import PedidoService

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# ============================================================================
# INSTANCIAÇÃO DOS ADAPTERS CONCRETOS
# ============================================================================
# Estes objetos implementam as portas definidas em ports/outputs.py.
# Para trocar o Mock por uma integração real (ex.: Mercado Pago de fato),
# bastaria substituir a linha abaixo por outra classe que também
# implemente IPagamento — nada no domínio precisaria mudar.
# ============================================================================
pagamento_adapter: PagamentoMockAdapter = PagamentoMockAdapter()
pedido_repository: PedidoMemoryRepository = PedidoMemoryRepository()
notificador_adapter: NotificadorMockAdapter = NotificadorMockAdapter()

# ============================================================================
# INJEÇÃO DE DEPENDÊNCIA NO SERVIÇO DE DOMÍNIO
# ============================================================================
# O PedidoService recebe as implementações concretas através das portas
# abstratas. Aqui ocorre a Inversão de Dependência.
# ============================================================================
pedido_service: PedidoService = PedidoService(
    pagamento_port=pagamento_adapter,
    pedido_repository=pedido_repository,
    notificador_port=notificador_adapter,
)


def _obter_pedido_service_configurado() -> PedidoService:
    """Função de override que devolve a instância de PedidoService já montada."""
    return pedido_service


# INICIALIZAÇÃO DO FASTAPI E REGISTRO DE ROTAS
app = FastAPI(
    title="Doutor Ludo API",
    description=(
        "MVP de uma plataforma de aluguel de jogos de tabuleiro, "
        "construído com Arquitetura Hexagonal para a disciplina de "
        "Engenharia de Software II "
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sobrescreve a dependência declarada no controller,
# injetando a instância real e já configurada do PedidoService.
app.dependency_overrides[get_pedido_service] = _obter_pedido_service_configurado

# Registra as rotas HTTP definidas no adapter de entrada.
app.include_router(router, prefix="/api")


@app.get("/", tags=["Status"])
def status_aplicacao() -> dict[str, str]:
    """Endpoint simples de verificação de saúde da aplicação."""
    return {
        "status": "online",
        "aplicacao": "Doutor Ludo API",
        "arquitetura": "Hexagonal",
        "documentacao": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
