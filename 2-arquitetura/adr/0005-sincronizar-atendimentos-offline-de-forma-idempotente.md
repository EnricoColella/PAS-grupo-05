
# ADR 0005: sincronizar atendimentos offline de forma idempotente

**Status:** aceito

**Contexto:**
As UBS e UPAs podem sofrer quedas de internet por períodos de minutos a horas, mas triagem e atendimento precisam continuar funcionando. Quando a conexão retornar, os registros produzidos localmente devem chegar ao sistema central sem perda e sem duplicação, inclusive quando uma operação já tiver sido processada e sua confirmação se perder durante a comunicação.

**Decisão:**
Permitir o registro local temporário das operações autorizadas a funcionar offline e sincronizá-las posteriormente com o sistema central utilizando  **identificadores únicos de idempotência** . O servidor reconhecerá reenvios da mesma operação e garantirá que seu efeito seja aplicado uma única vez. **(Livro, seção 18.4.)**

**Alternativas consideradas:**

* **Bloquear o atendimento durante a indisponibilidade da internet:** descartada porque viola diretamente o requisito de continuidade definido no caso.
* **Reenviar operações sem idempotência:** descartada porque uma nova tentativa sem chave de idempotência pode repetir um efeito que já foi aplicado. **(Livro, seção 18.4.)**
* **Tratar o armazenamento local como fonte definitiva dos dados:** descartada porque permitiria estados independentes nas unidades para informações que precisam convergir para o sistema central.

**Consequências:**

* **Positivas:** triagens e atendimentos podem continuar durante interrupções de conectividade; operações pendentes podem ser reenviadas com segurança; perda de confirmação não produz aplicação duplicada; o mecanismo pode ser validado isoladamente pelo spike. **(Livro, seção 18.4.)**
* **Negativas:** a aplicação da unidade precisa manter estado temporário de sincronização; o servidor precisa reconhecer identificadores já processados; conflitos que não sejam resolvidos apenas por idempotência exigirão tratamento explícito; operações de consistência global continuam indisponíveis offline.
