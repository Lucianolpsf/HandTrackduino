import cv2
import os
from cvzone.HandTrackingModule import HandDetector
from dotenv import load_dotenv
load_dotenv()

CAMERA = os.getenv('CAMERA')
video = cv2.VideoCapture(CAMERA)
video.set(3, 1280)
video.set(4, 720)

detector = HandDetector()
desenho = []

def gen_frames():
    global desenho
    while True:
        success, img = video.read()
        if not success or img is None:
            print("Erro: Não foi possível capturar a imagem da câmera!")
            continue

        resultado = detector.findHands(img, draw=True)
        hands = resultado[0]

        if hands:
            lmlist = hands[0]['lmList']
            dedos = detector.fingersUp(hands[0])
            dedosLev = dedos.count(1)

            if dedosLev == 1:
                x, y = lmlist[8][0], lmlist[8][1]
                cv2.circle(img, (x, y), 15, (0, 0, 255), cv2.FILLED)
                desenho.append((x, y))
            elif dedosLev != 1 and dedosLev != 3:
                desenho.append((0, 0))
            elif dedosLev == 3:
                desenho = []

            for id, ponto in enumerate(desenho):
                x, y = ponto
                cv2.circle(img, (x, y), 10, (0, 0, 255), cv2.FILLED)
                if id >= 1:
                    ax, ay = desenho[id-1]
                    if x != 0 and ax != 0:
                        cv2.line(img, (x, y), (ax, ay), (0, 0, 255), 20)

        img = cv2.flip(img, 1)
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')