
# ADR 0006: usar fila persistente para integrações assíncronas

**Status:** aceito

**Contexto:**
As notificações compulsórias precisam chegar à Vigilância Epidemiológica municipal em até 24 horas, mas os sistemas federais podem ficar temporariamente indisponíveis. A indisponibilidade de um sistema externo não deve bloquear o atendimento nem causar perda de tarefas de integração que ainda precisam ser executadas.

**Decisão:**
Persistir primeiro as informações no sistema municipal e utilizar uma **fila persistente de tarefas de integração** para os envios externos que não exigem resposta imediata. Essas tarefas serão processadas por uma  **função gerenciada** , com reentrega segura por meio de idempotência. **(Livro, seções 11.2, 11.5 e 12.5.)**

**Alternativas consideradas:**

* **Enviar diretamente ao sistema federal antes de concluir a operação local:** descartada porque elimina o desacoplamento temporal e faz a operação municipal depender da disponibilidade do consumidor externo. **(Livro, seções 11.2 e 11.5.)**
* **Manter as tentativas de envio apenas em memória:** descartada porque o trabalho pendente precisa sobreviver à indisponibilidade do consumidor e do processo responsável pelo envio; o corretor de mensagens exerce justamente o papel de manter a mensagem até seu processamento. **(Livro, seção 11.2.)**
* **Adotar arquitetura orientada a eventos em toda a aplicação:** descartada porque fluxos que exigem resposta imediata ou consistência forte não devem ser convertidos para esse estilo. **(Livro, seção 11.6.)**

**Consequências:**

* **Positivas:** a operação municipal pode ser concluída sem depender da disponibilidade federal; tarefas podem permanecer pendentes até o processamento; falhas temporárias podem ser tratadas por novas tentativas; picos podem ser amortecidos pela fila. **(Livro, seção 11.5.)**
* **Negativas:** a atualização externa passa a ser eventualmente consistente; reentregas exigem idempotência; a fila precisa ser monitorada; tarefas não processadas após as tentativas previstas exigem tratamento operacional. **(Livro, seções 11.4 e 11.7.)**
