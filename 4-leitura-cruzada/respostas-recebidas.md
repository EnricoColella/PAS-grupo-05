
# Respostas às objeções recebidas

## Objeção 1 — Banco de dados centralizado e pico de campanhas

**Resposta: rebatemos.**

A objeção parte da premissa de que todos os domínios utilizam consistência forte sobre as mesmas estruturas do banco, o que não corresponde à nossa decisão. O ADR 0002 define propriedade lógica dos dados por módulo e requisitos de consistência diferentes por subdomínio; consistência forte é necessária especialmente nas operações que realmente exigem essa garantia.

Além disso, o pico de 20 vezes definido no caso está associado ao **agendamento de campanhas**, e não necessariamente a uma multiplicação equivalente de baixas de estoque e gravações clínicas concorrentes.

O uso de um banco relacional compartilhado é um trade-off consciente do Envelope A: reduzimos a complexidade operacional inicial em troca de escala conjunta, custo já reconhecido no ADR 0001 e no documento principal.

**Mudança:** não alteraremos a decisão arquitetural. O risco de capacidade continuará sendo tratado por dimensionamento e testes de carga antes das campanhas.

---

## Objeção 2 — Retenção de 20 anos sem estratégia de arquivamento

**Resposta: aceitamos parcialmente.**

A objeção é válida ao apontar que a retenção de longo prazo precisa possuir uma estratégia operacional de ciclo de vida. Entretanto, nossa decisão de utilizar um banco relacional central não afirma que todos os dados dos 20 anos deverão permanecer indefinidamente no mesmo conjunto de dados quente.

Também não há informação suficiente no caso para afirmar antecipadamente que serão produzidos determinados volumes em terabytes ou para definir arbitrariamente que dados com mais de dois anos deverão migrar para uma tecnologia específica.

**Mudança:** acrescentaremos ao documento principal que a retenção de 20 anos deve possuir política de ciclo de vida, permitindo particionamento e armazenamento em camadas conforme volume e frequência real de acesso, preservando recuperação e auditoria. Não fixaremos prazo ou tecnologia antes de existirem medições que sustentem essa decisão.

---

## Objeção 3 — Uso de função serverless para integração

**Resposta: rebatemos.**

A função gerenciada executa um trabalho **curto, independente, sem estado e disparado por uma mensagem da fila**, exatamente o tipo de carga para o qual adotamos serverless de forma localizada.

Se o sistema federal ficar indisponível, a função não permanece executando durante horas. A tarefa permanece na fila persistente e novas tentativas ocorrem posteriormente. Quando houver acúmulo, a concorrência do consumidor pode ser limitada para evitar uma retomada descontrolada.

Substituir esse mecanismo por um worker permanente dentro da Aplicação de Saúde também possui custos: o processo precisa ser executado continuamente, coordenado quando houver várias réplicas da aplicação e monitorado da mesma forma.

A superioridade financeira do worker também não pode ser determinada sem dados de volume e utilização.

**Mudança:** manteremos a fila persistente e a função gerenciada.

---

## Objeção 4 — Ausência de resolução de conflitos no funcionamento offline

**Resposta: aceitamos parcialmente.**

O spike foi construído para provar exclusivamente a decisão considerada mais arriscada no ADR 0005: uma operação processada cuja confirmação foi perdida pode ser reenviada sem produzir duplicação.

Ele não pretende demonstrar todo o problema de sincronização offline.

A objeção, entretanto, mostra que precisamos deixar mais claro quais operações podem funcionar offline. O mecanismo não deve transmitir uma cópia completa do estado de um paciente e sobrescrever silenciosamente o estado central.

**Mudança:** deixaremos explícito que o funcionamento offline é restrito às operações assistenciais autorizadas, como novos registros de triagem e atendimento. Alterações concorrentes de dados compartilhados não serão resolvidas automaticamente por estratégias como Last-Write-Wins; quando uma operação depender de um estado que mudou desde sua criação, o conflito deverá ser identificado para tratamento explícito.

O spike continuará inalterado, pois seu objetivo permanece sendo provar a idempotência do reenvio.

---

## Objeção 5 — Receita criada offline e validação pela Farmácia

**Resposta: rebatemos.**

O próprio Caso Saúde estabelece que a **dispensação só pode ocorrer com receita vinculada ao prontuário**.

Permitir que a Farmácia dispense medicamentos com base apenas em uma receita física ainda não sincronizada alteraria uma regra de negócio definida pelo enunciado. Isso não pode ser decidido apenas pela arquitetura.

Enquanto a receita produzida offline ainda não tiver sido sincronizada e vinculada ao prontuário central, a aplicação não possui evidência suficiente para autorizar a dispensação segundo a regra fornecida.

Se a Secretaria desejar futuramente um procedimento de contingência baseado em receita física, isso exigirá uma nova regra de negócio e uma decisão específica de auditoria e reconciliação.

**Mudança:** nenhuma.

---

## Objeção 6 — Consulta do estado dos leitos durante a migração do legado

**Resposta: rebatemos.**

Nossa arquitetura já prevê que, enquanto uma capacidade ainda pertence ao legado, o sistema novo realiza **consultas e confirmações através do Adaptador de Regulação Legada**.

Portanto, o sistema novo não depende de uma cópia local desatualizada para apresentar a disponibilidade das capacidades que ainda não foram migradas.

A autoridade continua sendo o legado até a transferência completa da capacidade. Uma visão replicada por CDC ou polling seria eventualmente consistente e poderia apresentar um leito como disponível mesmo após uma alteração ainda não replicada. A confirmação definitiva continuaria precisando consultar a autoridade.

Um read model poderá ser avaliado posteriormente como otimização caso medições demonstrem que a latência do legado é um problema relevante, mas ele não é necessário para garantir a correção da reserva.

**Mudança:** nenhuma.

---

## Objeção 7 — Complexidade operacional de fila, função e observabilidade

**Resposta: aceitamos parcialmente.**

Concordamos que uma pequena equipe não deve adicionar infraestrutura distribuída sem necessidade e que tarefas pendentes precisam ser facilmente auditáveis.

Porém, substituir a fila gerenciada por uma tabela e um worker interno não elimina a operação: continuariam sendo necessários agendamento, controle de concorrência, repetição, tratamento de falhas e alertas. Além disso, perderíamos o amortecimento de carga e o desacoplamento temporal proporcionados pela fila.

A objeção, contudo, evidencia um ponto que pode ser melhorado: entre salvar a notificação municipal e publicá-la na fila existe uma etapa que precisa ser durável.

**Mudança:** adicionaremos uma **outbox transacional** no Banco de Dados Central. A notificação e sua tarefa de integração serão registradas na mesma transação local; posteriormente, o Adaptador de Mensageria publicará as tarefas pendentes na fila. A fila persistente e a Função de Integração continuarão sendo utilizadas para o envio ao sistema federal.

Assim, uma falha entre a gravação municipal e a publicação na fila não provoca perda silenciosa da tarefa, sem abandonar os benefícios da mensageria gerenciada.
