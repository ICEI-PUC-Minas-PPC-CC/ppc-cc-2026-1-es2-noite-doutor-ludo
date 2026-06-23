# Documento de Entrega - Sprint 4: Organização, Integração e Planejamento do MVP

## 1. Descrição do fluxo principal do sistema

A funcionalidade principal selecionada para o MVP é o **checkout de locação com pagamento simulado**. Essa escolha está alinhada às histórias de catálogo, carrinho, período de locação, checkout e confirmação do pedido, além de respeitar a Arquitetura Hexagonal definida pelo grupo.

O fluxo principal ocorre da seguinte forma:

1. **Entrada de dados pelo usuário**
   O cliente acessa o catálogo, visualiza os jogos disponíveis, abre os detalhes de um jogo e adiciona os itens desejados ao carrinho. Em seguida, informa as datas de início e devolução da locação, confirma ou cadastra um endereço básico de entrega e escolhe a forma de pagamento.

2. **Envio da requisição para o sistema**
   A interface web envia os dados do checkout por uma requisição HTTP REST para o adaptador de entrada `PedidoController`. Essa requisição contém os itens do carrinho, o usuário autenticado, as datas da locação, o endereço de entrega e os dados necessários para simular o pagamento.

3. **Acionamento da camada de domínio**
   O `PedidoController` repassa os dados para o `PedidoService`, que centraliza a regra de negócio do fluxo. O serviço valida o carrinho, verifica se há itens selecionados, confere a disponibilidade dos jogos, valida o período de locação, calcula o valor total e cria um `Pedido` com status inicial **Aguardando Pagamento**.

4. **Comunicação por portas**
   O `PedidoService` não acessa diretamente banco de dados, serviço de pagamento ou serviço de e-mail. Para manter o isolamento do domínio, ele utiliza as portas:
   - `IPagamento`, para processar a transação;
   - `IPedidoRepository`, para salvar e consultar pedidos;
   - `INotificador`, para enviar a confirmação ao usuário.

5. **Execução pelos adaptadores de saída**
   No MVP, a porta `IPagamento` será implementada por um adaptador simulado, como `PagamentoMockAdapter`, retornando sucesso ou falha controlada sem chamada real ao Mercado Pago. A persistência será feita pelo `PedidoRepositoryMySQL`, que converte o pedido em comandos de banco de dados. A confirmação será enviada pelo `EmailSmtpAdapter` ou, no MVP, por um adaptador simplificado de notificação.

6. **Resposta ao usuário**
   Se o pagamento simulado for aprovado, o `PedidoService` altera o status do `Pedido` para **Pago**, salva o pedido, aciona a confirmação e retorna ao `PedidoController`. O controlador devolve uma resposta REST com o número do pedido, status, valor total e mensagem de confirmação. Se houver falha de validação ou pagamento, a resposta informa o erro e o pedido não é confirmado.

## 2. Definição do escopo do MVP

O MVP será focado em validar a experiência essencial de locação: o usuário escolhe jogos, define o período, confirma os dados básicos e finaliza um pedido com pagamento simulado.

### Entra no MVP

- **Catálogo básico de jogos**
  - Visualizar a listagem de jogos disponíveis no acervo.
  - Visualizar informações principais do jogo, como nome, imagem, status e detalhes básicos.
  - Histórias relacionadas: H2.1, H2.2, H2.3, H2.4 e H4.1.

- **Carrinho de locação**
  - Adicionar jogos ao carrinho.
  - Visualizar os itens selecionados.
  - Remover itens do carrinho.
  - Visualizar subtotal.
  - Histórias relacionadas: H4.4, H5.1, H5.2, H5.3 e H5.4.

- **Período de locação**
  - Selecionar data de início.
  - Selecionar data de devolução.
  - Calcular o valor total com base na quantidade de dias.
  - Confirmar o período escolhido.
  - Histórias relacionadas: H6.1, H6.2, H6.3 e H6.4.

- **Endereço básico de entrega**
  - Confirmar um endereço salvo ou cadastrar um endereço simples para vincular ao pedido.
  - O MVP não terá janelas avançadas de entrega ou coleta.
  - História relacionada: H8.1.

- **Checkout com pagamento simulado**
  - Escolher forma de pagamento: PIX ou cartão.
  - Validar dados mínimos da forma de pagamento.
  - Processar a transação por meio de um adaptador mock.
  - Confirmar o pedido e exibir o comprovante/resumo.
  - Histórias relacionadas: H7.1, H7.2, H7.3 e H7.4.

### Não entra no MVP

- Recuperação de senha por e-mail.
- Filtros avançados por categoria, busca textual e quantidade de jogadores.
- Galeria completa de fotos, manuais em PDF e vídeos explicativos.
- Integração real com Mercado Pago.
- Janela de horário para entrega.
- Janela de horário para coleta/devolução.
- Algoritmos avançados de logística.
- Painel administrativo ou gestão completa do acervo.

## 3. Relação entre classes e arquitetura

A implementação será planejada de acordo com a Arquitetura Hexagonal, separando domínio, portas e adaptadores.

