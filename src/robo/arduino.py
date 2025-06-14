import cv2
import mediapipe as mp
from . import servo_braco3d as mao
import os
from dotenv import load_dotenv
load_dotenv()

CAMERA = os.getenv('CAMERA')

hands = mp.solutions.hands
Hands = hands.Hands(max_num_hands=1)
mpDwaw = mp.solutions.drawing_utils

def gen_arduino_frames():
    cap = cv2.VideoCapture(int(CAMERA))
    cap.set(3, 1280)
    cap.set(4, 720)
    try:
        while True:
            success, img = cap.read()
            if not success or img is None:
                print("Erro: Não foi possível capturar a imagem da câmera!")
                continue
            frameRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
            results = Hands.process(frameRGB)
            handPoints = results.multi_hand_landmarks
            h, w, _ = img.shape
            pontos = []
            if handPoints:
                for points in handPoints:
                    mpDwaw.draw_landmarks(img, points,hands.HAND_CONNECTIONS)
                    for id, cord in enumerate(points.landmark):
                        cx, cy = int(cord.x * w), int(cord.y * h)
                        cv2.circle(img,(cx,cy),4,(255,0,0),-1)
                        pontos.append((cx,cy))

                    if pontos:
                        distPolegar = abs(pontos[17][0] - pontos[4][0])
                        distIndicador = pontos[5][1] - pontos[8][1]
                        distMedio = pontos[9][1] - pontos[12][1]
                        distAnelar = pontos[13][1] - pontos[16][1]
                        distMinimo = pontos[17][1] - pontos[20][1]

                        if distPolegar <80:
                            mao.abrir_fechar(10,0)
                        else:
                            mao.abrir_fechar(10,1)

                        if distIndicador >=1:
                            mao.abrir_fechar(9,1)
                        else:
                            mao.abrir_fechar(9,0)

                        if distMedio >=1:
                            mao.abrir_fechar(8,1)
                        else:
                            mao.abrir_fechar(8,0)

                        if distAnelar >=1:
                            mao.abrir_fechar(7,0)
                        else:
                            mao.abrir_fechar(7,1)

                        if distMinimo >=1:
                            mao.abrir_fechar(6,0)
                        else:
                            mao.abrir_fechar(6,1)

            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    finally:
        cap.release()
