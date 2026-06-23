# Definição da Arquitetura do Sistema

## 1. Descrição e Justificativa da Arquitetura

Para o sistema Doutor Ludo, foi escolhida a **Arquitetura Hexagonal**. O objetivo central desta abordagem é colocar o Domínio (regras de negócio) no centro da aplicação, isolando-o completamente de tecnologias externas, frameworks, banco de dados e interfaces de usuário.

### Justificativa

A escolha da Arquitetura Hexagonal visa evitar problemas de alto acoplamento no sistema. Por exemplo, a funcionalidade de "Checkout com Pagamento Online" exige integração com o Mercado Pago e persistência em banco de dados. Se o núcleo do sistema dependesse diretamente dessas ferramentas, qualquer mudança futura (como a troca do gateway de pagamento ou do banco MySQL para PostgreSQL) exigiria a reescrita da lógica de negócio. Com essa estrutura, as tecnologias e componentes externos ficam isolados, o que simplifica a manutenção e permite substituir ou atualizar esses periféricos sem a necessidade de alterar o núcleo da aplicação.

## 2. Organização das Camadas e Responsabilidades

O sistema está dividido em três camadas principais de responsabilidade:

### 2.1 Camada de Domínio

É o núcleo isolado do sistema, responsável por concentrar todas as regras de negócio da aplicação, sem possuir qualquer conhecimento sobre o mundo externo. O foco aqui é estritamente o funcionamento das regras de locação. Por exemplo, nesta camada reside a lógica para validar se um determinado jogo de tabuleiro está disponível no acervo para as datas escolhidas ou o cálculo do valor total do pedido com base nos dias selecionados para o aluguel.

### 2.2 Camada de Portas

As portas funcionam como os "contratos" do sistema. Elas servem para o domínio avisar o que ele precisa do mundo externo, mas sem se importar em como isso será feito. Por exemplo, existe um contrato que diz que o sistema precisa cobrar o cliente e outro que diz que precisamos salvar o pedido. O domínio apenas aciona esses contratos, garantindo que ele não precise conhecer a API do Mercado Pago ou os comandos do MySQL.

### 2.3 Camada de Adaptadores

Aqui é onde o código interage com as ferramentas externas de verdade. Os adaptadores são os responsáveis por conectar a nossa aplicação com o mundo externo. Por exemplo, temos adaptadores de entrada que recebem os dados preenchidos pelo usuário no site (via requisição HTTP) e os enviam para o sistema. E temos adaptadores de saída, que são as classes que realmente executam o comando SQL no banco de dados ou que fazem a conexão via internet com a API de pagamentos para aprovar a transação.

## 3. Comunicação entre os Componentes

A comunicação entre os componentes do sistema pode ser compreendida através do caminho que os dados percorrem durante o fluxo de finalização de um aluguel (Checkout):

- **Do Usuário para o Controlador (REST):** O cliente finaliza o pedido na interface do site, que envia uma requisição HTTP no padrão **REST** para o PedidoController.
- **Do Controlador para o Domínio:** O PedidoController recebe esses dados e aciona o núcleo do sistema repassando as informações para o coração do sistema, acionando o PedidoService para iniciar o atendimento.
- **Do Domínio para as Portas:** O PedidoService executa as regras de negócio, como validar as datas da locação e calcular o valor final. Quando precisa salvar informações ou processar o pagamento, o serviço chama os métodos definidos pelas interfaces IPagamento e IPedidoRepository.
- **Das Portas para os Adaptadores:** Os adaptadores de saída MercadoPagoAdapter e PedidoRepositoryMySQL implementam essas interfaces. Eles recebem o chamado do domínio e realizam as ações técnicas, como conectar-se à API do Mercado Pago e gravar os dados no banco de dados MySQL.
- **Retorno da Resposta:** Assim que as operações externas são concluídas, a resposta faz o caminho de volta até o PedidoController, que devolve uma confirmação no padrão REST para avisar o usuário, na tela do site, que a sua reserva está garantida.