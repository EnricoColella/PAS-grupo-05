
# C4 — Nível 1: Contexto

O diagrama de contexto apresenta o **Sistema Municipal Integrado de Saúde** como uma única caixa e mostra os principais grupos de usuários e sistemas externos com os quais ele se comunica.

```mermaid
flowchart TB

    subgraph usuarios[" "]
        direction LR
        cidadao["👤<br/><b>Paciente e família</b><br/><small>Consulta informações e realiza agendamentos</small>"]
        profissionais["👤<br/><b>Profissionais da rede</b><br/><small>Realizam atendimento, regulação e dispensação</small>"]
        gestao["👤<br/><b>Gestão e vigilância</b><br/><small>Acompanham a rede e informações epidemiológicas</small>"]
    end

    sistema["«system»<br/><b>Sistema Municipal Integrado de Saúde</b><br/>Integra as capacidades da rede municipal de saúde"]

    subgraph externos[" "]
        direction LR
        legado["«external_system»<br/><b>Sistema legado de regulação</b><br/><small>Mantém as capacidades de regulação ainda não migradas</small>"]
        federal["«external_system»<br/><b>Sistemas federais de saúde</b><br/><small>Trocam dados de saúde com a rede municipal</small>"]
    end

    cidadao -->|"Consulta informações e realiza agendamentos<br/>[HTTPS]"| sistema

    profissionais -->|"Consulta e registra informações assistenciais<br/>[HTTPS]"| sistema

    gestao -->|"Consulta informações de gestão e vigilância<br/>[HTTPS]"| sistema

    sistema -->|"Consulta e confirma operações de capacidades ainda não migradas<br/>[API]"| legado

    sistema -->|"Envia e recebe dados de saúde<br/>[API]"| federal

    style usuarios fill:none,stroke:none
    style externos fill:none,stroke:none

    style cidadao fill:#08427b,color:#fff,stroke:#073b6f
    style profissionais fill:#08427b,color:#fff,stroke:#073b6f
    style gestao fill:#08427b,color:#fff,stroke:#073b6f

    style sistema fill:#1168bd,color:#fff,stroke:#0b4884

    style legado fill:#999,color:#fff,stroke:#777
    style federal fill:#999,color:#fff,stroke:#777
```

## Relações principais

**Paciente e família:** utilizam o sistema para consultar informações disponíveis ao cidadão e realizar agendamentos.

**Profissionais da rede:** utilizam o sistema durante atendimento, registro clínico, regulação de leitos, dispensação de medicamentos e demais atividades assistenciais.

**Gestão e vigilância:** utilizam as informações consolidadas da rede para acompanhamento da operação e das atividades de vigilância epidemiológica.

**Sistema legado de regulação:** permanece externo ao novo sistema durante o processo de migração. Enquanto uma capacidade ainda não tiver sido migrada, as operações correspondentes continuam dependendo do legado como autoridade.

**Sistemas federais de saúde:** recebem e fornecem dados por integrações externas. Sua eventual indisponibilidade não deve impedir a continuidade das operações locais que não dependem de resposta imediata desses sistemas.

## Escopo representado

Neste nível, detalhes internos como Portal Web, Aplicação da Unidade, banco de dados, fila e módulos de negócio não aparecem. Esses elementos pertencem aos níveis de contêineres e componentes.

O objetivo deste diagrama é mostrar apenas:

- quem utiliza o Sistema Municipal Integrado de Saúde;
- quais sistemas externos participam de seus fluxos;
- quais informações ou operações atravessam essas fronteiras.
