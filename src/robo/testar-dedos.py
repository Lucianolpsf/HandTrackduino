from pyfirmata import Arduino, SERVO
import time
import os

from dotenv import load_dotenv
load_dotenv()

PORTA = os.getenv('PORTA')
board = Arduino(PORTA)

pins = {
    "dedao": 10,
    "indicador": 9,
    "medio": 8,
    "anelar": 7,
    "minimo": 6
}

for pin in pins.values():
    board.digital[pin].mode = SERVO

for pin in pins.values():
    if pin == 7 or pin == 6:
        board.digital[pin].write(150)
        time.sleep(0.02)
    else:
        board.digital[pin].write(0)
        time.sleep(0.02)


def rotateServo(pino, angle):
    board.digital[pino].write(angle)
    time.sleep(0.02)

def testar_dedo(nome, pin):
    print(f"\nTestando {nome} (pino {pin})")
    min_angle = int(input("Digite o ângulo MÍNIMO (aberto): "))
    max_angle = int(input("Digite o ângulo MÁXIMO (fechado): "))
    print("Movendo para o ângulo mínimo...")
    rotateServo(pin, min_angle)
    time.sleep(5)
    print("Movendo para o ângulo máximo...")
    rotateServo(pin, max_angle)
    time.sleep(5)
    print("Voltando para o ângulo mínimo...")
    rotateServo(pin, min_angle)
    time.sleep(5)
    print(f"Teste do {nome} concluído. Anote os ângulos que não fazem barulho ou forçam o servo.")

if __name__ == "__main__":
    print("=== Teste Interativo dos Dedos ===")
    for nome, pin in pins.items():
        testar_dedo(nome, pin)
    print("\nTeste finalizado! Ajuste os ângulos no seu código principal conforme os melhores valores encontrados.")