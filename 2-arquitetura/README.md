
# Documento de Arquitetura — Sistema Municipal Integrado de Saúde

## 1. Objetivo

Este documento apresenta a arquitetura proposta para o **Sistema Municipal Integrado de Saúde**, responsável por integrar as capacidades da rede municipal envolvendo UBS, UPAs, hospital de referência, regulação de leitos, farmácia municipal, vigilância epidemiológica e serviços destinados ao cidadão.

A arquitetura foi definida para o **Caso Saúde — Envelope A**, considerando tanto os requisitos do caso quanto as restrições da organização responsável pela primeira versão.

As decisões arquiteturais detalhadas estão registradas nos ADRs da pasta `adr/`.

---

## 2. Contexto do problema

Atualmente, as unidades da rede municipal utilizam sistemas heterogêneos e, em alguns casos, processos baseados em papel. O prontuário do paciente não circula de forma integrada entre as unidades.

A nova solução deve integrar:

- 70 UBS;
- 5 UPAs;
- 1 hospital de referência;
- central de regulação;
- farmácia municipal;
- vigilância epidemiológica;
- serviços destinados ao cidadão;
- sistemas federais de saúde.

Existe ainda um **sistema legado de regulação** que continuará ativo durante pelo menos dois anos e deverá ser substituído gradualmente.

A rede realiza aproximadamente **12 mil atendimentos por dia**, e diferentes partes do sistema possuem necessidades distintas de disponibilidade, consistência, volume e conectividade.

---

## 3. Envelope organizacional

O projeto está inserido no **Envelope A**.

A primeira versão será construída por uma equipe de **seis desenvolvedores**, sem equipe dedicada de operação. Existe caixa para seis meses e a infraestrutura deverá utilizar nuvem pública paga por uso.

Além disso, a Secretaria Municipal de Saúde pretende disponibilizar o prontuário integrado em **três UBS dentro de quatro meses**.

Essas restrições tornam especialmente importantes:

- simplicidade operacional;
- velocidade inicial de desenvolvimento;
- custo;
- modificabilidade;
- possibilidade de evolução posterior.

A arquitetura não deve assumir antecipadamente a complexidade operacional de uma organização com vários times independentes.

Conforme o livro, decisões arquiteturais devem ser analisadas pelos atributos de qualidade priorizados e pelos respectivos trade-offs, e não como soluções universalmente melhores. **(Livro, seção 2.4.)**

---

## 4. Requisitos que mais pressionam a arquitetura

### 4.1 Continuidade durante falhas de conexão

A conectividade das UBS é instável, com interrupções diárias que podem durar de minutos a horas.

Triagem e atendimento precisam continuar sendo registrados durante essas interrupções e posteriormente sincronizados sem perda ou duplicação.

Esse requisito pressiona principalmente disponibilidade local, consistência durante sincronização e resiliência.

### 4.2 Reserva exclusiva de leitos

Um leito regulado só pode estar reservado para um paciente de cada vez, mesmo quando várias unidades disputam o recurso em tempo real.

Essa capacidade exige **consistência forte**.

Além disso, o sistema legado permanece no circuito durante a migração, criando a necessidade de definir explicitamente qual sistema possui autoridade sobre cada operação.

### 4.3 Prontuário eletrônico

O prontuário possui dados sensíveis e, segundo a premissa da atividade, deve ser mantido por 20 anos.

Também é necessário identificar quem acessou ou alterou os registros.

A arquitetura precisa permitir propriedade explícita dos dados, auditoria, retenção de longo prazo e controle das fronteiras de acesso.

O tratamento jurídico detalhado das solicitações relacionadas à LGPD não é definido pela atividade. A arquitetura fornece mecanismos de propriedade, auditoria e aplicação de políticas de retenção, mas a regra jurídica específica deverá ser definida pela organização responsável.

### 4.4 Farmácia e estoque

A farmácia municipal possui aproximadamente 1.200 itens de estoque, com controle de lote e validade.

Uma dispensação somente pode ser realizada quando existe uma receita correspondente no prontuário.

Esse fluxo exige comportamento transacional e fronteiras claras entre Prontuário e Farmácia.

