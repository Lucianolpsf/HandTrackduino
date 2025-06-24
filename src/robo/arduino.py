from services.cameras.camera_manager import CameraManager
import cv2
import time
import mediapipe as mp

from services.cameras.utils import add_watermark
from . import servo_braco3d as mao

hands = mp.solutions.hands
Hands = hands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils


def mao_aberta():
    # Posição de descanso (ajuste conforme necessário)
    mao.abrir_fechar(10, 0)
    mao.abrir_fechar(9, 1)
    mao.abrir_fechar(8, 1)
    mao.abrir_fechar(7, 0)
    mao.abrir_fechar(6, 0)

def gen_arduino_frames():
    last_detected_time = time.time()
    in_rest_position = False
    cam = CameraManager.get_instance()

    while True:
        current_time = time.time()
        img = cam.get_frame()
        if img is None:
            continue
        frameRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = Hands.process(frameRGB)
        handPoints = results.multi_hand_landmarks
        h, w, _ = img.shape
        pontos = []
        if handPoints:
            last_detected_time = current_time
            if in_rest_position:
                print("Mão detectada novamente, saindo da posição de descanso.")
                in_rest_position = False
            for points in handPoints:
                mpDraw.draw_landmarks(img, points, hands.HAND_CONNECTIONS)
                for id, cord in enumerate(points.landmark):
                    cx, cy = int(cord.x * w), int(cord.y * h)
                    cv2.circle(img, (cx, cy), 4, (255, 0, 0), -1)
                    pontos.append((cx, cy))

                if pontos:
                    distPolegar = abs(pontos[17][0] - pontos[4][0])
                    distIndicador = pontos[5][1] - pontos[8][1]
                    distMedio = pontos[9][1] - pontos[12][1]
                    distAnelar = pontos[13][1] - pontos[16][1]
                    distMinimo = pontos[17][1] - pontos[20][1]

                    gesto_sinal_proibido = (
                        distMedio >= 1 and 
                        distIndicador < 5 and 
                        distAnelar < 5 and 
                        distMinimo < 1 and 
                        distPolegar >= 1
                    )
                    if gesto_sinal_proibido:
                        x, y, w_box, h_box = 30, 30, 400, 70
                        cv2.rectangle(img, (x, y), (x + w_box, y + h_box), (0, 0, 255), -1)
                        cv2.putText(img, 'SINAL PROIBIDO!', (x + 10, y + 50),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)
                        mao_aberta()
                    else:
                        # Ajuste os thresholds conforme necessário para seu projeto
                        mao.abrir_fechar(10, 1 if distPolegar < 50 else 0)
                        mao.abrir_fechar(9, 1 if distIndicador >= 1 else 0)
                        mao.abrir_fechar(8, 1 if distMedio >= 1 else 0)
                        mao.abrir_fechar(7, 0 if distAnelar >= 1 else 1)
                        mao.abrir_fechar(6, 0 if distMinimo >= 1 else 1)

        # Verifica inatividade
        if current_time - last_detected_time > 5:
            if not in_rest_position:
                print("Nenhuma mão detectada por 5 segundos. Voltando para a posição padrão.")
                mao_aberta()
                in_rest_position = True

        # Overlay de status
        overlay = img.copy()

        if current_time - last_detected_time > 5:
            texto = "Mao em Descanso"
            cor = (0, 0, 255)
            posicao = (10, 30)
        else:
            texto = "Mao Detectada"
            cor = (0, 255, 0)
            posicao = (10, 30)
        cv2.rectangle(overlay, (posicao[0]-10, posicao[1]-30), (posicao[0]+300, posicao[1]+10), (0,0,0), -1)
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        cv2.putText(img, texto, posicao, cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)
        
        img = add_watermark(img)
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
