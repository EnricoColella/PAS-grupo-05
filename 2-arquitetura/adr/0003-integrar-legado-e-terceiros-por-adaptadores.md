
# ADR 0003: integrar legado e terceiros por adaptadores

**Status:** aceito

**Contexto:**
O sistema legado de regulação continuará ativo por pelo menos dois anos e precisará coexistir com a nova solução durante a substituição gradual. A aplicação também depende de sistemas federais cujos contratos e disponibilidade estão fora do controle da equipe. Essas dependências externas não devem contaminar os modelos internos dos módulos de negócio nem criar duas implementações ativas da mesma capacidade.

**Decisão:**
Isolar o legado e os sistemas externos por  **portas secundárias e adaptadores** , utilizando uma **camada anticorrupção** para traduzir contratos e modelos. Substituir o sistema legado por  **estrangulamento** , migrando uma capacidade de negócio por vez e mantendo, em cada etapa, apenas uma implementação responsável pelas operações daquela capacidade. **(Livro, seções 7.3, 19.2 e 19.3.)**

**Alternativas consideradas:**

* **Substituir todo o legado de uma vez:** descartada porque a reescrita completa concentra risco e valor apenas no fim, enquanto o capítulo de evolução recomenda substituição incremental com o sistema em funcionamento. **(Livro, seções 19.1 e 19.2.)**
* **Consumir diretamente os contratos do legado dentro dos módulos de negócio:** descartada porque espalharia detalhes do modelo antigo pelo domínio, exatamente o acoplamento que a camada anticorrupção busca evitar. **(Livro, seção 19.3.)**
* **Manter sistema novo e legado gravando a mesma capacidade em paralelo:** descartada porque manter duas implementações ativas da mesma regra impede o desligamento real do legado e a escrita dupla pode produzir divergência entre os estados. **(Livro, seções 19.2 e 19.5.)**

**Consequências:**

* **Positivas:** detalhes e formatos externos ficam concentrados nos adaptadores; o domínio novo permanece independente do modelo legado; a migração pode ocorrer gradualmente por capacidade; cada etapa pode ser validada antes da transferência de autoridade. **(Livro, seções 19.2 e 19.3.)**
* **Negativas:** legado e sistema novo precisarão coexistir durante a transição; adaptadores e traduções acrescentam código e testes; a camada anticorrupção possui custo de manutenção enquanto o legado existir e deve ser removida ao final. **(Livro, seção 19.3.)**