### 4.5 Vigilância epidemiológica

Doenças de notificação compulsória precisam ser comunicadas à Vigilância Epidemiológica em até 24 horas.

Os sistemas federais utilizados nas integrações possuem períodos de indisponibilidade.

A indisponibilidade de um sistema externo não pode impedir o registro municipal da notificação ou bloquear a unidade de saúde.

### 4.6 Campanhas de vacinação

Durante campanhas, o serviço de agendamento pode receber um pico de aproximadamente vinte vezes o acesso normal.

A arquitetura precisa permitir aumento de capacidade sem exigir uma decomposição antecipada de toda a aplicação em serviços independentes.

---

## 5. Visão geral da arquitetura

A estrutura principal escolhida é um **monolito modular**, complementado por **arquitetura hexagonal em fronteiras específicas**.

O monolito modular define a estrutura da Aplicação de Saúde:

- uma única unidade principal de implantação;
- módulos organizados por capacidade de negócio;
- interfaces públicas entre módulos;
- internos privados;
- propriedade lógica dos dados.

Essas características correspondem ao mecanismo descrito para o monolito modular no livro. **(Livro, seções 6.1 a 6.3.)**

A arquitetura hexagonal é utilizada em escala menor quando um módulo depende de sistema legado, sistema externo, mensageria ou outra infraestrutura cuja implementação deva permanecer isolada do domínio. Nesse estilo, as interfaces são declaradas pelo lado interno e implementadas externamente por adaptadores. **(Livro, seções 7.1 a 7.3.)**

Os dois estilos, portanto, possuem fronteiras diferentes:

- o **monolito modular** define como a aplicação principal é estruturada e implantada;
- a **arquitetura hexagonal** define como determinadas dependências externas e tecnológicas são isoladas por portas e adaptadores.

O próprio livro apresenta a combinação de monolito modular com portas e adaptadores como uma composição possível entre os estilos. **(Livro, seções 6.9 e 7.9.)**

Essa composição está registrada no **ADR 0001**.

---

## 6. Por que não microsserviços agora

A aplicação possui vários subdomínios, mas isso não significa que cada um precise constituir uma unidade de implantação independente.

O livro aponta o monolito modular como apropriado quando o domínio justifica fronteiras internas, mas a equipe ainda é pequena e a organização não possui uma plataforma operacional distribuída madura. Também registra como custo do estilo uma única unidade de implantação e um conjunto único de métricas e pipeline. **(Livro, seções 6.5 e 6.7.)**

Com uma equipe de seis pessoas e nenhuma equipe dedicada de operação, distribuir antecipadamente cada capacidade aumentaria a quantidade de unidades de implantação e de problemas associados à operação distribuída sem uma necessidade organizacional comprovada.

Isso não significa que a aplicação nunca poderá possuir serviços independentes. A decisão é **não distribuí-los antecipadamente**.

O monolito modular mantém fronteiras internas que podem servir de ponto de partida para uma futura extração quando houver uma necessidade concreta. **(Livro, seções 6.5 e 6.9.)**

---

## 7. C4 — Contexto

O nível de contexto representa o Sistema Municipal Integrado de Saúde como uma única caixa e apresenta os atores e sistemas externos com os quais ele interage.

Diagrama completo: [`c4-contexto.md`](./c4-contexto.md)

Os principais atores são:

- Paciente e família;
- Profissionais da rede;
- Gestão e vigilância.

Os sistemas externos principais são:

- Sistema legado de regulação;
- Sistemas federais de saúde.

O legado permanece responsável pelas capacidades de regulação que ainda não foram migradas.

Os sistemas federais trocam informações com a rede municipal, mas sua disponibilidade não determina a disponibilidade dos fluxos locais que não precisam de resposta externa imediata.

---

## 8. C4 — Contêineres

O nível de contêineres apresenta as unidades executáveis e de armazenamento que compõem o sistema.

Diagrama completo: [`c4-conteineres.md`](./c4-conteineres.md)

### 8.1 Portal Web

Atende pacientes, familiares, gestão e vigilância.

Não utiliza o mecanismo de operação offline das unidades assistenciais.

### 8.2 Aplicação da Unidade

