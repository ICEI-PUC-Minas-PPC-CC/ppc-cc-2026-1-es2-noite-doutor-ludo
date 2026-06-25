# Descrição da Implementação e Relação Arquitetural - MVP Doutor Ludo

Este documento apresenta uma breve descrição do que foi implementado no MVP do sistema **Doutor Ludo** e explica como o código-fonte se relaciona com a arquitetura definida.

---

## 1. O que foi Implementado

Focando no objetivo de validar o fluxo central com escopo reduzido para o MVP, implementamos o ciclo de checkout de um aluguel utilizando o jogo **Xadrez** como item fixo no catálogo:

* **Catálogo e Detalhes:** A interface consome os dados do jogo (nome, categoria, preço da diária e imagem hospedada no próprio repositório) a partir de um endpoint do backend e exibe essas informações na tela.
* **Formulário de Checkout:** Captura os dados de endereço do usuário, o intervalo de datas desejado para a locação e o método de pagamento escolhido (PIX ou Cartão). 
* **Comunicação REST e Envio JSON:** Ao clicar em finalizar, o frontend empacota todas essas informações do formulário e as envia para o backend por meio de uma requisição HTTP REST, utilizando o formato JSON.
* **Processamento e Simulação:** O sistema calcula o valor total multiplicando os dias selecionados pelo preço da diária. Ele simula a autorização da transação financeira através de um componente simulado e registra o pedido. Para efeitos de teste no MVP, se o preenchimento dos campos estiver correto, o pagamento sempre será autorizado.
* **Evidência no Terminal:** Ao rodar o backend localmente, o terminal exibe em tempo real as mensagens de confirmação do fluxo, permitindo visualizar o exato momento em que o pagamento é autorizado e o e-mail de confirmação é enviado ao cliente.

---

## 2. Relação com a Arquitetura Hexagonal

A implementação seguiu a **Arquitetura Hexagonal** planejada, isolando as regras de negócio das tecnologias externas:

* **Camada de Domínio (`src/backend/domain/`):** Contém as entidades básicas (`Pedido`, `Jogo`, `Usuario`, `Endereco`) em `entities.py` e o serviço orquestrador `PedidoService` em `services.py`. Esta camada usa apenas tipos nativos do Python, sem misturar código de frameworks web ou de banco de dados, mantendo o "coração" do sistema isolado.
* **Camada de Portas (`src/backend/ports/`):** O arquivo `outputs.py` define os contratos de saída, como `IPagamento` (para o gateway), `IPedidoRepository` (para persistência) e `INotificador` (para comunicações). O domínio conversa apenas com essas interfaces abstratas.
* **Camada de Adaptadores (`src/backend/adapters/`):** 
   * **Inbound (Entrada):** O arquivo `http_controller.py` usa o **FastAPI** para expor as rotas REST e traduzir os dados JSON da web para o formato aceito pelo domínio.
   * **Outbound (Saída):** O arquivo `memory_repository.py` simula o banco de dados salvando as informações em memória (listas e dicionários), enquanto o `mock_adapters.py` executa a simulação do gateway de pagamento e notificações.

A ligação final é feita no arquivo **`main.py`**, que cria os adaptadores de infraestrutura e os injeta no serviço de domínio antes de iniciar a aplicação, garantindo a inversão de dependência.