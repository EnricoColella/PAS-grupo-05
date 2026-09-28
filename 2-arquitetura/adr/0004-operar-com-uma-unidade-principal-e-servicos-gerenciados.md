
# ADR 0004: operar com uma unidade principal e serviços gerenciados

**Status:** aceito

**Contexto:**
A solução será construída por seis desenvolvedores, sem equipe dedicada de operação, utilizando nuvem pública paga por uso. O sistema precisa colocar o piloto em produção rapidamente, suportar picos temporários de acesso e manter visibilidade suficiente para identificar falhas. Ao mesmo tempo, a equipe deve evitar assumir uma plataforma operacional distribuída mais complexa do que o necessário.

**Decisão:**
Implantar a  **Aplicação de Saúde como uma única unidade principal** , utilizando serviços gerenciados para banco relacional e mensageria. Utilizar uma **função gerenciada acionada pela fila persistente** para trabalhos assíncronos curtos de integração, mantendo observabilidade por logs estruturados, métricas e pontos de saúde. **(Livro, seções 6.7, 12.5 e 18.5.)**

**Alternativas consideradas:**

* **Implantar cada módulo como serviço independente:** descartada porque aumentaria a quantidade de unidades de implantação e a superfície operacional para uma equipe sem operação distribuída madura. **(Livro, seções 6.5 e 6.7.)**
* **Operar infraestrutura própria para banco, mensageria e orquestração:** descartada porque o envelope prioriza uma equipe pequena sem operação dedicada, e o uso localizado de capacidades gerenciadas reduz a quantidade de infraestrutura diretamente operada pela equipe. **(Livro, seções 12.5 e 12.7.)**
* **Implementar toda a aplicação como funções serverless:** descartada porque o livro recomenda evitar serverless em cargas contínuas, fluxos síncronos conversadores e situações em que a latência e o estado transacional tornam o modelo inadequado. **(Livro, seção 12.6.)**

**Consequências:**

* **Positivas:** a aplicação principal permanece em uma única unidade de implantação; trabalhos assíncronos curtos podem executar sob demanda; logs, métricas e pontos de saúde fornecem visibilidade operacional. **(Livro, seções 6.7, 12.5 e 18.5.)**
* **Negativas:** os módulos principais continuam sendo implantados e escalados juntos; um pico localizado pode exigir aumentar a capacidade do monolito inteiro; serviços gerenciados possuem limites e custos que precisam ser acompanhados. **(Livro, seções 6.6, 12.6 e 12.7.)**
