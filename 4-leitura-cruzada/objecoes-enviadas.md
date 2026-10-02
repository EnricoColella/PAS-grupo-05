
# Objeções ao Grupo 01 — Saúde, Envelope B

## Objeção 1 — O banco compartilhado enfraquece a independência dos microsserviços

**Trecho atacado:** `2-arquitetura/adr/01-estrutura-geral-hibrida.md`, decisão e consequências; `2-arquitetura/diagrama/C4.pdf`, C4 Nível 2.

**Argumento:** O ADR escolhe microsserviços para dar autonomia aos 5 times e isolamento de falhas, mas o C4 mostra os principais serviços utilizando o mesmo **Banco de Dados Principal PostgreSQL**. Isso cria uma dependência compartilhada: mudanças de esquema, indisponibilidade ou sobrecarga do banco podem atingir vários serviços ao mesmo tempo, reduzindo justamente a autonomia e o isolamento usados para justificar microsserviços e o SLA de 99,9%.

**O que teríamos feito:** Manteríamos microsserviços no Envelope B, mas definiríamos propriedade dos dados por serviço e evitaríamos acesso direto a um banco compartilhado entre domínios. Cada serviço teria seu armazenamento sob sua responsabilidade e integração explícita quando dados de outro domínio fossem necessários.

---

## Objeção 2 — Agendamento e regulação aparecem acoplados apesar de terem requisitos de escala diferentes

**Trecho atacado:** `2-arquitetura/adr/01-estrutura-geral-hibrida.md`, decisão; `2-arquitetura/mapa-restricoes-decisoes.md`, decisão sobre campanhas; `2-arquitetura/diagrama/C4.pdf`, C4 Nível 2.

**Argumento:** O ADR define **serverless exclusivamente para Agendamento e Cidadão**, devido ao pico de 20 vezes, mas o C4 apresenta um único contêiner chamado **“API Agendamentos e Regulação”**. Isso acopla um fluxo sazonal e altamente escalável à regulação de leitos, que é crítica para o SLA e exige consistência forte. Além de contradizer a fronteira híbrida definida no ADR, um pico de campanha pode disputar recursos com a regulação.

**O que teríamos feito:** Separaríamos claramente o Agendamento serverless do microsserviço de Regulação, permitindo que cada um escale e seja implantado de forma independente.

---

## Objeção 3 — A fila FIFO não garante sozinha que o mesmo leito nunca seja reservado duas vezes

**Trecho atacado:** `2-arquitetura/respostas-obrigatorias.md`, seção **2. Gestão de Concorrência de Leitos com Sistema Legado**; `2-arquitetura/adr/03-acl-sistema-regulacao.md`.

**Argumento:** A solução serializa as solicitações do novo sistema por uma fila FIFO e depois utiliza “lock otimista ou transação ACID” no legado. Porém, o legado continua ativo por dois anos e o documento não garante que **toda** reserva passe obrigatoriamente por essa fila. Se o legado ainda puder receber comandos por outro caminho, existem duas rotas concorrentes e a fila do sistema novo não garante exclusividade global.

**O que teríamos feito:** Enquanto a capacidade não fosse migrada, manteríamos o legado como **única autoridade de escrita** da reserva e obrigaríamos todas as confirmações a passar por ele através da ACL. Após a migração, a autoridade passaria integralmente ao novo serviço, sem duas autoridades simultâneas.

---

## Objeção 4 — A arquitetura promete 99,9% de disponibilidade, mas não define como esse SLA será observado

**Trecho atacado:** `2-arquitetura/adr/04-padrao-implantacao-aws.md`, decisão e consequências.

**Argumento:** O ADR define EKS em três zonas e *self-healing*, mas isso descreve como a aplicação é implantada, não **como a equipe sabe que o sistema está cumprindo o SLA**. O próprio ADR reconhece a necessidade de observabilidade distribuída, porém não decide quais métricas, verificações de saúde, rastreamentos ou alertas serão usados. Isso deixa sem resposta uma pergunta central do Envelope B: “como vocês sabem que o sistema está de pé?”.

**O que teríamos feito:** Definiríamos health/readiness checks, métricas e alertas para os fluxos críticos, rastreamento distribuído e acompanhamento específico do SLA das funções cobertas pelo contrato, principalmente UPA e regulação.

---

## Objeção 5 — Event Sourcing não garante por si só auditoria imutável de acessos ao prontuário

**Trecho atacado:** `2-arquitetura/adr/02-event-sourcing-prontuario.md.md`, decisão e consequências; `2-arquitetura/respostas-obrigatorias.md`, seção **3. Auditoria do Prontuário e Adequação à LGPD**.

**Argumento:** O ADR afirma que Event Sourcing fornece auditoria “absoluta e imutável”, inclusive sobre quem **visualizou** o prontuário. Porém, Event Sourcing registra principalmente mudanças de estado do domínio; acessos de leitura precisam de uma trilha de auditoria própria. Além disso, armazenar eventos não os torna automaticamente impossíveis de alterar por um administrador, que é justamente o motivo usado para descartar a alternativa relacional.

**O que teríamos feito:** Separaríamos o histórico clínico da trilha de auditoria. Acessos e alterações seriam registrados em um log de auditoria append-only/tamper-evident com usuário, operação e horário. Event Sourcing só seria mantido para o prontuário se houvesse outra razão de domínio que justificasse seu custo.

---

## Objeção 6 — O spike não prova que os dados offline sobrevivem a uma reinicialização da UPA

**Trecho atacado:** `3-spike/exemplo.py`, função `criar_banco_local`; `2-arquitetura/adr/05-sincronizacao-assincrona-upa-offline.md`.

**Argumento:** O ADR define um banco local para permitir que a UPA continue trabalhando durante quedas de minutos a horas, mas o spike cria o SQLite com `sqlite3.connect(":memory:")`. Esse banco desaparece se o processo reiniciar. Assim, o spike prova corretamente a idempotência no reenvio, mas não prova a persistência local que faz parte da decisão e é especialmente importante porque a UPA está coberta pelo SLA do Envelope B.

**O que teríamos feito:** Usaríamos um arquivo SQLite no spike e simularíamos uma reinicialização: registrar a triagem offline, fechar e reabrir o banco, restaurar a rede e sincronizar. O teste provaria simultaneamente que a operação não é perdida e que o reenvio não cria duplicata.
