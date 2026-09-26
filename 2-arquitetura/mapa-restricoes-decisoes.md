
# Mapa de Restrições e Decisões

Este documento relaciona as restrições do **Envelope A** e os requisitos que mais pressionam o Caso Saúde às decisões arquiteturais adotadas.

## Decisões arquiteturais

| ID           | Decisão                                                                                                                                                                                                                                           | ADR relacionado |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------- |
| **D1** | Adotar**monolito modular** como estrutura principal e aplicar **portas e adaptadores** nas fronteiras com sistemas externos e infraestrutura substituível.                                                                            | ADR 0001        |
| **D2** | Manter um**banco relacional central**, com propriedade lógica dos dados por módulo e nível de consistência definido conforme o subdomínio. Capacidades que exigem consistência forte possuem uma única autoridade de escrita por vez. | ADR 0002        |
| **D3** | Isolar legado e terceiros por adaptadores e substituir o sistema de regulação por**estrangulamento**, migrando uma capacidade de cada vez e evitando duas autoridades simultâneas sobre a mesma operação.                               | ADR 0003        |
| **D4** | Operar poucas unidades próprias em nuvem, utilizando serviços gerenciados para banco e mensageria e uma**função gerenciada** para trabalhos assíncronos curtos, com logs, métricas e pontos de saúde.                                 | ADR 0004        |
| **D5** | Permitir operação offline nas unidades por armazenamento local temporário e sincronização posterior com**identificadores únicos e processamento idempotente**.                                                                         | ADR 0005        |
| **D6** | Utilizar**fila persistente de tarefas de integração** para operações externas que não exigem resposta imediata, processadas posteriormente por uma função gerenciada.                                                                 | ADR 0006        |

---

## Restrições do Envelope A

| Restrição                                                       | Impacto arquitetural                                                                                                                                          | Decisão |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| **Equipe de 6 desenvolvedores**                             | A equipe não deve assumir a coordenação e operação de grande quantidade de serviços independentes.                                                      | D1, D4   |
| **Sem equipe dedicada de operação**                       | A arquitetura precisa reduzir a quantidade de unidades próprias e evitar infraestrutura distribuída desnecessária.                                         | D1, D4   |
| **Caixa para 6 meses**                                      | A primeira versão precisa priorizar simplicidade operacional e evitar investimentos antecipados em estruturas cuja necessidade ainda não foi comprovada.    | D1, D4   |
| **Nuvem pública paga por uso**                             | Recursos gerenciados podem ser utilizados nas capacidades em que eliminam trabalho operacional relevante e trabalhos assíncronos podem executar sob demanda. | D4, D6   |
| **Entregar rápido e barato sem impedir evolução futura** | As fronteiras de negócio precisam existir desde a primeira versão, mesmo sem distribuir fisicamente os módulos.                                            | D1, D3   |
| **Prontuário circulando em 3 UBS em 4 meses**              | A arquitetura inicial precisa permitir entrega incremental e funcionamento mesmo com conectividade instável nas unidades.                                    | D1, D5   |

### O que não será feito agora

Para atender à pergunta obrigatória do Envelope A, a primeira versão **não adotará**:

- microsserviços para cada módulo de negócio;
- banco de dados fisicamente separado para cada módulo;
- arquitetura orientada a eventos como estrutura global da aplicação;
- service mesh ou plataforma própria de orquestração;
- substituição completa do sistema legado em uma única migração;
- Event Sourcing como mecanismo geral de persistência.

Essas opções não são necessárias para o piloto atual. A possibilidade de evolução é preservada por fronteiras explícitas entre módulos, propriedade lógica dos dados, portas e adaptadores e migração gradual por capacidade.

---

## Requisitos críticos do Caso Saúde

