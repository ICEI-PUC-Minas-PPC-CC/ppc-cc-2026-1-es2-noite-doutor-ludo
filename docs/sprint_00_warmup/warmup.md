# Warmup

## 1. Escolha de uma funcionalidade principal

A funcionalidade selecionada para esta análise é o Checkout com Pagamento Online. Esta funcionalidade é o ponto crítico do sistema, onde a reserva é efetivada através de uma transação financeira segura, exigindo alta confiabilidade e integração com serviços externos.

## 2. Descrição do fluxo completo

O fluxo descreve a jornada do usuário desde a intenção de pagamento até a confirmação da reserva:
- **Quem inicia a ação:** O Usuário (Cliente) logado.
- **O que acontece primeiro:** O usuário, na tela de checkout, seleciona o método de pagamento (Cartão ou PIX) e insere os dados necessários.
- **Quais partes do sistema são acionadas:**
    - A interface de usuário captura a ação e envia para o controlador de pedidos.
    - O núcleo do sistema valida a disponibilidade dos itens no carrinho para o período escolhido.
    - O serviço de pagamento é acionado para processar a cobrança junto ao gateway externo (Mercado Pago).
    - O banco de dados é atualizado para registrar o pedido e reduzir a disponibilidade do slot de logística.
- **Como os dados circulam:** Os dados do cartão são "tokenizados" para segurança, o valor total calculado no carrinho é enviado para o processador de pagamento e, após a aprovação, o status do pedido muda para "Pago" no banco de dados.
- **Qual é o resultado final:** O usuário visualiza a tela de sucesso e recebe um e-mail de confirmação com os detalhes da locação.

## 3. Mapeamento técnico e Reformulação Arquitetural

É importante notar que, devido à adoção da Arquitetura Hexagonal, a modelagem inicial precisou ser expandida. O sistema não utiliza apenas classes de domínio, mas também Portas (Interfaces) e Adaptadores para isolar as regras de negócio de detalhes técnicos.
As classes principais identificadas são:
- **Classes de Domínio:** PedidoService, Pedido, ItemPedido, Usuario, Endereco, Jogo, Carrinho e ItemCarrinho.
- **Portas (Interfaces de Contrato):** IPagamento, INotificador e IPedidoRepository.
- **Adaptadores (Implementações Técnicas):** PedidoController, MercadoPagoAdapter, EmailSmtpAdapter e PedidoRepositoryMySQL.

## 4. Organização arquitetural

A arquitetura escolhida é a Arquitetura Hexagonal. O objetivo central é colocar o domínio no centro do sistema, garantindo que as regras de negócio de locação de jogos não dependam de tecnologias externas.

**Estrutura de responsabilidades:**
- Núcleo (Domínio): O PedidoService coordena o fluxo, mas ele não conhece o banco de dados ou o Mercado Pago. Ele conversa apenas com interfaces.
- Portas (Interfaces): Definem o que deve ser feito (ex: pagar, salvar, enviar_email) através de contratos de comunicação.
- Adaptadores de Entrada: O PedidoController recebe a requisição via HTTP e traduz para uma chamada ao serviço de domínio.
- Adaptadores de Saída: Classes como MercadoPagoAdapter implementam a interface de pagamento, realizando a comunicação real com a API externa.

**Fluxo simplificado:** Usuário → PedidoController → PedidoService → IPagamento (Interface) → MercadoPagoAdapter → Gateway Externo.

## 5. Identificação de problemas

A análise crítica do modelo original (Cartões CRC) revelou pontos de melhoria que foram corrigidos com a nova arquitetura:
- Acoplamento Forte: Originalmente, a classe Pagamento processaria a transação diretamente. Isso gerava dependência direta de APIs externas, o que dificulta a manutenção e testes.
- Violação do Princípio de Responsabilidade Única: A classe Pedido concentrava muitas tarefas (cálculo, status, logística e agora pagamento).
- Dificuldade de Evolução: Se o grupo decidisse trocar o Mercado Pago por outro gateway ou trocar o banco de dados, teria que reescrever a lógica de negócio. A nova estrutura com interfaces resolve esse problema ao isolar a implementação.

## 6. Definição de classes (Estrutura Final)

Com base na arquitetura hexagonal e nas necessidades da funcionalidade de Checkout, as classes estão assim definidas:

**Camada de Domínio (Núcleo)** 
- Pedido: Entidade que armazena os dados da locação, status e datas.
- ItemPedido: Entidade que registra o jogo e o preço unitário histórico.
- PedidoService: Orquestrador das regras de negócio. Ele chama a interface de pagamento e de persistência.

**Camada de Portas (Interfaces/Contratos)** 
- IPagamento: Interface que define o método pagar(double valor). Permite trocar o meio de pagamento sem afetar o PedidoService.
- INotificador: Interface que define o método enviar(String mensagem). Padroniza como o sistema envia confirmações (Email, SMS).
- IPedidoRepository: Interface que define como o sistema espera que um pedido seja salvo no banco de dados.

**Camada de Adaptadores (Infraestrutura)**
- PedidoController: Adaptador de entrada que recebe as requisições REST da web.
- MercadoPagoAdapter: Implementação concreta que contém a lógica técnica para falar com a API do Mercado Pago.
- EmailSmtpAdapter: Implementação técnica para envio de e-mails via servidor SMTP.
- PedidoRepositoryMySQL: Implementação concreta que executa os comandos SQL no banco de dados