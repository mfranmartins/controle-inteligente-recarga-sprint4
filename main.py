
from machine import ADC, Pin
import time
import sys
import select

potenciometros = [
    ADC(Pin(26)),
    ADC(Pin(27)),
    ADC(Pin(28))
]

leds = [
    {
        "r": Pin(0, Pin.OUT),
        "g": Pin(1, Pin.OUT),
        "b": Pin(2, Pin.OUT)
    },
    {
        "r": Pin(3, Pin.OUT),
        "g": Pin(4, Pin.OUT),
        "b": Pin(5, Pin.OUT)
    },
    {
        "r": Pin(6, Pin.OUT),
        "g": Pin(7, Pin.OUT),
        "b": Pin(8, Pin.OUT)
    }
]

nomes = ["EV1", "EV2", "EV3"]
demandas = [0, 0, 0]
energia_disponivel = 5000
potencia_alocada = [0, 0, 0]
estados = ["SEM DEMANDA"] * 3

potencia_minima = 500
limite_baixa_energia = 2000

comando_buffer = ""
mensagem = "Digite os comandos no Monitor Serial."
ultimo_painel = None

poll = select.poll()
poll.register(sys.stdin, select.POLLIN)


def decimal_para_hexadecimal(numero):
    digitos = "0123456789ABCDEF"

    if numero == 0:
        return "0"

    resultado = ""

    while numero > 0:
        resto = numero % 16
        resultado = digitos[resto] + resultado
        numero //= 16

    return resultado


def desligar_led(led):
    led["r"].value(0)
    led["g"].value(0)
    led["b"].value(0)


def definir_cor(led, estado):
    desligar_led(led)

    if estado == "RECARGA TOTAL":
        led["g"].value(1)

    elif estado == "RECARGA REDUZIDA":
        led["r"].value(1)
        led["g"].value(1)

    elif estado in ("EM ESPERA", "RECARGA BLOQUEADA"):
        led["r"].value(1)


def processar_comando(comando):
    global energia_disponivel, mensagem

    comando = comando.strip().upper()

    try:
        if comando.startswith("ENERGIA"):
            valor = int(comando[7:])

            if 0 <= valor <= 10000 and valor % 250 == 0:
                energia_disponivel = valor
                mensagem = "Energia disponivel atualizada."
            else:
                mensagem = "Energia invalida: use 0 a 10000 W, em passos de 250 W."

        elif (
            len(comando) >= 4
            and comando[0] in "123"
            and comando[1:3] == "EV"
        ):
            indice = int(comando[0]) - 1
            valor = int(comando[3:])

            if 0 <= valor <= 10000 and valor % 250 == 0:
                demandas[indice] = valor
                mensagem = "Demanda do " + nomes[indice] + " atualizada."
            else:
                mensagem = "Demanda invalida: use 0 a 10000 W, em passos de 250 W."

        else:
            mensagem = "Comando invalido. Use 1EV3000 ou ENERGIA5000."

    except ValueError:
        mensagem = "Formato invalido. Exemplo: 1EV3000."


def ler_serial():
    global comando_buffer

    while poll.poll(0):
        caractere = sys.stdin.read(1)

        if not caractere:
            break

        if caractere == "\r" or caractere == "\n":
            if comando_buffer:
                processar_comando(comando_buffer)
                comando_buffer = ""
        else:
            comando_buffer += caractere


def ler_baterias():
    baterias = []

    for potenciometro in potenciometros:
        leitura = potenciometro.read_u16()
        bateria = round(leitura * 100 / 65535)
        baterias.append(bateria)

    return baterias


def distribuir_energia(baterias):
    alocacoes = [0, 0, 0]
    novos_estados = ["SEM DEMANDA"] * 3

    fila = [
        i for i in range(3)
        if demandas[i] > 0
    ]

    fila.sort(key=lambda i: (baterias[i], demandas[i]))

    if energia_disponivel < limite_baixa_energia:
        if fila:
            indice = fila[0]
            alocacao = min(demandas[indice], energia_disponivel)

            if alocacao >= potencia_minima:
                alocacoes[indice] = alocacao

                if alocacao == demandas[indice]:
                    novos_estados[indice] = "RECARGA TOTAL"
                else:
                    novos_estados[indice] = "RECARGA REDUZIDA"

            else:
                novos_estados[indice] = "EM ESPERA"

        for indice in fila[1:]:
            novos_estados[indice] = "EM ESPERA"

    else:
        restante = energia_disponivel

        for indice in fila:
            alocacao = min(demandas[indice], restante)

            if alocacao >= potencia_minima:
                alocacoes[indice] = alocacao
                restante -= alocacao

                if alocacao == demandas[indice]:
                    novos_estados[indice] = "RECARGA TOTAL"
                else:
                    novos_estados[indice] = "RECARGA REDUZIDA"
            else:
                novos_estados[indice] = "EM ESPERA"

    for i in range(3):
        if novos_estados[i] == "SEM DEMANDA":
            definir_cor(leds[i], "SEM DEMANDA")
        else:
            definir_cor(leds[i], novos_estados[i])

    return alocacoes, novos_estados


def exibir_painel(baterias, alocacoes, novos_estados):
    global ultimo_painel

    painel = (
        tuple(baterias),
        tuple(demandas),
        energia_disponivel,
        tuple(alocacoes),
        tuple(novos_estados),
        mensagem
    )

    if painel == ultimo_painel:
        return

    ultimo_painel = painel

    print("\033[2J\033[H")
    print("====== GOODWE SMART CHARGING STATION ======")
    print("Energia disponivel:", energia_disponivel, "W")
    print(
        "Decimal:", energia_disponivel,
        "| Binario:", bin(energia_disponivel)[2:],
        "| Hex:", decimal_para_hexadecimal(energia_disponivel)
    )
    print()

    for i in range(3):
        print(
            nomes[i],
            "| Bateria:", str(baterias[i]) + "%",
            "| Demanda:", demandas[i], "W"
        )
        print(
            "Potencia alocada:", alocacoes[i],
            "W | Estado:", novos_estados[i]
        )

    print()
    print("Mensagem:", mensagem)



while True:
    baterias = ler_baterias()

    ler_serial()

    for i in range(3):
        if baterias[i] >= 100 and demandas[i] > 0:
            demandas[i] = 0
            mensagem = nomes[i] + " com bateria em 100%: demanda zerada."

    potencia_alocada, estados = distribuir_energia(baterias)

    exibir_painel(baterias, potencia_alocada, estados)

    time.sleep(0.1)
