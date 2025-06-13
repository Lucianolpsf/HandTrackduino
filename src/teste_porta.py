import serial

try:
    s = serial.Serial('COM4', 9600)
    print("Porta COM4 aberta com sucesso!")
    s.close()
except serial.SerialException as e:
    print(f"Erro ao abrir COM4: {e}")
