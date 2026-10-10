# ADR 0007: garantir publicação durável com outbox transacional

**Status:** aceito

**Contexto:**
O ADR 0006 define que informações municipais são persistidas antes de tarefas de integração serem encaminhadas para uma fila persistente. Entretanto, a confirmação da transação no Banco de Dados Central e a publicação na fila são duas operações que podem falhar independentemente. Uma falha após salvar a notificação e antes de publicar sua tarefa poderia deixar uma integração necessária sem registro na fila. Esta decisão complementa o ADR 0006 sem substituir o uso da fila persistente ou da Função de Integração.

**Decisão:**
Registrar a alteração municipal e sua tarefa de integração em uma **outbox transacional** na mesma transação do Banco de Dados Central. O Adaptador de Mensageria publicará posteriormente as tarefas pendentes da outbox na Fila Persistente e registrará a publicação após a confirmação da fila. O processamento continuará idempotente porque uma tarefa pode ser publicada ou entregue mais de uma vez após falhas de confirmação. **(Livro, seção 11.2.)**

**Alternativas consideradas:**

* **Persistir a informação e publicar diretamente na fila em seguida:** descartada porque a gravação no banco e a publicação são operações independentes; uma falha entre as duas pode produzir uma tarefa perdida.
* **Substituir a fila por um worker que processe somente uma tabela de pendências:** descartada porque eliminaria o amortecimento e o desacoplamento já escolhidos no ADR 0006, sem necessidade de abandonar a mensageria gerenciada.
* **Utilizar transação distribuída entre banco e fila:** descartada pelo aumento de complexidade operacional e pelo baixo alinhamento com o Envelope A, que possui equipe reduzida e sem operação dedicada.

**Consequências:**

* **Positivas:** a alteração municipal e a intenção de integração passam a ser confirmadas atomicamente; falhas entre banco e mensageria não produzem perda silenciosa da tarefa; a Fila Persistente continua desacoplando o sistema municipal da disponibilidade federal.
* **Negativas:** surge uma tabela de outbox que precisa ser consultada e limpa conforme política operacional; o publicador precisa lidar com repetição; tarefas pendentes na outbox passam a fazer parte da observabilidade da integração.