É utilizada por profissionais de UBS, UPA, hospital e farmácia.

Essa aplicação participa diretamente dos fluxos assistenciais e possui suporte a armazenamento local para as operações autorizadas a continuar durante indisponibilidade de internet.

### 8.3 Armazenamento Local

Mantém temporariamente as operações que ainda não foram confirmadas pelo sistema central.

Esse armazenamento não constitui uma segunda fonte definitiva do estado da rede.

### 8.4 Aplicação de Saúde

É a principal unidade de implantação do backend.

Sua estrutura interna segue o estilo de **monolito modular** e concentra as capacidades de Triagem e Atendimento, Prontuário, Regulação, Farmácia e Estoque, Agendamento e Vigilância Epidemiológica.

### 8.5 Banco de Dados Central

É um banco relacional compartilhado fisicamente pela aplicação.

Apesar do compartilhamento físico, os dados são separados logicamente por módulo. O livro descreve esse arranjo como um dos elementos do monolito modular: o banco permanece único, mas cada módulo é proprietário de suas tabelas e os demais não devem acessá-las diretamente. **(Livro, seção 6.2.)**

A decisão está registrada no **ADR 0002**.

### 8.6 Fila Persistente

É utilizada somente para tarefas de integração que podem ser processadas posteriormente.

O uso de mensageria permite desacoplamento temporal quando o produtor não precisa da resposta do consumidor para prosseguir, mas introduz entrega eventual, tratamento de duplicatas e necessidade de monitoramento. **(Livro, seções 11.2, 11.5 e 11.7.)**

Seu uso é localizado e não significa adoção de arquitetura orientada a eventos para toda a aplicação.

### 8.7 Função de Integração

A fila aciona uma função gerenciada responsável por trabalhos assíncronos curtos de integração.

O livro aponta trabalhos curtos, discretos, acionados por evento e executados por equipes pequenas sem plataforma própria como sinais favoráveis ao uso localizado de serverless. **(Livro, seção 12.5.)**

---

## 9. C4 — Componentes da Aplicação de Saúde

O nível de componentes abre apenas o contêiner mais importante: a **Aplicação de Saúde**.

Diagrama completo: [`c4-componentes.md`](./c4-componentes.md)

### 9.1 API de Entrada

Recebe operações originadas pelo Portal Web e pela Aplicação da Unidade e encaminha cada uma para o módulo correspondente.

### 9.2 Triagem e Atendimento

É responsável pelos registros produzidos nos fluxos de triagem e atendimento.

### 9.3 Prontuário Eletrônico

Mantém histórico clínico, receitas e informações necessárias à auditoria dos registros.

### 9.4 Regulação

Coordena solicitações de leitos e transporte.

A confirmação definitiva depende de qual sistema possui a autoridade daquela capacidade durante a migração.

### 9.5 Farmácia e Estoque

Controla itens, lotes, validade e dispensações.

Quando precisa validar uma receita, utiliza a interface pública do módulo de Prontuário.

### 9.6 Agendamento

Mantém consultas, exames, vacinação e outros agendamentos.

### 9.7 Vigilância Epidemiológica

Mantém as notificações e informações epidemiológicas da rede municipal.

### 9.8 Adaptador de Regulação Legada

Isola o contrato do sistema legado e funciona como **camada anticorrupção**, papel que o livro posiciona naturalmente como um adaptador secundário em uma arquitetura hexagonal. **(Livro, seção 19.3; seção 7.3.)**

### 9.9 Adaptador de Mensageria

Isola os módulos da tecnologia utilizada pela fila persistente.

---

## 10. Fronteiras entre módulos

A aplicação segue as seguintes regras arquiteturais:

1. cada módulo possui uma interface pública;
2. implementações internas não são acessadas por outros módulos;
3. cada módulo é proprietário de seus dados;
4. nenhum módulo realiza consultas diretas às tabelas de outro módulo;
5. chamadas entre módulos que necessitam resposta imediata são realizadas em processo;
6. dependências tecnológicas ou externas relevantes são isoladas por adaptadores;
7. ciclos entre módulos devem ser evitados e tratados como violação arquitetural.