| Classe ou interface | Camada | Responsabilidade no MVP | Conexão com outros componentes |
| --- | --- | --- | --- |
| `Usuario` | Domínio | Representar o cliente que realiza a locação. | Associado ao `Pedido` e ao `Endereco`. |
| `Endereco` | Domínio | Representar o endereço básico de entrega e coleta. | Informado no checkout e vinculado ao `Pedido`. |
| `Categoria` | Domínio | Classificar jogos do catálogo. | Relacionada à entidade `Jogo`. No MVP, será usada apenas como informação simples. |
| `Jogo` | Domínio | Representar cada jogo disponível para locação. | Usado em `ItemCarrinho` e `ItemPedido`. |
| `ItemCarrinho` | Domínio | Representar um jogo escolhido antes da finalização. | Compõe o `Carrinho`. |
| `Carrinho` | Domínio | Agrupar os jogos escolhidos e calcular subtotal. | Convertido em `Pedido` durante o checkout. |
| `ItemPedido` | Domínio | Registrar o jogo efetivamente alugado e o preço histórico. | Compõe o `Pedido`. |
| `Pedido` | Domínio | Representar a locação final, com datas, itens, endereço, status e valor total. | Criado e atualizado pelo `PedidoService`. |
| `PedidoService` | Domínio/Serviço | Orquestrar o checkout, aplicar regras de negócio, calcular total, processar pagamento e confirmar reserva. | Usa `IPagamento`, `IPedidoRepository` e `INotificador`. |
| `IPagamento` | Porta de saída | Definir o contrato para processamento de pagamento. | Implementada no MVP por `PagamentoMockAdapter`; futuramente por `MercadoPagoAdapter`. |
| `IPedidoRepository` | Porta de saída | Definir o contrato de persistência de pedidos. | Implementada por `PedidoRepositoryMySQL`. |
| `INotificador` | Porta de saída | Definir o contrato para envio de confirmação ao usuário. | Implementada por `EmailSmtpAdapter` ou notificador simplificado. |
| `PedidoController` | Adaptador de entrada | Receber requisições REST do checkout e retornar respostas HTTP. | Chama o `PedidoService`. |
| `PedidoRepositoryMySQL` | Adaptador de saída | Salvar e consultar pedidos no banco MySQL. | Implementa `IPedidoRepository`. |
| `PagamentoMockAdapter` | Adaptador de saída | Simular aprovação ou recusa de pagamento no MVP. | Implementa `IPagamento`. |
| `MercadoPagoAdapter` | Adaptador de saída futuro | Integrar com a API real do Mercado Pago em versão posterior. | Também implementará `IPagamento`. |
| `EmailSmtpAdapter` | Adaptador de saída | Enviar confirmação do pedido ao cliente. | Implementa `INotificador`. |

## 4. Planejamento técnico da implementação

### 4.1 Camada de domínio

A camada de domínio concentrará as regras principais do MVP.

O `PedidoService` será responsável por:

- receber os dados vindos do `PedidoController`;
- validar se o carrinho possui itens;
- validar as datas de início e devolução;
- verificar a disponibilidade dos jogos;
- transformar `Carrinho` em `Pedido`;
- calcular o total usando os itens e o número de dias da locação;
- iniciar o pedido com status **Aguardando Pagamento**;
- chamar a porta `IPagamento`;
- alterar o status para **Pago** em caso de sucesso;
- salvar o pedido usando `IPedidoRepository`;
- acionar `INotificador` para confirmação.

Métodos planejados:

- `iniciarCheckout(carrinho, datas, endereco)`
- `processarPagamento(pedido, dadosPagamento)`
- `confirmarReserva(pedido)`

### 4.2 Portas

As portas funcionarão como contratos entre o domínio e os recursos externos.

`IPagamento`:

- `processarTransacao(valor, metodo, dados)`

`IPedidoRepository`:

- `salvar(pedido)`
- `buscarPorNumero(numeroPedido)`

`INotificador`:

- `enviarConfirmacao(email, pedido)`

### 4.3 Adaptadores

Os adaptadores farão a ligação entre a aplicação e a infraestrutura.

`PedidoController`:

- expõe o endpoint de checkout;
- recebe dados em JSON;
- chama o `PedidoService`;
- retorna resposta HTTP com sucesso ou erro.

`PedidoRepositoryMySQL`:

- grava o pedido, itens do pedido, usuário/endereço relacionado, valor total e status;
- consulta pedido pelo número.

`PagamentoMockAdapter`:

- simula o processamento do pagamento;
- retorna sucesso para dados válidos;
- pode retornar falha controlada para testes do fluxo alternativo.

`EmailSmtpAdapter` ou notificador simplificado:

- envia ou simula o envio de confirmação do pedido;
- permite validar o uso da porta `INotificador` sem acoplar o domínio à tecnologia de e-mail.

## 5. Integração entre os principais componentes

O fluxo técnico integrado do MVP será:

1. `PedidoController` recebe a requisição REST de checkout.
2. `PedidoController` chama `PedidoService.iniciarCheckout()`.
3. `PedidoService` valida `Carrinho`, `Jogo`, `Endereco` e datas.
4. `PedidoService` cria `Pedido` e `ItemPedido`.
5. `PedidoService` chama `IPagamento.processarTransacao()`.
6. `PagamentoMockAdapter` simula o pagamento e retorna o resultado.
7. Em caso de aprovação, `PedidoService` altera o status do `Pedido` para **Pago**.
8. `PedidoService` chama `IPedidoRepository.salvar()`.
9. `PedidoRepositoryMySQL` salva os dados do pedido.
10. `PedidoService` chama `INotificador.enviarConfirmacao()`.
11. `EmailSmtpAdapter` ou adaptador simplificado registra/envia a confirmação.
12. `PedidoController` retorna a resposta final para a interface.

## 6. Resultado esperado do MVP

Ao final da implementação do MVP, o sistema deverá permitir que um usuário conclua uma locação básica de jogos: selecionar jogos, definir datas, informar endereço, realizar pagamento simulado e receber a confirmação do pedido. Essa versão não implementa todos os recursos planejados, mas comprova o funcionamento do fluxo principal e demonstra que as classes, portas, adaptadores e regras de domínio estão integrados de acordo com a Arquitetura Hexagonal.
