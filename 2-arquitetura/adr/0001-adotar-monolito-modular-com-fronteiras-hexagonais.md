
# ADR 0001: adotar monolito modular com fronteiras hexagonais

**Status:** aceito

**Contexto:**
A primeira versão será desenvolvida por uma equipe de seis pessoas, sem equipe dedicada de operação, e precisa colocar o prontuário em funcionamento em três UBS em quatro meses. O domínio possui capacidades distintas, como atendimento, prontuário, regulação, farmácia, agendamento e vigilância, além de dependências de sistemas externos e de um sistema legado que continuará ativo durante a migração. A arquitetura precisa manter baixo o custo inicial de operação sem impedir evolução posterior.

**Decisão:**
Adotar um **monolito modular** como estrutura principal e única unidade de implantação da Aplicação de Saúde, com módulos alinhados às capacidades de negócio e comunicação por interfaces públicas. Aplicar **arquitetura hexagonal** somente nas fronteiras com sistemas externos ou infraestrutura substituível, por meio de portas e adaptadores. **(Livro, seções 6.1, 6.2, 6.9 e 7.9.)**

**Alternativas consideradas:**

* **Monolito em camadas:** descartado porque as fronteiras principais do problema são capacidades de negócio distintas, e não apenas responsabilidades técnicas. **(Livro, seções 6.1 e 6.2.)**
* **Microsserviços desde a primeira versão:** descartado porque a equipe é pequena e não possui uma plataforma operacional distribuída madura, sinais que favorecem manter os módulos em uma única unidade de implantação. **(Livro, seções 6.5 e 6.7.)**
* **Aplicar arquitetura hexagonal uniformemente em todos os módulos:** descartado porque o livro alerta para o excesso de cerimônia quando portas e adaptadores são introduzidos sem uma fronteira tecnológica que justifique o custo. **(Livro, seções 7.6 e 7.7.)**

**Consequências:**

* **Positivas:** as capacidades de negócio permanecem explicitamente separadas dentro de uma única unidade de implantação; a operação inicial permanece concentrada em um artefato; dependências externas ficam isoladas do domínio; as fronteiras criadas permitem avaliar extrações futuras sem distribuir o sistema antecipadamente. **(Livro, seções 6.7, 6.9 e 7.7.)**
* **Negativas:** todos os módulos principais continuam sendo implantados e escalados juntos; falhas graves no processo principal podem atingir várias capacidades; a modularidade depende de disciplina e verificação das fronteiras; portas e adaptadores acrescentam código nas integrações em que forem aplicados. **(Livro, seções 6.6, 6.7 e 7.7.)**