Essas regras correspondem ao mecanismo do monolito modular descrito no livro, incluindo interface pública restrita, internos privados, dados logicamente separados e verificação das fronteiras. **(Livro, seções 6.2 e 6.3.)**

O livro também alerta que fronteiras apenas documentais tendem a se degradar e recomenda verificação automatizada por função de aptidão. **(Livro, seção 6.6.)**

---

## 11. Propriedade e consistência dos dados

O sistema utiliza um banco relacional fisicamente compartilhado e separação lógica dos dados por módulo. Essa organização segue diretamente o modelo de dados do monolito modular. **(Livro, seção 6.2.)**

O livro registra que esse arranjo exige disciplina de acesso, mas evita o custo de consistência distribuída enquanto os módulos permanecem no mesmo banco. **(Livro, seção 6.7.)**

### 11.1 Leitos

Reserva de leito exige consistência forte.

Uma confirmação definitiva nunca pode existir simultaneamente para dois pacientes.

Por isso, existe sempre **uma única autoridade de escrita** para a capacidade.

### 11.2 Prontuário

O prontuário exige longa retenção e rastreabilidade.

Seu módulo é responsável pelos dados clínicos e pelas informações de auditoria.

### 11.3 Farmácia

Dispensação e movimentação de estoque são transacionais.

A validação de uma receita ocorre por meio do contrato público do Prontuário, preservando a propriedade dos dados.

---

## 12. Regulação e convivência com o legado

A substituição do sistema legado não será realizada por uma única troca.

A estratégia utilizada é o **estrangulamento**, no qual o sistema novo assume capacidades gradualmente enquanto o legado continua atendendo o que ainda não foi migrado. **(Livro, seção 19.2.)**

Enquanto uma capacidade ainda não tiver sido migrada:

```text
Aplicação de Saúde
        ↓
Regulação
        ↓
Adaptador de Regulação Legada
        ↓
Sistema legado
```

Nesse estágio, o legado permanece como **única autoridade de escrita** da capacidade.

Quando a capacidade for migrada:

```text
Aplicação de Saúde
        ↓
Regulação
        ↓
Banco de Dados Central
```

A partir desse momento, o legado deixa de confirmar novas operações dessa capacidade.

O livro alerta que manter duas implementações responsáveis pela mesma capacidade após a migração impede o desligamento real do legado. Também descreve o risco da escrita dupla entre armazenamentos independentes, que não possui transação atômica única. **(Livro, seções 19.2 e 19.5.)**

A estratégia está detalhada nos **ADRs 0002 e 0003**.

---

## 13. Operação durante indisponibilidade de internet

O funcionamento offline é limitado às capacidades que podem operar localmente sem coordenação global imediata.

```text
Aplicação da Unidade
        ↓
Armazenamento Local
        ↓
operação pendente
```

Quando a conexão retorna:

```text
Operação pendente
        ↓
Aplicação de Saúde
        ↓
processamento
        ↓
confirmação
```

Cada operação possui um identificador de idempotência.

Se o servidor processar uma operação, mas a confirmação for perdida na rede, o cliente poderá enviá-la novamente sem que o mesmo efeito seja aplicado duas vezes.

O livro estabelece a idempotência como condição para que uma operação possa ser repetida com segurança após uma falha transitória. **(Livro, seção 18.4.)**

Esse mecanismo está registrado no **ADR 0005** e será validado pelo spike da Entrega 3.

Operações de consistência global, especialmente reserva definitiva de leitos, não são autorizadas a concluir offline.

---

## 14. Integração com sistemas federais

A integração federal não constitui uma dependência síncrona obrigatória para todas as operações municipais.

No caso das notificações epidemiológicas:

```text
Vigilância Epidemiológica
        ↓
Banco de Dados Central
        ↓
tarefa de integração
        ↓
Fila Persistente
        ↓
Função de Integração
        ↓
Sistema Federal
```

A notificação é primeiro registrada municipalmente.

Somente depois é criada a tarefa necessária à transmissão externa.

Caso o sistema federal esteja indisponível, a tarefa permanece pendente para processamento posterior.

