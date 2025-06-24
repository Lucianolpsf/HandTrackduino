from pyfirmata import Arduino, SERVO, OUTPUT
import time
import threading
import os
from dotenv import load_dotenv
import requests
load_dotenv()

PORTA = os.getenv('PORTA')

modo_automatico = False
thread_auto = None
board = None

estado_dedos = {10: None, 9: None, 8: None, 7: None, 6: None}

ANGULOS_SERVOS = {
    10: {"min": 0, "max": 120},
    9:  {"min": 0, "max": 150},
    8:  {"min": 0, "max": 150},
    7:  {"min": 0, "max": 180},
    6:  {"min": 0, "max": 180},
}


def get_arduino_port():
    try:
        resp = requests.get("http://localhost:5000/get_arduino_port")
        return resp.json().get("port")
    except Exception:
        return None


def conectar_arduino():
    global board
    if board is None:
        porta = get_arduino_port()
        if not porta:
            raise Exception("Porta do Arduino não selecionada!")
        board = Arduino(porta)
        for pin in [10, 9, 8, 7, 6]:
            board.digital[pin].mode = SERVO


def rotateServo(pino, angle):
    board.digital[pino].write(angle)
    time.sleep(0.02)


def abrir_fechar(pin, on_off):
    conectar_arduino()
    if estado_dedos.get(pin) != on_off:
        angulo = ANGULOS_SERVOS[pin]["min"] if on_off == 1 else ANGULOS_SERVOS[pin]["max"]
        rotateServo(pin, angulo)
        estado_dedos[pin] = on_off


def liberar_servos():
    mover_dedos_gradualmente({10: 1, 9: 0, 8: 0, 7: 1, 6: 1})


def _executar_rotina():
    global modo_automatico

    gestos = [
        {"nome": "paz", "dedos": {10: 1, 9: 1, 8: 1, 7: 1, 6: 1}},      # ✌️
        {"nome": "rock", "dedos": {10: 0, 9: 1, 8: 0, 7: 1, 6: 0}},     # 🤘
        {"nome": "aberta", "dedos": {10: 0, 9: 1, 8: 1, 7: 0, 6: 0}},   # 🖐️
        {"nome": "hang", "dedos": {10: 0, 9: 0, 8: 0, 7: 1, 6: 0}},     # 🤙
        {"nome": "fechada", "dedos": {10: 1, 9: 0, 8: 0, 7: 1, 6: 1}},  # ✊
        {"nome": "tchau", "dedos": {10: 0, 9: 1, 8: 1, 7: 0, 6: 0}},    # 👋
        {"nome": "aponta", "dedos": {10: 1, 9: 1, 8: 0, 7: 1, 6: 1}},   # 👉
    ]
    indice = 0

    while modo_automatico:
        gesto = gestos[indice]
        print(f"[AUTOMÁTICO] Executando gesto: {gesto['nome']}")

        mover_dedos_gradualmente(gesto["dedos"], passos=20, delay=0.02)

        if gesto["nome"] == "tchau":
            for _ in range(4):
                if not modo_automatico:
                    break
                mover_dedos_gradualmente({9: 0, 8: 0, 7: 1, 6: 1}, passos=10, delay=0.04)
                mover_dedos_gradualmente({9: 1, 8: 1, 7: 0, 6: 0}, passos=10, delay=0.04)

        indice = (indice + 1) % len(gestos)
        for _ in range(5):
            if not modo_automatico:
                break
            time.sleep(1)


def rotina_automatica(on=False):
    global modo_automatico, thread_auto

    if on and not modo_automatico:
        modo_automatico = True
        thread_auto = threading.Thread(target=_executar_rotina)
        thread_auto.start()
        print("Modo automático INICIADO")

    elif not on:
        modo_automatico = False
        if thread_auto is not None:
            thread_auto.join(timeout=2)
        liberar_servos()
        print("Modo automático PARADO")


def mover_dedos_gradualmente(dedos_estado_destino, passos=20, delay=0.02):
    """
    Move todos os dedos gradualmente para o estado desejado.
    dedos_estado_destino: dict {pin: on_off}
    passos: quantidade de passos para o movimento
    delay: tempo entre cada passo
    """
    conectar_arduino()
    # Ângulos atuais
    angulos_atuais = {}
    angulos_finais = {}
    for pin, on_off in dedos_estado_destino.items():
        estado_atual = estado_dedos.get(pin)
        if estado_atual is None:
            # Se não sabemos o estado, assumimos min
            angulos_atuais[pin] = ANGULOS_SERVOS[pin]["min"]
        else:
            angulos_atuais[pin] = ANGULOS_SERVOS[pin]["min"] if estado_atual == 1 else ANGULOS_SERVOS[pin]["max"]
        angulos_finais[pin] = ANGULOS_SERVOS[pin]["min"] if on_off == 1 else ANGULOS_SERVOS[pin]["max"]

    for passo in range(1, passos + 1):
        for pin in dedos_estado_destino:
            ang_atual = angulos_atuais[pin]
            ang_final = angulos_finais[pin]
            angulo = int(ang_atual + (ang_final - ang_atual) * passo / passos)
            board.digital[pin].write(angulo)
        time.sleep(delay)

    # Atualiza estado_dedos
    for pin, on_off in dedos_estado_destino.items():
        estado_dedos[pin] = on_off

# Exemplo de uso:
# mover_dedos_gradualmente({10: 1, 9: 0, 8: 0, 7: 1, 6: 1})
