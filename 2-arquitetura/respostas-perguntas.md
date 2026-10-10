# Respostas às Perguntas Obrigatórias do Caso Saúde

Este documento responde às cinco perguntas obrigatórias do Caso Saúde e relaciona cada resposta às decisões arquiteturais e aos diagramas C4 correspondentes.

## 1. Como a UPA continua triando e atendendo com a internet fora do ar, e o que acontece quando ela volta?

A **Aplicação da Unidade** continua permitindo o registro das operações autorizadas a funcionar offline utilizando armazenamento local persistente. Cada operação recebe um identificador único e permanece pendente até ser confirmada pelo sistema central.

Quando a conexão retorna, as operações pendentes são sincronizadas com a **Aplicação de Saúde**. Caso uma operação já tenha sido processada, mas a confirmação tenha se perdido, o mesmo identificador é reenviado e o servidor reconhece a repetição, evitando aplicar o efeito duas vezes.

O mecanismo offline é utilizado para novos registros assistenciais autorizados, como triagem e atendimento. Ele não envia uma cópia completa do estado de um paciente para sobrescrever silenciosamente o estado central.

Alterações que dependam de um estado compartilhado que possa ter sido modificado durante a indisponibilidade não são resolvidas automaticamente por uma política de *Last-Write-Wins*. Elas exigem reconexão ou tratamento explícito antes de alterar definitivamente o estado central.

O armazenamento local é temporário e não se torna uma segunda fonte definitiva dos dados da rede. Operações que exigem coordenação global, como a confirmação de uma reserva de leito, não podem ser concluídas offline.

**ADRs relacionados:**

* ADR 0002 — definir propriedade e consistência dos dados por módulo;
* ADR 0005 — sincronizar atendimentos offline de forma idempotente.

**Diagramas relacionados:**

* C4 de Contêineres: Aplicação da Unidade, Armazenamento Local e Aplicação de Saúde;
* C4 de Componentes: Triagem e Atendimento e Prontuário Eletrônico.

---

## 2. Como duas unidades disputando o mesmo leito nunca conseguem reservá-lo ao mesmo tempo, com o sistema legado ainda no circuito?

A reserva definitiva de um leito é tratada como operação de **consistência forte** e possui sempre **uma única autoridade de escrita**.

Enquanto a capacidade de reserva ainda pertence ao sistema legado, toda confirmação feita pelo novo sistema passa pelo módulo de Regulação e pelo Adaptador de Regulação Legada. Nesse estágio, somente o legado pode confirmar ou recusar definitivamente a reserva.

O sistema novo não mantém uma segunda confirmação concorrente para o mesmo leito.

Quando essa capacidade for migrada, a autoridade de escrita passa integralmente para o módulo de Regulação da Aplicação de Saúde e o legado deixa de confirmar novas reservas dessa capacidade.

Assim, novo sistema e legado nunca atuam simultaneamente como autoridades sobre o mesmo estado de reserva.

**ADRs relacionados:**

* ADR 0002 — definir propriedade e consistência dos dados por módulo;
* ADR 0003 — integrar legado e terceiros por adaptadores.

**Diagramas relacionados:**

* C4 de Contexto: Sistema Municipal Integrado de Saúde e Sistema Legado de Regulação;
* C4 de Componentes: Regulação, Adaptador de Regulação Legada e Sistema Legado.

---

## 3. Como o prontuário garante que se saiba quem acessou cada registro, e como convive a guarda de 20 anos com os direitos do paciente sob a LGPD?

O módulo de **Prontuário Eletrônico** é o proprietário dos registros clínicos e das informações de auditoria associadas a eles. Alterações e acessos relevantes ao prontuário devem ser registrados com identificação do responsável, permitindo rastrear quem consultou ou modificou as informações.

A arquitetura trata a retenção de 20 anos como uma restrição específica do prontuário, conforme a premissa definida na atividade.

Essa retenção não exige que todos os registros permaneçam durante vinte anos no mesmo conjunto de dados de acesso frequente. O módulo deve permitir uma política de ciclo de vida na qual dados históricos possam ser particionados ou movidos para camadas de armazenamento adequadas conforme volume e frequência de acesso, sem perder a capacidade de recuperação e auditoria.

A primeira versão não define antecipadamente um prazo de migração nem uma tecnologia específica para armazenamento histórico, pois essas escolhas devem ser baseadas no volume real observado.