O desacoplamento temporal por mensageria é adequado quando o produtor não precisa da resposta para prosseguir e pode permitir absorção de picos; o custo é consistência eventual e necessidade de tratar duplicação e falhas. **(Livro, seções 11.5 a 11.7.)**

O uso da fila é **localizado**. Operações que precisam de resposta imediata ou consistência forte permanecem síncronas, situação em que o próprio livro recomenda evitar o estilo orientado a eventos. **(Livro, seção 11.6.)**

A decisão está registrada no **ADR 0006**.

---

## 15. Operação e implantação

A Aplicação de Saúde permanece como uma única unidade principal de implantação, propriedade característica do monolito modular. **(Livro, seções 6.1 e 6.3.)**

O projeto utiliza serviços gerenciados para banco, mensageria e processamento assíncrono curto.

O uso da função gerenciada fica restrito ao trabalho curto e acionado pela fila, coerente com os sinais de adoção descritos para serverless. **(Livro, seção 12.5.)**

A aplicação principal pode possuir mais de uma instância quando houver necessidade de aumentar capacidade. Como consequência do monolito modular, porém, seus módulos permanecem na mesma unidade de implantação e são escalados em conjunto. **(Livro, seção 6.6.)**

A observabilidade mínima prevista utiliza logs estruturados, métricas e pontos de saúde, elementos tratados no capítulo de observabilidade do livro. **(Livro, seção 18.5.)**

Chamadas externas devem possuir tempo limite explícito, padrão considerado obrigatório pelo livro para chamadas que cruzam limites de processo. **(Livro, seção 18.4.)**

A estratégia está registrada no **ADR 0004**.

---

## 16. Pico de campanhas

O agendamento pode apresentar picos muito maiores durante campanhas de vacinação.

Na primeira versão, esse requisito não será resolvido extraindo antecipadamente o módulo de Agendamento para um microsserviço.

A Aplicação de Saúde poderá aumentar sua quantidade de instâncias quando necessário, aceitando que os módulos sejam escalados juntos.

O livro registra a escala conjunta como uma das limitações do monolito modular: quando apenas uma capacidade possui perfil de carga muito diferente, escalar toda a unidade pode desperdiçar recursos. **(Livro, seção 6.6.)**

Esse custo é aceito no estágio atual do projeto em troca de menor complexidade operacional.

Caso medições futuras mostrem que o módulo possui perfil de escala significativamente diferente do restante, sua fronteira já existente permitirá reavaliar uma extração. **(Livro, seções 6.5 e 6.9.)**

---

## 17. O que não será feito agora

A primeira versão não adotará:

- um microsserviço por subdomínio;
- um banco físico por módulo;
- arquitetura orientada a eventos para toda a aplicação;
- Event Sourcing como fonte de verdade geral;
- service mesh;
- plataforma própria de orquestração;
- substituição integral do legado em uma única virada.

A decisão de evitar distribuição antecipada é sustentada pelos sinais de adoção e custo do monolito modular para equipes pequenas e sem plataforma operacional madura. **(Livro, seções 6.5 e 6.7.)**

O uso localizado de mensageria é preferido a uma arquitetura global orientada a eventos porque várias capacidades exigem resposta imediata e consistência forte. **(Livro, seção 11.6.)**

A migração do legado permanece incremental por capacidade, em vez de uma reescrita completa. **(Livro, seções 19.1 e 19.2.)**

A evolução futura é preservada por módulos alinhados às capacidades de negócio, interfaces públicas, propriedade lógica dos dados, portas e adaptadores e migração por capacidade. **(Livro, seções 6.9, 7.9 e 19.2.)**

---

## 18. Decisões arquiteturais

| ADR                                                                              | Decisão                                                  |
| -------------------------------------------------------------------------------- | --------------------------------------------------------- |
| [ADR 0001](./adr/0001-adotar-monolito-modular-com-fronteiras-hexagonais.md)       | Adotar monolito modular com fronteiras hexagonais         |
| [ADR 0002](./adr/0002-definir-propriedade-e-consistencia-dos-dados.md)            | Definir propriedade e consistência dos dados por módulo |
| [ADR 0003](./adr/0003-integrar-legado-e-terceiros-por-adaptadores.md)             | Integrar legado e terceiros por adaptadores               |
| [ADR 0004](./adr/0004-operar-com-uma-unidade-principal-e-servicos-gerenciados.md) | Operar com uma unidade principal e serviços gerenciados  |
| [ADR 0005](./adr/0005-sincronizar-atendimentos-offline-de-forma-idempotente.md)   | Sincronizar atendimentos offline de forma idempotente     |
| [ADR 0006](./adr/0006-usar-fila-persistente-para-integracoes-assincronas.md)      | Usar fila persistente para integrações assíncronas     |

