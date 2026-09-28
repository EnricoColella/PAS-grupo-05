# Spike — sincronização offline idempotente

Este spike valida o **ADR 0005 — sincronizar atendimentos offline de forma idempotente**.

O risco testado é simples: uma UBS ou UPA registra uma operação enquanto está sem internet. Quando a conexão retorna, o servidor pode processar a operação corretamente, mas a confirmação pode se perder. Se a unidade reenviar a mesma operação sem nenhum controle, o atendimento poderia ser criado duas vezes.

O programa simula somente o necessário para provar essa decisão. A operação fica em um dicionário que representa o armazenamento local da unidade. Quando a rede volta, ela é enviada ao servidor com uma **chave de idempotência**. O servidor guarda as chaves já processadas e o atendimento correspondente. Na primeira tentativa, a operação é processada, mas a confirmação é propositalmente perdida. Na segunda tentativa, a mesma chave é enviada novamente e o servidor devolve o resultado anterior sem criar outro atendimento.

Para executar:

```bash
python3 exemplo.py
```

A saída deve ser igual ao conteúdo de `saida-esperada.txt`. O resultado final esperado é: **1 atendimento criado, 1 chave processada e 0 operações locais pendentes**.

Se a decisão estivesse errada e o servidor executasse novamente toda operação reenviada, a segunda tentativa criaria um segundo atendimento. O spike existe justamente para mostrar que isso não acontece.

O mecanismo segue o princípio apresentado no **Livro, seção 18.4**: uma repetição de tentativa só é segura quando a operação é idempotente, por exemplo por meio de uma chave enviada pelo cliente.