| Requisito que pressiona                                                      | Impacto arquitetural                                                                                                                                                      | Decisão |
| ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| **70 UBS, 5 UPAs e 1 hospital de referência**                         | O sistema precisa atender múltiplas unidades sem criar uma implantação independente para cada uma.                                                                     | D1, D4   |
| **12 mil atendimentos por dia**                                        | A aplicação precisa permitir aumento de capacidade mantendo a operação simples.                                                                                       | D4       |
| **Pico de 40 triagens por hora na maior UPA**                          | O caminho de triagem deve permanecer simples e não depender de múltiplas chamadas distribuídas internas.                                                               | D1       |
| **Internet instável nas UBS, com quedas de minutos a horas**          | Triagem e atendimento precisam continuar registrando operações localmente durante a indisponibilidade.                                                                  | D5       |
| **Sincronizar depois sem perder nem duplicar**                         | Reenvios precisam ser seguros e reconhecidos pelo sistema central.                                                                                                        | D5       |
| **Prontuário com retenção de 20 anos**                              | O módulo de Prontuário precisa possuir responsabilidade explícita sobre seus registros e histórico de auditoria.                                                      | D2       |
| **Saber quem acessou e quem alterou o prontuário**                    | A persistência do prontuário precisa incluir informações de auditoria sob responsabilidade do mesmo módulo.                                                          | D2       |
| **Um leito só pode ser reservado para um paciente por vez**           | A confirmação exige consistência forte e uma única autoridade capaz de alterar definitivamente o estado do leito.                                                     | D2       |
| **Unidades disputam leitos em tempo real**                             | A reserva definitiva não pode ser resolvida offline nem por consistência eventual.                                                                                      | D2       |
| **Sistema legado de regulação continuará ativo**                    | Enquanto uma capacidade ainda estiver no legado, ele permanece sua única autoridade de escrita; após a migração, essa autoridade passa integralmente ao sistema novo. | D2, D3   |
| **Legado deve ser substituído gradualmente**                          | A migração precisa ocorrer por capacidade de negócio, utilizando adaptador e camada anticorrupção.                                                                   | D3       |
| **Farmácia possui 1.200 itens com lote e validade**                   | Estoque, lotes e dispensações precisam possuir proprietário explícito e persistência transacional.                                                                   | D2       |
| **Dispensação exige receita vinculada ao prontuário**               | Farmácia deve validar a receita pela interface pública do módulo de Prontuário, sem acessar diretamente seus dados.                                                   | D1, D2   |
| **Notificação compulsória em até 24 horas**                        | A notificação deve ser persistida primeiro na Vigilância municipal, independentemente da disponibilidade federal.                                                      | D2, D6   |
| **Sistema federal pode ficar indisponível**                           | O envio externo que não exige resposta imediata precisa permanecer pendente até poder ser reprocessado.                                                                 | D3, D6   |
| **Sistema externo fora do ar não pode bloquear a unidade**            | Integrações não críticas para a resposta imediata devem ser temporalmente desacopladas.                                                                               | D3, D6   |
| **Campanha de vacinação gera pico de até 20 vezes o acesso normal** | A aplicação precisa permitir aumento temporário de capacidade sem exigir decomposição prévia em serviços independentes.                                            | D4       |
| **Prontuário contém dados sensíveis**                               | A responsabilidade pelos dados e pela auditoria precisa permanecer explícita e controlada pelo módulo proprietário.                                                    | D2       |

---

## Autoridade sobre reserva de leitos durante a migração

A decisão combinada **D2 + D3** estabelece que a reserva possui **uma única autoridade de escrita por capacidade em qualquer momento**.

Enquanto a capacidade ainda estiver no legado:

```text
Aplicação de Saúde
        ↓
Módulo de Regulação
        ↓
Adaptador
        ↓
Sistema legado
        ↓
confirma ou recusa a reserva
```

O sistema novo não confirma paralelamente a mesma reserva.

Depois da migração da capacidade:

```text
Aplicação de Saúde
        ↓
Módulo de Regulação
        ↓
Banco de Dados Central
```

O legado deixa de receber novas operações dessa capacidade.

Não existe, portanto, um período de **dual-write** de reservas.

---

## Uso localizado de processamento assíncrono

A decisão **D6** não significa adoção de arquitetura orientada a eventos para todo o sistema.

Ela se aplica somente quando:

1. a operação local já pode ser considerada concluída;
2. o resultado externo não é necessário imediatamente;
3. uma indisponibilidade externa não deve bloquear o usuário.

Exemplo principal:

```text
Vigilância Epidemiológica
        ↓
notificação persistida
        ↓
tarefa de integração
        ↓
Fila Persistente
        ↓
Função de Integração
        ↓
Sistema Federal
```

Já operações como reserva de leito continuam síncronas porque exigem resposta imediata e consistência forte.

---

# Rastreabilidade inversa

| Decisão                                                 | Forças que justificam sua existência                                                                                                                         |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **D1 — Monolito modular + fronteiras hexagonais** | 6 desenvolvedores; ausência de operação dedicada; prazo curto; vários subdomínios; necessidade de evolução futura; integração com legado e terceiros. |
| **D2 — Propriedade e consistência dos dados**    | Reserva exclusiva de leitos; prontuário de longa retenção; auditoria; receita e dispensação; rastreio de lote; notificações persistidas.                |
| **D3 — Adaptadores e migração gradual**         | Legado ativo por pelo menos dois anos; contratos externos; necessidade de substituição sem interrupção; indisponibilidade de terceiros.                    |
| **D4 — Poucas unidades e serviços gerenciados**  | Equipe pequena; ausência de operação; nuvem paga por uso; campanha com pico de carga; necessidade de observabilidade.                                       |
| **D5 — Offline com idempotência**                | Quedas diárias de internet; continuidade da triagem; sincronização sem perda nem duplicação.                                                              |
| **D6 — Fila persistente de integração**         | Sistema federal indisponível; notificação compulsória; integração não pode bloquear unidade; trabalho assíncrono curto.                                |

Todas as decisões arquiteturais do projeto possuem pelo menos uma força concreta do caso ou do envelope, e todos os requisitos críticos apresentados acima possuem uma decisão responsável por atendê-los.