Os direitos do paciente sobre seus dados precisam ser tratados sem apagar indiscriminadamente informações submetidas à retenção definida no caso. A atividade não especifica o procedimento jurídico detalhado para cada solicitação prevista na LGPD; por isso, a arquitetura garante propriedade, auditoria e capacidade de aplicar políticas de retenção, deixando a regra jurídica específica como política da organização responsável.

**ADR relacionado:**

* ADR 0002 — definir propriedade e consistência dos dados por módulo.

**Diagramas relacionados:**

* C4 de Contêineres: Aplicação de Saúde e Banco de Dados Central;
* C4 de Componentes: Prontuário Eletrônico.

---

## 4. Como a notificação compulsória chega à vigilância em até 24 horas mesmo se o sistema federal estiver indisponível?

A notificação é registrada primeiro no módulo municipal de **Vigilância Epidemiológica**, portanto sua disponibilidade para a Vigilância municipal não depende da disponibilidade do sistema federal.

A notificação e a tarefa necessária para sua integração externa são gravadas na **mesma transação local** do Banco de Dados Central. A tarefa fica registrada em uma **outbox transacional**.

O **Adaptador de Mensageria** consulta as tarefas pendentes da outbox e as publica na **Fila Persistente**. Dessa forma, se a aplicação falhar depois de salvar a notificação, mas antes da publicação, a tarefa continua registrada e pode ser enviada posteriormente.

A **Função de Integração** consome a mensagem da fila e tenta transmiti-la ao sistema federal. Caso o destino esteja indisponível, a mensagem permanece pendente para nova tentativa, sem bloquear a unidade nem apagar a notificação municipal.

Como uma publicação ou entrega pode ser repetida após uma falha de confirmação, o processamento externo precisa ser idempotente. O atraso da fila e as tarefas pendentes da outbox também precisam ser monitorados para evitar que uma notificação permaneça sem tratamento.

Assim, existem duas proteções diferentes: a **outbox** impede a perda da tarefa entre o banco e a fila, enquanto a **Fila Persistente** desacopla a operação municipal da disponibilidade do sistema federal.

**ADRs relacionados:**

* ADR 0004 — operar com uma unidade principal e serviços gerenciados;
* ADR 0006 — usar fila persistente para integrações assíncronas;
* ADR 0007 — garantir publicação durável com outbox transacional.

**Diagramas relacionados:**

* C4 de Contêineres: Aplicação de Saúde, Banco de Dados Central, Fila Persistente, Função de Integração e Sistemas Federais;
* C4 de Componentes: Vigilância Epidemiológica e Adaptador de Mensageria.

---

## 5. Como o sistema legado de regulação é substituído aos poucos sem interromper o serviço?

A integração com o sistema legado fica isolada pelo **Adaptador de Regulação Legada**, que funciona como camada anticorrupção entre o modelo novo e o contrato antigo.

A substituição segue a estratégia de **estrangulamento**, migrando uma capacidade de negócio por vez.

Enquanto uma capacidade ainda pertence ao legado, suas operações continuam sendo encaminhadas para ele. Depois que a nova implementação é validada e assume a capacidade, o sistema novo passa a ser sua autoridade e o legado deixa de atender novas operações daquela parte.

A migração não utiliza duas implementações como autoridades simultâneas sobre a mesma capacidade. Isso permite que o legado continue em funcionamento enquanto o novo sistema cresce ao redor dele, sem exigir uma interrupção geral para uma troca completa.

**ADRs relacionados:**

* ADR 0001 — adotar monolito modular com fronteiras hexagonais;
* ADR 0003 — integrar legado e terceiros por adaptadores.

**Diagramas relacionados:**

* C4 de Contexto: Sistema Municipal Integrado de Saúde e Sistema Legado de Regulação;
* C4 de Componentes: Regulação e Adaptador de Regulação Legada.

---

# Resumo de rastreabilidade

| Pergunta                                             | ADRs principais              | Diagramas principais      |
| ---------------------------------------------------- | ---------------------------- | ------------------------- |
| **1 — Operação offline**                             | ADR 0002, ADR 0005           | Contêineres e Componentes |
| **2 — Reserva exclusiva de leito**                   | ADR 0002, ADR 0003           | Contexto e Componentes    |
| **3 — Auditoria e retenção do prontuário**           | ADR 0002                     | Contêineres e Componentes |
| **4 — Notificação com sistema federal indisponível** | ADR 0004, ADR 0006, ADR 0007 | Contêineres e Componentes |
| **5 — Substituição gradual do legado**               | ADR 0001, ADR 0003           | Contexto e Componentes    |
