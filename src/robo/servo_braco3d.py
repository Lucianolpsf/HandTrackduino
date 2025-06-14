from pyfirmata import Arduino,SERVO
import time
import os
from dotenv import load_dotenv
load_dotenv()

PORTA = os.getenv('PORTA')

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
    elif on_off==0 and pin!=10 and pin!=9:
        rotateServo(pin, 140)
    elif on_off == 0 and pin == 10:
        rotateServo(pin, 150)
    elif on_off == 0 and pin == 9:
        rotateServo(pin, 180)


