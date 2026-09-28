

# C4 — Nível 2: Contêineres

O diagrama de contêineres apresenta as principais unidades executáveis e de armazenamento do Sistema Municipal Integrado de Saúde. A arquitetura mantém uma aplicação principal em monolito modular e utiliza serviços gerenciados apenas nas fronteiras em que há necessidade específica de persistência, mensageria ou processamento assíncrono.

```mermaid
flowchart TB

    subgraph usuarios[" "]
        direction LR
        profissionais["👤<br/><b>Profissionais da rede</b><br/><small>Realizam atendimento, regulação e dispensação</small>"]
        gestao["👤<br/><b>Gestão e vigilância</b><br/><small>Acompanham a rede e informações epidemiológicas</small>"]
        cidadao["👤<br/><b>Paciente e família</b><br/><small>Consulta informações e realiza agendamentos</small>"]
    end

    subgraph sistema["Sistema Municipal Integrado de Saúde"]
        direction TB

        subgraph camada_interfaces[" "]
            direction LR

            subgraph bloco_unidade[" "]
                direction TB
                unidade["«container»<br/><b>Aplicação da Unidade</b><br/>[Web/PWA]<br/><small>Interface operacional para UBS, UPA, hospital e farmácia</small>"]
                local[("«container»<br/><b>Armazenamento Local</b><br/>[Persistência local]<br/><small>Mantém operações pendentes durante indisponibilidade da rede</small>")]
            end

            portal["«container»<br/><b>Portal Web</b><br/>[Web]<br/><small>Acesso de cidadãos, gestão e vigilância</small>"]
        end

        backend["«container»<br/><b>Aplicação de Saúde</b><br/>[API / Monolito modular]<br/><small>Executa as capacidades de negócio da rede municipal</small>"]

        subgraph camada_dados[" "]
            direction LR

            banco[("«container»<br/><b>Banco de Dados Central</b><br/>[Banco relacional gerenciado]<br/><small>Persistência principal dos módulos de negócio</small>")]

            subgraph bloco_integracao[" "]
                direction TB
                fila["«container»<br/><b>Fila Persistente</b><br/>[Mensageria gerenciada]<br/><small>Mantém tarefas de integração que podem ser processadas posteriormente</small>"]
                integracao["«container»<br/><b>Função de Integração</b><br/>[Função gerenciada]<br/><small>Processa tarefas assíncronas destinadas aos sistemas externos</small>"]
            end
        end
    end

    subgraph externos[" "]
        direction LR
        legado["«external_system»<br/><b>Sistema legado de regulação</b><br/><small>Autoridade das capacidades de regulação ainda não migradas</small>"]
        federal["«external_system»<br/><b>Sistemas federais de saúde</b><br/><small>Enviam e recebem dados por APIs externas</small>"]
    end


    profissionais -->|"Registra operações da unidade<br/>[chamada local]"| unidade
    gestao -->|"Consulta gestão e vigilância<br/>[chamada · HTTPS]"| portal
    cidadao -->|"Acessa serviços e agendamentos<br/>[chamada · HTTPS]"| portal

    unidade -->|"Grava e consulta pendências<br/>[acesso a dados · local]"| local

    unidade -->|"Consulta, registra e sincroniza<br/>[chamada · HTTPS/JSON]"| backend
    portal -->|"Consulta e registra informações<br/>[chamada · HTTPS/JSON]"| backend

    backend -->|"Lê e grava dados dos módulos<br/>[acesso a dados · SQL/TLS]"| banco
    backend -->|"Registra tarefa de integração<br/>[fila · mensageria]"| fila

    fila -->|"Aciona processamento pendente<br/>[fila · gatilho]"| integracao

    backend -->|"Confirma e consulta capacidades ainda no legado<br/>[chamada · API]"| legado

    integracao -->|"Transmite dados pendentes<br/>[chamada · API]"| federal
    federal -->|"Envia dados para a rede municipal<br/>[chamada · API]"| backend


    style usuarios fill:none,stroke:none
    style externos fill:none,stroke:none

    style camada_interfaces fill:none,stroke:none
    style camada_dados fill:none,stroke:none
    style bloco_unidade fill:none,stroke:none
    style bloco_integracao fill:none,stroke:none

    style sistema fill:#ffffff,stroke:#444,stroke-width:2px,stroke-dasharray:6 4

    style gestao fill:#08427b,color:#fff,stroke:#073b6f

    style portal fill:#1168bd,color:#fff,stroke:#0b4884
    style unidade fill:#1168bd,color:#fff,stroke:#0b4884
    style backend fill:#1168bd,color:#fff,stroke:#0b4884

    style local fill:#438dd5,color:#fff,stroke:#0b4884
    style banco fill:#438dd5,color:#fff,stroke:#0b4884
    style fila fill:#438dd5,color:#fff,stroke:#0b4884
    style integracao fill:#438dd5,color:#fff,stroke:#0b4884

    style legado fill:#999,color:#fff,stroke:#777
    style federal fill:#999,color:#fff,stroke:#777
```

## Responsabilidades dos contêineres

**Portal Web:** oferece as funcionalidades destinadas aos cidadãos e às áreas de gestão e vigilância. Não depende do mecanismo de armazenamento offline utilizado nas unidades de atendimento.

**Aplicação da Unidade:** é utilizada pelos profissionais das UBS, UPAs, hospital e farmácia. Permite acesso às capacidades da Aplicação de Saúde e controla as operações locais que precisam sobreviver às interrupções de conectividade.

**Armazenamento Local:** mantém temporariamente operações ainda não confirmadas pelo sistema central. Não representa uma segunda fonte de verdade da rede e é utilizado somente para as capacidades autorizadas a funcionar offline.

**Aplicação de Saúde:** contém os módulos de negócio do sistema e constitui a principal unidade de implantação. Internamente segue a estrutura de monolito modular definida no ADR 0001.

**Banco de Dados Central:** mantém a persistência principal do sistema. Embora fisicamente compartilhado, os dados são logicamente separados e possuem proprietário definido por módulo, conforme o ADR 0002.

**Fila Persistente:** armazena tarefas de integração que não precisam de resposta imediata. Seu uso é localizado e não transforma toda a aplicação em uma arquitetura orientada a eventos.

**Função de Integração:** é acionada pela fila para executar trabalhos assíncronos curtos, como transmitir notificações e outros dados aos sistemas federais. A indisponibilidade do destino não mantém uma requisição da unidade de saúde bloqueada.

## Decisões evidenciadas pelo diagrama

O suporte offline existe somente entre a **Aplicação da Unidade**, o **Armazenamento Local** e a **Aplicação de Saúde**. Quando a conexão retorna, as operações pendentes são sincronizadas de forma idempotente conforme o ADR 0005.

A comunicação com o **Sistema Legado de Regulação** permanece síncrona nas capacidades que ainda dependem dele. Enquanto uma capacidade não tiver sido migrada, o legado permanece como sua única autoridade de escrita, conforme os ADRs 0002 e 0003.

As integrações externas que não exigem resposta imediata passam pela **Fila Persistente** e pela **Função de Integração**. Já dados recebidos dos sistemas federais entram pela API da Aplicação de Saúde e são tratados pelos adaptadores correspondentes.

O diagrama contém **12 elementos**, respeitando o limite de legibilidade adotado no capítulo 3 do livro.
