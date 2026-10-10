# CHANGELOG — Revisão Final após Leitura Cruzada

Este documento registra as alterações realizadas na arquitetura após a leitura cruzada da Entrega 4.

As decisões originais foram preservadas quando as objeções não demonstraram violação do Caso Saúde ou do Envelope A. As alterações abaixo foram realizadas apenas nos pontos em que a revisão revelou uma lacuna ou necessidade de esclarecimento.

## 1. Ciclo de vida dos dados do prontuário

**Origem:** Objeção 2 — retenção de 20 anos sem estratégia de arquivamento.

**O que mudou:**
A documentação passou a deixar explícito que a retenção de 20 anos não significa manter todo o histórico no mesmo conjunto de dados de acesso frequente durante todo o período.

Foi acrescentada a possibilidade de aplicar uma política de ciclo de vida com particionamento ou armazenamento em camadas conforme volume e frequência real de acesso, preservando recuperação e auditoria.

**Por que mudou:**
A objeção apontou corretamente que a retenção de longo prazo possui custo operacional e precisa ser considerada arquiteturalmente.

Não foi definido um prazo fixo nem uma tecnologia específica de armazenamento histórico porque o Caso Saúde não fornece volume suficiente para sustentar essa escolha antecipadamente.

**Arquivos afetados:**

* `2-arquitetura/README.md`
* `2-arquitetura/mapa-restricoes-decisoes.md`
* `2-arquitetura/respostas-perguntas.md`

## 2. Limites da sincronização offline

**Origem:** Objeção 4 — ausência de resolução de conflitos no funcionamento offline.

**O que mudou:**
A documentação passou a deixar explícito que o mecanismo offline é destinado às operações assistenciais autorizadas, como novos registros de triagem e atendimento.

O mecanismo não deve enviar estados completos para sobrescrever silenciosamente informações compartilhadas no sistema central. Alterações que dependam de estado concorrente não serão automaticamente resolvidas por regras como *Last-Write-Wins*.

**Por que mudou:**
O ADR 0005 e o spike já provavam a idempotência do reenvio, mas não pretendiam resolver todos os possíveis conflitos de edição concorrente.

A alteração delimita melhor o escopo da decisão sem modificar o mecanismo provado pelo spike.

**Arquivos afetados:**

* `2-arquitetura/README.md`
* `2-arquitetura/mapa-restricoes-decisoes.md`
* `2-arquitetura/respostas-perguntas.md`

**Spike:**
`3-spike/exemplo.py` permanece inalterado, pois continua tendo como objetivo exclusivo provar que a perda de uma confirmação e o reenvio da mesma operação não produzem duplicação.

## 3. Outbox transacional para integrações externas

**Origem:** Objeção 7 — complexidade e confiabilidade do caminho entre persistência municipal e mensageria.

**O que mudou:**
Foi adicionada uma **outbox transacional** entre o registro municipal e a Fila Persistente.

A notificação e a tarefa de integração são registradas na mesma transação do Banco de Dados Central. Posteriormente, o Adaptador de Mensageria publica as tarefas pendentes na fila.

Foi criado o **ADR 0007 — garantir publicação durável com outbox transacional**.

**Por que mudou:**
A versão anterior possuía uma janela entre a confirmação da informação no banco e a publicação de sua tarefa na fila. Uma falha nesse intervalo poderia deixar a informação registrada municipalmente sem uma tarefa durável de integração.

A outbox elimina essa janela sem abandonar a Fila Persistente e a Função de Integração já escolhidas no ADR 0006.

**Arquivos afetados:**

* `2-arquitetura/README.md`
* `2-arquitetura/c4-conteineres.md`
* `2-arquitetura/c4-componentes.md`
* `2-arquitetura/mapa-restricoes-decisoes.md`
* `2-arquitetura/respostas-perguntas.md`
* `2-arquitetura/adr/0007-garantir-publicacao-duravel-com-outbox-transacional.md`

## 4. Objeções que não alteraram a arquitetura

### Objeção 1 — banco centralizado e pico de campanhas

A decisão foi mantida. O pico de vinte vezes definido no caso está associado ao serviço de agendamento e não demonstra, por si só, que todos os módulos produzirão a mesma multiplicação de escritas concorrentes.

O banco central permanece um trade-off consciente do Envelope A para reduzir a complexidade operacional inicial.

### Objeção 3 — uso de função serverless para integração

A decisão foi mantida.

A Função de Integração executa trabalho curto, sem estado e disparado pela fila. Quando o sistema federal está indisponível, o trabalho permanece pendente na mensageria; a função não permanece executando durante todo o período de indisponibilidade.

### Objeção 5 — receita criada offline e validação pela Farmácia

A decisão foi mantida.

O Caso Saúde determina que a dispensação exige receita vinculada ao prontuário. Permitir dispensação apenas com uma receita física ainda não sincronizada modificaria uma regra de negócio fornecida pelo enunciado.

### Objeção 6 — consulta de leitos durante a migração

A decisão foi mantida.

Enquanto uma capacidade ainda pertence ao legado, consultas e confirmações dessa capacidade passam pelo Adaptador de Regulação Legada. A confirmação continua dependente da autoridade vigente, evitando que uma réplica eventualmente consistente seja utilizada como fonte definitiva da disponibilidade do leito.

## 5. ADRs

Os ADRs `0001` a `0006` permanecem inalterados.

Nenhuma decisão aceita anteriormente foi contradita pelas mudanças da revisão e, portanto, nenhum ADR precisou receber status de substituído.

Foi criado o **ADR 0007**, que complementa o ADR 0006 adicionando a outbox transacional ao caminho de publicação das integrações.

## 6. Correção editorial

Foi corrigida no documento principal a referência ao arquivo do ADR 0006 para utilizar seu nome real:

`0006-notificar-vigilancia-por-fila-persistente.md`

Essa correção não altera nenhuma decisão arquitetural.
