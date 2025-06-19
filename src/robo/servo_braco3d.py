from pyfirmata import Arduino, SERVO
import time
import threading
import os
from dotenv import load_dotenv
load_dotenv()

PORTA = os.getenv('PORTA')

modo_automatico = False
thread_auto = None
board = None  # Inicialmente não conectado

# Estado atual dos dedos para evitar comandos repetidos
estado_dedos = {10: None, 9: None, 8: None, 7: None, 6: None}

def conectar_arduino():
    global board
    if board is None:
        board = Arduino(PORTA)
        for pin in [10, 9, 8, 7, 6]:
            board.digital[pin].mode = SERVO

def rotateServo(pino, angle):
    board.digital[pino].write(angle)
    time.sleep(0.015)

def abrir_fechar(pin, on_off):
    conectar_arduino()
    # Só envia comando se mudou o estado
    if estado_dedos.get(pin) != on_off:
        # Ajuste os ângulos conforme seu hardware para evitar forçar!
        if on_off == 1:
            # Abrir
            if pin == 8:
                rotateServo(pin, 0)
            else:
                rotateServo(pin, 0)
        elif on_off == 0:
            # Fechar
            if pin == 8:
                rotateServo(pin, 180)  # Ajuste se necessário
            elif pin == 10:
                rotateServo(pin, 120)  # Ajuste se necessário
            elif pin == 9:
                rotateServo(pin, 120)  # Ajuste se necessário
            else:
                rotateServo(pin, 120)  # Ajuste se necessário
        estado_dedos[pin] = on_off

def liberar_servos():
    # Todos abertos (posição de descanso)
    abrir_fechar(10, 1)
    abrir_fechar(9, 0)
    abrir_fechar(8, 0)
    abrir_fechar(7, 1)
    abrir_fechar(6, 1)


def _executar_rotina():
    global modo_automatico

    gestos = [
        {"nome": "rock", "dedos": {10: 1, 9: 1, 8: 0, 7: 1, 6: 0}},     # 🤘
        {"nome": "paz", "dedos": {10: 0, 9: 1, 8: 1, 7: 1, 6: 1}},      # ✌️
        {"nome": "hang", "dedos": {10: 1, 9: 0, 8: 0, 7: 1, 6: 0}},     # 🤙
        {"nome": "fechada", "dedos": {10: 0, 9: 0, 8: 0, 7: 1, 6: 1}},  # ✊
        {"nome": "aberta", "dedos": {10: 1, 9: 1, 8: 1, 7: 0, 6: 0}},   # 🖐️
        {"nome": "tchau", "dedos": {10: 1, 9: 1, 8: 1, 7: 0, 6: 0}},    # 👋
        {"nome": "aponta", "dedos": {10: 0, 9: 1, 8: 0, 7: 1, 6: 1}},   # 👉
    ]
    indice = 0

    while modo_automatico:
        gesto = gestos[indice]
        print(f"[AUTOMÁTICO] Executando gesto: {gesto['nome']}")

        for pin, estado in gesto["dedos"].items():
            print(f"[AUTOMÁTICO] Pino {pin} {'ABRINDO' if estado else 'FECHANDO'}")
            abrir_fechar(pin, estado)

        if gesto["nome"] == "tchau":
            for _ in range(4):
                if not modo_automatico: break
                abrir_fechar(9, 0)
                abrir_fechar(8, 0)
                abrir_fechar(7, 1)
                abrir_fechar(6, 1)
                time.sleep(0.4)
                abrir_fechar(9, 1)
                abrir_fechar(8, 1)
                abrir_fechar(7, 0)
                abrir_fechar(6, 0)
                time.sleep(0.4)

        indice = (indice + 1) % len(gestos)
        for _ in range(5):
            if not modo_automatico: break
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
