from pyfirmata import Arduino,SERVO
import time
import threading
import os
from dotenv import load_dotenv
load_dotenv()

PORTA = os.getenv('PORTA')

modo_automatico = False
thread_auto = None
board = None  # Inicialmente não conectado

def conectar_arduino():
    global board
    if board is None:
        from pyfirmata import Arduino
        board = Arduino(PORTA)
        # Faça outras configurações necessárias aqui

        pin1 = 10
        pin2 = 9
        pin3 = 8
        pin4 = 7
        pin5 = 6

        board.digital[pin1].mode = SERVO
        board.digital[pin2].mode = SERVO
        board.digital[pin3].mode = SERVO
        board.digital[pin4].mode = SERVO
        board.digital[pin5].mode = SERVO

def rotateServo(pino,angle):
    board.digital[pino].write(angle)
    time.sleep(0.015)


def abrir_fechar(pin,on_off):
    conectar_arduino()  # Certifique-se de que o Arduino está conectado antes de operar os pinos
    if on_off==1:
        rotateServo(pin, 0)
    elif on_off==0 and pin == 8:
        rotateServo(pin, 250)
    elif on_off==0 and pin!=10 and pin!=9:
        rotateServo(pin, 140)
    elif on_off == 0 and pin == 10:
        rotateServo(pin, 150)
    elif on_off == 0 and pin == 9:
        rotateServo(pin, 180)


def liberar_servos():
    # Defina aqui a posição neutra ou de descanso dos servos
    # Por exemplo, todos abertos:
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
        {"nome": "aberta", "dedos": {10: 1, 9: 1, 8: 1, 7: 0, 6: 0}},  # ✊
        {"nome": "tchau", "dedos": {10: 1, 9: 1, 8: 1, 7: 0, 6: 0}},    # 👋
        {"nome": "aponta", "dedos": {10: 0, 9: 1, 8: 0, 7: 1, 6: 1}},  # ✊
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
                # abrir_fechar(10, 1)
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
        for _ in range(10):
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
            thread_auto.join(timeout=2)  # Aguarda a thread terminar (com timeout)
        liberar_servos()  # Libera os servos para o modo manual
        print("Modo automático PARADO")