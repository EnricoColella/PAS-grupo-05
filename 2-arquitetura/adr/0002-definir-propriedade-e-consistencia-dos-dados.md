
# ADR 0002: definir propriedade e consistência dos dados por módulo

**Status:** aceito

**Contexto:**
O sistema possui dados com requisitos diferentes de consistência, retenção e rastreabilidade. A regulação exige que um leito nunca seja reservado simultaneamente para dois pacientes, o prontuário possui retenção de longo prazo e auditoria, e a farmácia depende de operações transacionais. Durante a migração, o sistema legado de regulação continuará ativo e parte das capacidades ainda permanecerá sob sua responsabilidade.

**Decisão:**
Utilizar um  **banco relacional central** , com separação lógica e propriedade exclusiva dos dados por módulo; nenhum módulo acessará diretamente as tabelas pertencentes a outro. Para capacidades que exigem consistência forte, haverá  **uma única autoridade de escrita por vez** : enquanto uma capacidade de regulação permanecer no legado, somente ele poderá confirmar suas operações; após a migração, essa autoridade passará integralmente ao módulo de Regulação do sistema novo. **(Livro, seção 6.2; seções 19.2 e 19.5.)**

**Alternativas consideradas:**

* **Um banco independente por módulo:** descartado nesta primeira versão porque a separação física introduziria problemas de consistência distribuída que o monolito modular evita enquanto os módulos compartilham a mesma unidade e o mesmo banco. **(Livro, seção 6.7.)**
* **Banco compartilhado sem propriedade explícita:** descartado porque permitiria acesso direto entre tabelas de diferentes capacidades e enfraqueceria as fronteiras do monolito modular. **(Livro, seção 6.2.)**
* **Gravar reservas simultaneamente no legado e no sistema novo:** descartado porque a escrita dupla em armazenamentos independentes não possui uma transação atômica única e pode gerar divergência após falha. **(Livro, seção 19.5.)**

**Consequências:**

* **Positivas:** operações que exigem consistência imediata podem permanecer em transações locais; cada módulo possui responsabilidade clara sobre seus dados; a reserva de leitos não possui duas fontes de verdade simultâneas; a separação lógica preserva uma possibilidade futura de extração. **(Livro, seções 6.2, 6.7 e 6.9.)**
* **Negativas:** o banco central continua sendo uma dependência compartilhada; consultas entre módulos precisam respeitar interfaces públicas em vez de acessar tabelas diretamente; uma futura separação física exigirá migração dos dados e revisão das operações hoje locais. **(Livro, seções 6.2 e 6.7.)**
