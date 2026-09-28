"""Spike do ADR 0005: sincronização offline idempotente.

O exemplo mostra uma UPA que registra uma triagem sem internet.
Quando a conexão volta, o servidor processa a operação, mas a primeira
confirmação se perde. A UPA envia a mesma operação novamente e o
servidor não cria um segundo atendimento.
"""


def registrar_offline(pendentes):
    """Cria uma operação local enquanto a unidade está sem internet."""

    operacao = {
        "chave": "UPA-01-OP-0001",
        "paciente": "PAC-123",
        "tipo": "triagem",
    }

    pendentes[operacao["chave"]] = operacao

    print(
        f"OFFLINE: operação {operacao['chave']} "
        "salva localmente"
    )


def processar_no_servidor(operacao, banco):
    """Aplica a operação uma única vez usando a chave de idempotência."""

    chave = operacao["chave"]

    # Se a chave já foi processada, o servidor não repete o efeito.
    if chave in banco["processadas"]:
        atendimento_id = banco["processadas"][chave]
        return atendimento_id, True

    atendimento_id = f"ATD-{len(banco['atendimentos']) + 1:03d}"

    banco["atendimentos"].append(
        {
            "id": atendimento_id,
            "paciente": operacao["paciente"],
            "tipo": operacao["tipo"],
        }
    )

    # Em produção, o atendimento e a chave deveriam ser gravados na mesma transação do banco.
    banco["processadas"][chave] = atendimento_id

    return atendimento_id, False


def enviar(operacao, banco, rede):
    """Simula o envio ao servidor e a perda da primeira confirmação."""

    atendimento_id, repetida = processar_no_servidor(operacao, banco)

    # O servidor já processou, mas a resposta não chega à unidade.
    if rede["perder_primeira_confirmacao"]:
        rede["perder_primeira_confirmacao"] = False
        print(
            "REDE: servidor processou a operação, "
            "mas a resposta não chegou à unidade"
        )
        return None

    return atendimento_id, repetida


def sincronizar(pendentes, banco, rede):
    """Tenta enviar as operações que ficaram pendentes localmente."""

    for chave in list(pendentes):
        operacao = pendentes[chave]

        for tentativa in range(1, 3):
            print(f"SYNC: tentativa {tentativa} para {chave}")

            resposta = enviar(operacao, banco, rede)

            if resposta is None:
                # Sem confirmação, a operação continua pendente.
                continue

            atendimento_id, repetida = resposta

            if repetida:
                print(
                    "SERVIDOR: chave já processada; "
                    "reutilizando resultado anterior"
                )
            else:
                print("SERVIDOR: operação aplicada pela primeira vez")

            print(
                f"SYNC: confirmação recebida ({atendimento_id})"
            )

            # Só remove do armazenamento local após receber confirmação.
            del pendentes[chave]
            break


def mostrar_resumo(pendentes, banco):
    """Mostra as provas."""

    quantidade_atendimentos = len(banco["atendimentos"])
    quantidade_processadas = len(banco["processadas"])
    quantidade_pendentes = len(pendentes)

    passou = (
        quantidade_atendimentos == 1
        and quantidade_processadas == 1
        and quantidade_pendentes == 0
    )

    print("\nRESUMO")
    print(
        "atendimentos no banco central: "
        f"{quantidade_atendimentos}"
    )
    print(
        "chaves de idempotência processadas: "
        f"{quantidade_processadas}"
    )
    print(
        "operações locais pendentes: "
        f"{quantidade_pendentes}"
    )
    print(f"RESULTADO: {'PASSOU' if passou else 'FALHOU'}")

    return passou


def main():
    # Armazenamento local da unidade.
    pendentes = {}

    # Banco central simulado.
    banco = {
        "atendimentos": [],
        "processadas": {},
    }

    # Rede simulada: perde somente a primeira confirmação.
    rede = {
        "perder_primeira_confirmacao": True,
    }

    registrar_offline(pendentes)

    print("REDE: conexão restabelecida")
    sincronizar(pendentes, banco, rede)

    if not mostrar_resumo(pendentes, banco):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