---

## 19. Mapa de restrições e decisões

A rastreabilidade entre o Caso Saúde, o Envelope A e as decisões da arquitetura está detalhada em:

[`mapa-restricoes-decisoes.md`](./mapa-restricoes-decisoes.md)

---

## 20. Respostas às perguntas obrigatórias

As cinco perguntas obrigatórias do Caso Saúde são tratadas em:

[`respostas-perguntas.md`](./respostas-perguntas.md)

| Pergunta                                        | ADRs                |
| ----------------------------------------------- | ------------------- |
| Operação com internet indisponível           | ADR 0002 e ADR 0005 |
| Duas unidades disputando o mesmo leito          | ADR 0002 e ADR 0003 |
| Auditoria e retenção do prontuário           | ADR 0002            |
| Notificação com sistema federal indisponível | ADR 0004 e ADR 0006 |
| Substituição gradual do legado                | ADR 0001 e ADR 0003 |

---

## 21. Decisão mais arriscada

A decisão considerada mais arriscada é a **sincronização das operações realizadas offline**.

O principal cenário de falha é:

1. a unidade realiza a operação offline;
2. a conexão retorna;
3. a operação é enviada;
4. o servidor a processa;
5. a confirmação se perde;
6. o cliente envia novamente a mesma operação.

Sem idempotência, o mesmo atendimento poderia ser aplicado duas vezes. O livro trata a idempotência como condição necessária para repetição segura de operações. **(Livro, seção 18.4.)**

Por isso, o **ADR 0005** será validado experimentalmente na Entrega 3.

---

## 22. Trade-offs aceitos

A arquitetura não busca maximizar todos os atributos de qualidade simultaneamente. O livro trata explicitamente arquitetura como exercício de trade-offs. **(Livro, seção 2.4.)**

### Simplicidade operacional × escalabilidade seletiva

Manter uma aplicação principal reduz unidades de implantação, porém significa que módulos são implantados e escalados juntos. **(Livro, seções 6.6 e 6.7.)**

### Consistência × disponibilidade offline

Triagem e atendimento podem trabalhar temporariamente offline, mas operações de consistência global, como reserva de leito, não podem ser concluídas sem comunicação com a autoridade responsável.

### Desacoplamento × complexidade de mensageria

A fila protege operações municipais da indisponibilidade federal, mas adiciona consistência eventual, tratamento de duplicatas e monitoramento. **(Livro, seção 11.7.)**

### Isolamento do legado × código de tradução

A camada anticorrupção protege o domínio novo, mas acrescenta tradução e manutenção enquanto o legado existir. **(Livro, seção 19.3.)**

---

## 23. Referências utilizadas

A principal referência arquitetural do projeto é:

**ABREU, Douglas H. S. _Estilos Arquiteturais de Software: guia de consulta_. 2026.**

Seções particularmente utilizadas:

- Capítulo 2 — estilos, padrões, atributos de qualidade e trade-offs;
- Capítulo 3 — componentes, conectores, configurações e modelo C4;
- Capítulo 4 — registros de decisão arquitetural;
- Capítulo 6 — monolito modular;
- Capítulo 7 — arquitetura hexagonal;
- Capítulo 11 — arquitetura orientada a eventos e mensageria;
- Capítulo 12 — serverless;
- Capítulo 18 — resiliência e observabilidade;
- Capítulo 19 — evolução e migração de legado;
- Apêndice B — modelos de ADR e C4.

As premissas de volume, prazos, retenção, disponibilidade da rede e requisitos funcionais utilizadas neste documento são as definidas pelo **Caso Saúde — Envelope A** da atividade.
